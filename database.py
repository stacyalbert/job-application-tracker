import json
import os
import mysql.connector


def get_db():
    """Open a new connection. Credentials come from environment variables."""
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "job_tracker"),
    )


def fetch_all(sql, params=()):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def fetch_one(sql, params=()):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def execute(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


# ---------- Companies ----------

def get_all_companies():
    return fetch_all("SELECT * FROM companies ORDER BY company_name")


def get_company(company_id):
    return fetch_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))


def add_company(d):
    return execute(
        """INSERT INTO companies (company_name, industry, website, city, state, notes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (d["company_name"], d["industry"], d["website"], d["city"], d["state"], d["notes"]),
    )


def update_company(company_id, d):
    return execute(
        """UPDATE companies
           SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s
           WHERE company_id=%s""",
        (d["company_name"], d["industry"], d["website"], d["city"], d["state"], d["notes"], company_id),
    )


def delete_company(company_id):
    return execute("DELETE FROM companies WHERE company_id = %s", (company_id,))

# ---------- Jobs ----------

def parse_skills(value):
    """Turn whatever MySQL returns for a JSON column into a Python list."""
    if value is None:
        return []
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    return value if isinstance(value, list) else []


def _with_skills(job):
    if job is not None:
        job["skills"] = parse_skills(job.get("requirements"))
    return job


JOB_SELECT = """SELECT j.*, c.company_name
                FROM jobs j
                JOIN companies c ON j.company_id = c.company_id"""


def get_all_jobs():
    rows = fetch_all(JOB_SELECT + " ORDER BY j.date_posted DESC, j.job_title")
    return [_with_skills(r) for r in rows]


def get_job(job_id):
    return _with_skills(fetch_one(JOB_SELECT + " WHERE j.job_id = %s", (job_id,)))


def add_job(d):
    return execute(
        """INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
                             job_url, date_posted, requirements)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (d["company_id"], d["job_title"], d["job_type"], d["salary_min"], d["salary_max"],
         d["job_url"], d["date_posted"], json.dumps(d["skills"])),
    )


def update_job(job_id, d):
    return execute(
        """UPDATE jobs
           SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, salary_max=%s,
               job_url=%s, date_posted=%s, requirements=%s
           WHERE job_id=%s""",
        (d["company_id"], d["job_title"], d["job_type"], d["salary_min"], d["salary_max"],
         d["job_url"], d["date_posted"], json.dumps(d["skills"]), job_id),
    )


def delete_job(job_id):
    return execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))

# ---------- Applications ----------

def parse_json_object(value):
    """Turn whatever MySQL returns for a JSON column into a Python dict."""
    if value is None:
        return {}
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def _with_interview(row):
    if row is not None:
        row["interview"] = parse_json_object(row.get("interview_data"))
    return row


APPLICATION_SELECT = """SELECT a.*, j.job_title, c.company_name
                        FROM applications a
                        JOIN jobs j ON a.job_id = j.job_id
                        JOIN companies c ON j.company_id = c.company_id"""


def get_all_applications():
    rows = fetch_all(APPLICATION_SELECT + " ORDER BY a.application_date DESC, a.application_id DESC")
    return [_with_interview(r) for r in rows]


def get_application(application_id):
    return _with_interview(
        fetch_one(APPLICATION_SELECT + " WHERE a.application_id = %s", (application_id,))
    )


def add_application(d):
    return execute(
        """INSERT INTO applications (job_id, application_date, status, resume_version,
                                     cover_letter_sent, interview_data)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (d["job_id"], d["application_date"], d["status"], d["resume_version"],
         d["cover_letter_sent"], json.dumps(d["interview"]) if d["interview"] else None),
    )


def update_application(application_id, d):
    return execute(
        """UPDATE applications
           SET job_id=%s, application_date=%s, status=%s, resume_version=%s,
               cover_letter_sent=%s, interview_data=%s
           WHERE application_id=%s""",
        (d["job_id"], d["application_date"], d["status"], d["resume_version"],
         d["cover_letter_sent"], json.dumps(d["interview"]) if d["interview"] else None,
         application_id),
    )


def delete_application(application_id):
    return execute("DELETE FROM applications WHERE application_id = %s", (application_id,))

