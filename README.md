# atlassian-addons-audit-sheet

This tool will synchronize the list of Enabled User-Installed plugins in JIRA,
Confluence, and Bitbucket with a Google Sheet for documentation and auditing.

## Getting Started

You will need to update **audit.py** for your environment:
* **sheet_url** - URL of your Google Sheet. A sample that you can copy is here:
https://docs.google.com/spreadsheets/d/1iBHfz0TOyPxC3JRQp30v2Qs9lHbKfwOG-eZ53BK_ok0/edit#gid=0
  * Replace `YOURGOOGLESHEET` with your Google Sheet URL.
* **possibletargets** - Sheet Names and URLs of your Confluence, JIRA, and Stash servers.
  * Replace `YOURCONFLUENCESERVER` with URL to your Confluence server.
  * Replace `YOURJIRASERVER` with URL to your Jira server.
  * Replace `YOURBITBUCKETSERVER` with URL to your Stash/Bitbucket server.

You will also need to update **jira_credentials.py** with your username and
password. (We assume the same credentials will work across all your servers.)

## Prerequisites

* Python 3.0
* Requests - Python Library for HTTP requests
  http://docs.python-requests.org/en/master/
* pygsheets - Python Library for Google Sheets
  http://pygsheets.readthedocs.io/en/latest/
* Authorize pygsheets to use the Google Sheets API
  http://pygsheets.readthedocs.io/en/latest/authorizing.html
(The process will generate a **client_secret.json** to be copied to working
directory. Upon first run, a web browser will open up to authorize, which will
generate **sheets.googleapis.com-python.json** in your working directory.)

## Usage

Once you've installed the required libraries, you should be able to simply run:
```
./audit.py hosts (jira, confluence, stash, or all)
```

As it runs, the script will echo out each Plugin it finds, along with
description, current version, and pricing; it then updates the sheet with this
information.

## Extras

**sheetscript.gs** is an Apps Script that can be added to your Google Sheet to
automatically generate an email when licenses are about to expire. Additionally,
it adds a pop-up alert to the sheet warning users not to edit any columns that
may be overwritten by the audit.py script. You'll need to update **sheetscript.gs**
then specify these values:
* **emailAddress**, replace `YOUREMAILADDRESS` with your email address.
* (optional) **daysprior** (default 7-day notice), replace `7` with your preferred day number.

The [sample Google Sheet](https://docs.google.com/spreadsheets/d/1iBHfz0TOyPxC3JRQp30v2Qs9lHbKfwOG-eZ53BK_ok0/edit#gid=0)
contains conditional formatting that automatically color codes cells
accordingly:
* Tag column (Req = Green, Attn = Red)
* Version mismatch with Latest version - Yellow
* License expiring within 7 days - Orange
* Known Atlassian built-in add-on - Blue

## License

addons-audit-sheet is licensed under the [Apache License, v2.0](LICENSE).

## Disclaimer

This is not an official Google product.
