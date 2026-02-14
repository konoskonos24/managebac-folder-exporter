📦 ManageBac File Scraper (Fork)



🔗 Forked from: https://github.com/yutotakano/managebac-file-scraper

👤 Original author: yutotakano

A Python CLI tool that logs into ManageBac and downloads all files from the Files tab of your classes.
Downloads are organized by class and folder, with retry logic and rate-limit handling.

This fork extends the original archived project with new features and improvements.

✨ Features

🔐 Authenticated login using session cookies

🧭 Automatic class discovery

📁 Recursive folder discovery (BFS crawl)

⬇️ Download all files per class

🎯 Filter by class name or class ID

📂 List folders without downloading

📌 Download a specific folder only

🔁 Retry with exponential backoff

🧼 Safe filename sanitization

📊 Progress bars with tqdm

🆕 Changes in this fork

Added recursive folder discovery

Added --class-id and --class-name filters

Added --list-folders mode

Added --folder-id selective downloads

Improved rate-limit handling and retries

Improved filename sanitization

🛠 Installation
git clone https://github.com/<your-username>/managebac-file-scraper.git
cd managebac-file-scraper
pip install -r requirements.txt

🧩 Requirements

Python 3.8+

requests

beautifulsoup4

lxml

tqdm

🚀 Usage
python scrape.py <school_code> <email> <password> <output_dir>

🔎 Arguments
Argument	Description
school_code	The part between https:// and .managebac.com
email	Your ManageBac login email
password	Your ManageBac password
output_dir	Directory where downloads will be saved

Each class is saved into its own subfolder.

🎯 Optional filters
Download a single class by name
python scrape.py myschool email password downloads --class-name "biology"

Download a single class by ID
python scrape.py myschool email password downloads --class-id 12345

📂 List folders without downloading
python scrape.py myschool email password downloads --class-id 12345 --list-folders

📥 Download a specific folder
python scrape.py myschool email password downloads --class-id 12345 --folder-id 67890

❓ Show help
python scrape.py -h

🔒 Security Note

Avoid putting your password in shell history. Use an environment variable instead:

export MB_PASSWORD="your_password"
python scrape.py myschool email $MB_PASSWORD downloads


🚫 Never commit credentials, cookies, or downloaded files.

⚖️ Legal Notice

Use this tool only on accounts and data you are authorized to access.
You are responsible for complying with your institution’s policies and ManageBac terms of service.

This project is intended for personal backup and educational use.

📌 Project Status

This fork is actively maintained and includes improvements over the original archived repository.

📜 License

This project is licensed under the GNU General Public License v3.0.
It is a fork of managebac-file-scraper by yutotakano, also licensed under GPL-3.0.

See LICENSE.md for the full license text.

🙏 Acknowledgements

Thanks to yutotakano for the original project.
