managebac-file-scraper (fork)

Forked from: https://github.com/yutotakano/managebac-file-scraper

Original author: yutotakano

This is a Python CLI tool that downloads all files listed in the Files tab of ManageBac.
It authenticates using your credentials, iterates over each class, discovers folders, and downloads the available files into organized local directories.

Changes in this fork

Added folder discovery (recursive crawl)

Added --class-id and --class-name filters

Added --list-folders mode (no download)

Added --folder-id selective downloads

Added retry logic with exponential backoff

Improved filename sanitization

Improved rate-limit handling

Usage

python scrape.py <school_code> <email> <password> <output_dir>

Arguments

school_code → the part between https:// and .managebac.com
email → your ManageBac login email
password → your ManageBac password
output_dir → directory where downloads will be saved

Each class is saved into its own subfolder.

Optional filters

Download a single class by name:

python scrape.py myschool email password downloads --class-name "biology"

Download a single class by ID:

python scrape.py myschool email password downloads --class-id 12345

List folders without downloading:

python scrape.py myschool email password downloads --class-id 12345 --list-folders

Download a specific folder:

python scrape.py myschool email password downloads --class-id 12345 --folder-id 67890

Show help:

python scrape.py -h

Security note

Avoid putting your password in shell history.
You can use an environment variable instead:

export MB_PASSWORD="your_password"
python scrape.py myschool email $MB_PASSWORD downloads

Legal notice

Use this tool only on accounts and data you are authorized to access.
You are responsible for complying with your institution’s policies and ManageBac terms of service.

This project is intended for personal backup and educational use.

Disclaimer

This tool may not handle all ManageBac edge cases.
It is provided as a best-effort utility and may require adaptation for specific schools or account configurations.

License

GNU General Public License v3.0
See LICENSE.md for details.
