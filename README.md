# Nextmove — Job Application Tracker

Nextmove is a local Flask web app for organizing a job search. Track companies,
job postings, applications, interview details, and professional contacts. The
dashboard summarizes your search, and Skill Match compares your skills with
saved job requirements.

## What you need

- Python 3.10 or newer
- MySQL 8.0 or newer, running locally
- A MySQL account that can create and drop the `job_tracker` database for
  setup, then read and write its tables while using the app
- A terminal and a web browser
- Git, to clone the repository

Installers are available from the official download pages:
[Python](https://www.python.org/downloads/),
[MySQL Community Server](https://dev.mysql.com/downloads/mysql/),
[MySQL Workbench](https://dev.mysql.com/downloads/workbench/), and
[Git](https://git-scm.com/downloads). Workbench is optional if you use the
MySQL command-line client.

The app uses Flask and the MySQL Connector/Python package. Dependencies are
listed in `requirements.txt`; no separate Node.js installation is needed.

## 1. Get the project

Clone the repository and enter its folder:

```bash
git clone https://github.com/stacyalbert/job-application-tracker.git
cd job-application-tracker
```

If Git is not installed, download the repository ZIP from GitHub and extract
it. Open a terminal in the extracted `job-application-tracker` folder.

## 2. Create a Python environment

Using a virtual environment keeps this project's Python packages separate
from other projects.

### macOS or Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents environment activation, use Command Prompt instead:

```bat
py -m venv venv
venv\Scripts\activate.bat
```

When activated, the terminal prompt usually shows `(venv)`.

## 3. Install Python dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Create and populate the MySQL database

Make sure your local MySQL server is running. The project includes `schema.sql`,
which creates the four tables (`companies`, `jobs`, `applications`, and
`contacts`) and inserts example records.

> **Important: `schema.sql` is destructive.** It starts by dropping the
> existing `job_tracker` database and then recreating it. Running it again
> permanently deletes any data currently stored in that database. Only run it
> during initial setup or when you intentionally want to reset the project data.

Choose **one** way to run the schema:

### Option A: MySQL command line (macOS, Linux, or a terminal with MySQL CLI)

From the project directory:

```bash
mysql -u root -p < schema.sql
```

Replace `root` with your MySQL administrator username if it is different. Enter
that account's password when MySQL prompts. No password is included in this
command or saved in the project.

### Option B: MySQL Workbench (all platforms)

1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `schema.sql` from this project folder.
3. Review the destructive warning above and confirm the script targets your
   local development server.
4. Execute the whole script (the lightning-bolt **Execute** control).
5. In the Schemas panel, refresh and confirm that `job_tracker` appears.

The app's default connection settings expect a local MySQL server, database
name `job_tracker`, and user `root`. You can override these settings with
environment variables in the next step.

## 5. Set database connection variables

The database password is read from the `DB_PASSWORD` environment variable. Do
not put it in `app.py`, `database.py`, or any other project file. These
variables apply only to the current terminal session, so set them again in
each new terminal window.

### macOS or Linux (zsh/bash)

From the project directory, enter:

```bash
read -s DB_PASSWORD
```

Type the MySQL password and press Enter; the characters will not appear. Then
export the connection settings:

```bash
export DB_PASSWORD
export DB_HOST=localhost
export DB_USER=root
export DB_NAME=job_tracker
```

If your MySQL username or database name differs, change `DB_USER` or
`DB_NAME` to match.

### Windows PowerShell

This securely prompts for the password and keeps the environment variables
only in the current PowerShell session:

```powershell
$securePassword = Read-Host "MySQL password" -AsSecureString
$credential = New-Object System.Net.NetworkCredential("", $securePassword)
$env:DB_PASSWORD = $credential.Password
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_NAME = "job_tracker"
Remove-Variable securePassword, credential
```

Change `DB_USER` if you used a different MySQL account. Avoid putting a real
password directly in a command, script, or project file.

## 6. Start Nextmove

With the virtual environment active and database variables set, start the
Flask app from the project directory:

```bash
python app.py
```

The terminal should report that the server is running. Open this address in
your browser:

**http://127.0.0.1:5000**

Keep the terminal open while using the app. To stop the server, focus that
terminal and press **Ctrl+C**.

If port 5000 is already occupied, choose another port:

### macOS or Linux

```bash
PORT=5001 python app.py
```

### Windows PowerShell

```powershell
$env:PORT = "5001"
python app.py
```

Then open **http://127.0.0.1:5001**.

## Using the application

- **Overview:** see company, job, application, and contact totals, application
  status counts, and recent applications.
- **Companies:** create, view, edit, search, and delete companies.
- **Job library:** save positions, salary details, posting links, and required
  skills. Open a job for its detail view or track an application for it.
- **Applications:** record application dates, status, resume version, cover
  letter, interview notes, and interview rounds.
- **People:** save contacts associated with companies.
- **Skill match:** enter comma-separated skills such as `Python, SQL, Flask`
  to see match percentages and matched or missing requirements for each job.

The project loads sample data from `schema.sql`. You can use those sample
records to explore the screens, or add your own records through the app.
Deleting a company also deletes its associated jobs, applications, and contacts
because the database uses cascading foreign keys.

## Troubleshooting

### `mysql: command not found`

The MySQL command-line client is not installed or is not on your PATH. Start
MySQL Workbench and run `schema.sql` there, or install/configure the MySQL
client for your platform.

### `Access denied` or a database connection error

- Confirm the MySQL server is running.
- Verify `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in the same terminal
  where you start Flask.
- Check that the MySQL account can connect locally and access `job_tracker`.
- If the app is running, stop it with Ctrl+C, set the variables again, and
  restart it.

### `Unknown database 'job_tracker'` or missing-table errors

The schema has not been run successfully. Use MySQL Workbench or the MySQL
command-line instructions in Step 4. Remember that rerunning `schema.sql`
deletes existing project data.

### `ModuleNotFoundError`

Activate the virtual environment and install dependencies again:

```bash
python -m pip install -r requirements.txt
```

### The browser cannot connect

Keep the Flask terminal running, use the exact URL and port printed there, and
check whether you selected an alternate port such as 5001.

## Project files

```text
app.py                 Flask routes, validation, and page handlers
database.py            MySQL connection and parameterized database queries
schema.sql             Database schema and example records
requirements.txt       Python dependencies
templates/             Jinja HTML templates
static/style.css       Application styles and responsive layouts
static/app.js          Delete confirmations, flash dismissal, and table search
AI_USAGE.md             AI tools, prompts, generated work, and reflections
```

## Checks

With the virtual environment active, compile the Python files:

```bash
python -m py_compile app.py database.py
```

## Development and security note

This project is configured for a local course demonstration. Run it on
`127.0.0.1` for development; do not expose Flask's built-in development server
to the public internet. The app does not currently implement user
authentication, so it is not configured for multi-user or public production
hosting.
