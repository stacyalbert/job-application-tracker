# Job Application Tracker

A Flask and MySQL web application for tracking companies, jobs, applications,
contacts, and skill matches.

## Prerequisites

- macOS, Linux, or Windows
- Python 3.10 or newer
- MySQL 8
- MySQL user with permission to create the `job_tracker` database

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/stacyalbert/job-application-tracker.git
   cd job-application-tracker
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the database and sample data:

   ```bash
   mysql -u root -p < schema.sql
   ```

   **Warning:** `schema.sql` drops and recreates the `job_tracker` database, so
   this command deletes any existing data in that database. Enter the MySQL
   password at the prompt. The password is not stored in the project.

5. Set the database environment variables in the terminal:

   ```bash
   read -s DB_PASSWORD
   export DB_PASSWORD
   export DB_HOST=localhost
   export DB_USER=root
   export DB_NAME=job_tracker
   ```

   `read -s` prompts for the password without displaying it.
   Repeat these environment-variable commands in each new terminal window.

6. Start the application:

   ```bash
   python app.py
   ```

   Open http://127.0.0.1:5000. If port 5000 is busy:

   ```bash
   PORT=5001 python app.py
   ```

## Features

- CRUD and validation for companies, jobs, applications, and contacts
- List and detail views
- Dashboard totals, application status counts, and recent applications
- Job Match percentage calculations with matched and missing skills
- Live table search and delete confirmation dialogs
- Flash messages and friendly 404/database error pages
- Parameterized SQL and cascading foreign keys

## Running checks

```bash
python -m py_compile app.py database.py
```