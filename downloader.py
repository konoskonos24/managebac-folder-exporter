import os
import shutil
import time
import requests
from tqdm import tqdm

def download(files, dir='.', cookies=None, delay=0.25, retries=3):
    os.makedirs(dir, exist_ok=True)

    for file in tqdm(files, desc='Downloading ' + dir, total=len(files)):
        filename = os.path.join(dir, file['name'])
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        url = file['url']

        for attempt in range(retries):
            try:
                with requests.get(url, stream=True, cookies=cookies, allow_redirects=True) as r:
                    # basic rate-limit handling
                    if r.status_code == 429:
                        time.sleep(2 * (attempt + 1))
                        continue

                    r.raise_for_status()

                    # skip HTML pages (not real files)
                    ctype = (r.headers.get('Content-Type') or '').lower()
                    if 'text/html' in ctype:
                        break

                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)

                time.sleep(delay)  # be polite to ManageBac
                break

            except requests.RequestException:
                if attempt == retries - 1:
                    # give up on this file, continue with the rest
                    break
                time.sleep(2 * (attempt + 1))

