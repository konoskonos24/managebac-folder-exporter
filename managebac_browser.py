import re
import time
import random
import requests
from bs4 import BeautifulSoup

# Folder URLs look like:
# /student/classes/<class_id>/files/folder/<folder_id>
FOLDER_RE = re.compile(r"/student/classes/(?P<class_id>\d+)/files/folder/(?P<folder_id>\d+)", re.IGNORECASE)

# Very soft file hints (we still let downloader skip HTML)
FILE_HINT_RE = re.compile(r"(download|attachment|uploads|file|document|resource)", re.IGNORECASE)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ManageBacFolderScanner/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

BAD_URL_PARTS = (
    '/student/profile',
    '/student/classes',
    '/login',
    '/logout',
)

def _abs(school_code, href):
    if href.startswith('/'):
        return f'https://{school_code}.managebac.com{href}'
    if href.startswith('http'):
        return href
    return f'https://{school_code}.managebac.com/{href.lstrip("/")}'


def fetch(url, jar, retries=6, base_sleep=0.6):
    """
    Fetch HTML reliably. Retries with backoff on 429 and transient errors.
    """
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, cookies=jar, headers=HEADERS, allow_redirects=True, timeout=30)
            last = r
            if r.status_code == 429:
                time.sleep((base_sleep * (2 ** attempt)) + random.random())
                continue
            return r
        except requests.RequestException:
            time.sleep((base_sleep * (2 ** attempt)) + random.random())
    return last


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


# -------------------------
# 1) Get classes
# -------------------------
def get_classes(school_code, jar):
    """
    Returns: [{'name': ..., 'id': ...}, ...]
    """
    r = fetch(f'https://{school_code}.managebac.com/student', jar)
    if r is None or r.status_code >= 400:
        return []

    soup = BeautifulSoup(r.text, 'lxml')
    classes_html = soup.select('#menu > ul > li[data-path^="classes"] > ul > li')

    classes = []
    for li in classes_html:
        span = li.find('span')
        a = li.find('a', href=True)
        if not span or not a:
            continue
        cid = a['href'].split('/')[-1]
        if not cid.isdigit():
            continue
        classes.append({'name': span.get_text(strip=True), 'id': cid})
    return classes


# -------------------------
# 2) Folder discovery
# -------------------------
def extract_folders_from_html(school_code, html):
    """
    Returns dict {folder_id: {'id':..., 'name':..., 'url':...}, ...}
    """
    out = {}
    soup = BeautifulSoup(html, 'lxml')

    for a in soup.find_all('a', href=True):
        href = (a.get('href') or '').strip()
        if not href:
            continue

        href_abs = _abs(school_code, href)
        m = FOLDER_RE.search(href_abs)
        if not m:
            continue

        folder_id = m.group('folder_id')
        name = a.get_text(" ", strip=True) or a.get('title') or f'folder_{folder_id}'
        name = " ".join(name.split())

        out[folder_id] = {"id": folder_id, "name": name, "url": href_abs}

    return out


def discover_folders(school_code, jar, class_id, start_folder_id=None, passes=1, max_pages=500):
    """
    Discover folders by crawling folder pages (BFS). Multiple passes can fill gaps if some
    requests were rate-limited/blocked.
    Returns: (folders_list, stats)
    """
    if start_folder_id:
        start_url = f'https://{school_code}.managebac.com/student/classes/{class_id}/files/folder/{str(start_folder_id).strip()}'
    else:
        start_url = f'https://{school_code}.managebac.com/student/classes/{class_id}/files'

    discovered = {}          # folder_id -> info
    stats = {"fetched": 0, "blocked": 0, "rate_limited": 0}

    for p in range(int(passes)):
        to_visit = [start_url] + [info["url"] for info in discovered.values()]
        visited_urls = set()

        while to_visit and stats["fetched"] < max_pages:
            url = to_visit.pop(0)
            if url in visited_urls:
                continue
            visited_urls.add(url)

            r = fetch(url, jar)
            stats["fetched"] += 1

            if r is None:
                stats["blocked"] += 1
                continue
            if r.status_code in (404, 422):
                stats["blocked"] += 1
                continue
            if r.status_code == 429:
                stats["rate_limited"] += 1
                continue

            found = extract_folders_from_html(school_code, r.text)
            for fid, info in found.items():
                if fid not in discovered:
                    discovered[fid] = info
                    to_visit.append(info["url"])

            time.sleep(0.12)

    return list(discovered.values()), stats


# -------------------------
# 3) File discovery for downloading
# -------------------------
def extract_candidate_file_links(school_code, html, directory_prefix=""):
    """
    Soft extraction of likely file links from a page.
    We do NOT guarantee they are real files; downloader should skip HTML.
    """
    soup = BeautifulSoup(html, 'lxml')
    out = []

    for a in soup.find_all('a', href=True):
        href = (a.get('href') or '').strip()
        if not href:
            continue

        if href.startswith('#') or href.lower().startswith('javascript:') or href.lower().startswith('mailto:'):
            continue

        href_abs = _abs(school_code, href)
        low = href_abs.lower()

        # skip obvious non-file pages
        if any(part in low for part in BAD_URL_PARTS):
            continue

        # skip folder links here
        if FOLDER_RE.search(href_abs):
            continue

        text = a.get_text(" ", strip=True) or a.get('title') or 'file'
        text = " ".join(text.split())
        if len(text) > 180:
            text = text[:180]

        # Very light filter: keep if URL looks like it might be a file/link
        if (FILE_HINT_RE.search(href_abs) is None) and ('.' not in text):
            # allow it through anyway? -> no, keep it mild but not everything
            continue

        out.append({
            "type": "file",
            "name": directory_prefix + text,
            "author": "",
            "date": "",
            "url": href_abs
        })

    return out


def get_files(school_code, jar, class_dict, folder_id=None):
    """
    Returns list of file dicts: [{'name':..., 'url':...}, ...]
    Strategy:
      - discover folders (1 pass) starting from class root or folder-id
      - fetch each folder page once
      - extract candidate file links from each page
    """
    class_id = class_dict["id"]

    # 1) Discover folders first (bounded)
    folders, stats = discover_folders(
        school_code,
        jar,
        class_id=class_id,
        start_folder_id=folder_id,
        passes=1,
        max_pages=300
    )

    # Always include the start page too (it may contain direct file links)
    if folder_id:
        start_pages = [f'https://{school_code}.managebac.com/student/classes/{class_id}/files/folder/{str(folder_id).strip()}']
    else:
        start_pages = [f'https://{school_code}.managebac.com/student/classes/{class_id}/files']

    # 2) Build pages to fetch: start page + each folder url
    pages_to_fetch = start_pages + [f["url"] for f in folders]

    files = []
    seen_urls = set()

    for url in pages_to_fetch:
        r = fetch(url, jar)
        if r is None or r.status_code in (404, 422) or r.status_code == 429:
            continue
        if r.status_code >= 400:
            continue

        # Directory prefix: if this url is a folder url, use its name
        prefix = ""
        m = FOLDER_RE.search(url)
        if m:
            fid = m.group("folder_id")
            name = next((x["name"] for x in folders if x["id"] == fid), f"folder_{fid}")
            prefix = get_valid_filename(name) + "/"

        found_files = extract_candidate_file_links(school_code, r.text, directory_prefix=prefix)
        for f in found_files:
            if f["url"] in seen_urls:
                continue
            seen_urls.add(f["url"])
            files.append(f)

        time.sleep(0.10)

    return files
