import argparse
import os
import managebac_authenticator
import managebac_browser
import downloader
from tqdm import tqdm
from multiprocessing import freeze_support


def filter_classes(classes, class_id=None, class_name=None):
    if class_id:
        wanted_id = str(class_id).strip()
        return [c for c in classes if c['id'] == wanted_id]
    if class_name:
        wanted = class_name.strip().lower()
        return [c for c in classes if wanted in c['name'].strip().lower()]
    return classes


if __name__ == '__main__':
    freeze_support()

    parser = argparse.ArgumentParser(
        description="ManageBac scraper: list folders or download files from a class/folder."
    )
    parser.add_argument('school_code', help='https://<school_code>.managebac.com')
    parser.add_argument('username', help='Login email address')
    parser.add_argument('password', help='Login password')
    parser.add_argument('output_dir', help='Output directory location')

    parser.add_argument('--class-id', default=None, help='Numeric class ID (exact match)')
    parser.add_argument('--class-name', default=None, help='Filter classes whose name contains this text')

    # Download starting point
    parser.add_argument('--folder-id', default=None, help='Folder ID within the selected class')

    # Folder discovery mode (no download)
    parser.add_argument('--list-folders', action='store_true', help='Only list folders (no download)')
    parser.add_argument('--rescan', type=int, default=1, help='How many discovery passes to run (default: 1)')
    parser.add_argument('--max-pages', type=int, default=500, help='Max pages to fetch during folder discovery')

    args = parser.parse_args()

    cookie_jar = managebac_authenticator.get_jar(args.school_code, args.username, args.password)
    classes = managebac_browser.get_classes(args.school_code, cookie_jar)
    classes = filter_classes(classes, args.class_id, args.class_name)

    # ---- LIST FOLDERS MODE ----
    if args.list_folders:
        if len(classes) != 1:
            print("Please select exactly ONE class when using --list-folders (use --class-id or --class-name).")
            managebac_authenticator.logout(args.school_code, cookie_jar)
            raise SystemExit(1)

        class_id = classes[0]['id']
        folders, stats = managebac_browser.discover_folders(
            args.school_code,
            cookie_jar,
            class_id=class_id,
            start_folder_id=args.folder_id,
            passes=args.rescan,
            max_pages=args.max_pages
        )

        folders = sorted(folders, key=lambda x: int(x["id"]))
        print(f"\nFound {len(folders)} folders in class {class_id}:")
        for f in folders:
            print(f'{f["id"]}\t{f["name"]}\t{f["url"]}')

        print(f"\nStats: fetched={stats.get('fetched', 0)} blocked={stats.get('blocked', 0)} rate_limited={stats.get('rate_limited', 0)}")
        managebac_authenticator.logout(args.school_code, cookie_jar)
        raise SystemExit(0)

    # ---- DOWNLOAD MODE ----
    dest_dir = args.output_dir
    if not dest_dir.endswith('/') and not dest_dir.endswith('\\'):
        dest_dir += os.sep

    with tqdm(desc='Class Progress: ', postfix='') as t:
        for class_dict in classes:
            t.postfix = class_dict['name']

            base_class_dir = os.path.join(dest_dir, managebac_browser.get_valid_filename(class_dict['name']))
            os.makedirs(base_class_dir, exist_ok=True)

            # If downloading a specific folder, keep it in a subfolder
            if args.folder_id:
                class_dir = os.path.join(base_class_dir, f"folder_{str(args.folder_id).strip()}")
            else:
                class_dir = base_class_dir
            os.makedirs(class_dir, exist_ok=True)

            files = managebac_browser.get_files(
                args.school_code,
                cookie_jar,
                class_dict,
                folder_id=args.folder_id
            )

            print(f"{class_dict['name']} ({class_dict['id']}) => files found: {len(files)}")
            downloader.download(files, dir=class_dir, cookies=cookie_jar)

            t.update()

    managebac_authenticator.logout(args.school_code, cookie_jar)
