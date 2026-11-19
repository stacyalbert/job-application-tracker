from datetime import datetime
import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


def clean(form, fields):
    """Strip whitespace; turn empty strings into None so MySQL stores NULL."""
    out = {}
    for f in fields:
        value = form.get(f, "").strip()
        out[f] = value if value else None
    return out


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


# ---------- Companies ----------

COMPANY_FIELDS = ["company_name", "industry", "website", "city", "state", "notes"]


def validate_company(d):
    errors = []
    if not d["company_name"]:
        errors.append("Company name is required.")
    elif len(d["company_name"]) > 100:
        errors.append("Company name must be 100 characters or fewer.")
    for field, label, maximum in (
        ("industry", "Industry", 50),
        ("website", "Website", 200),
        ("city", "City", 50),
        ("state", "State", 50),
    ):
        if d[field] and len(d[field]) > maximum:
            errors.append(f"{label} must be {maximum} characters or fewer.")
    if d["website"] and not d["website"].startswith(("http://", "https://")):
        errors.append("Website must start with http:// or https://")
    return errors


@app.route("/companies")
def companies():
    return render_template("companies.html", companies=db.get_all_companies())


@app.route("/companies/add", methods=["GET", "POST"])
def company_add():
    if request.method == "POST":
        data = clean(request.form, COMPANY_FIELDS)
        errors = validate_company(data)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("company_form.html", company=data, action="Add")
        db.add_company(data)
        flash("Company added.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company={}, action="Add")


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    existing = db.get_company(company_id)
    if not existing:
        flash("Company not found.", "error")
        return redirect(url_for("companies"))
    if request.method == "POST":
        data = clean(request.form, COMPANY_FIELDS)
        errors = validate_company(data)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("company_form.html", company=data, action="Edit")
        db.update_company(company_id, data)
        flash("Company updated.", "success")
        return redirect(url_for("companies"))
    return render_template("company_form.html", company=existing, action="Edit")


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id):
    db.delete_company(company_id)
    flash("Company deleted.", "success")
    return redirect(url_for("companies"))


# ---------- Jobs ----------

JOB_FIELDS = ["company_id", "job_title", "job_type", "salary_min", "salary_max",
              "job_url", "date_posted", "skills"]
JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]


@app.template_filter("salary_range")
def salary_range(job):
    lo, hi = job.get("salary_min"), job.get("salary_max")
    if lo and hi:
        return f"${lo:,} to ${hi:,}"
    if lo:
        return f"From ${lo:,}"
    if hi:
        return f"Up to ${hi:,}"
    return ""


def parse_skills_text(text):
    """'Python, sql, Python' -> ['Python', 'sql'] (trimmed, no case-insensitive duplicates)."""
    seen, skills = set(), []
    for item in (text or "").split(","):
        item = item.strip()
        if item and item.lower() not in seen:
            seen.add(item.lower())
            skills.append(item)
    return skills


def validate_job(raw):
    """Returns (cleaned_data, errors). raw holds the strings from the form."""
    errors, data = [], dict(raw)

    try:
        data["company_id"] = int(raw["company_id"])
        if not db.get_company(data["company_id"]):
            errors.append("Choose a company from the list.")
    except (TypeError, ValueError):
        errors.append("Choose a company.")

    if not raw["job_title"]:
        errors.append("Job title is required.")
    elif len(raw["job_title"]) > 100:
        errors.append("Job title must be 100 characters or fewer.")

    if raw["job_type"] and raw["job_type"] not in JOB_TYPES:
        errors.append("Choose a valid job type.")

    for key, label in (("salary_min", "Minimum salary"), ("salary_max", "Maximum salary")):
        if raw[key] is not None:
            try:
                data[key] = int(raw[key])
                if data[key] < 0:
                    errors.append(f"{label} can't be negative.")
            except ValueError:
                errors.append(f"{label} must be a whole number.")

    lo, hi = data.get("salary_min"), data.get("salary_max")
    if isinstance(lo, int) and isinstance(hi, int) and lo > hi:
        errors.append("Minimum salary can't be higher than maximum salary.")

    if raw["job_url"] and not raw["job_url"].startswith(("http://", "https://")):
        errors.append("Job URL must start with http:// or https://")
    if raw["job_url"] and len(raw["job_url"]) > 300:
        errors.append("Job URL must be 300 characters or fewer.")

    if raw["date_posted"]:
        try:
            datetime.strptime(raw["date_posted"], "%Y-%m-%d")
        except ValueError:
            errors.append("Date posted must be a valid date.")

    for key, label in (("salary_min", "Minimum salary"), ("salary_max", "Maximum salary")):
        value = data.get(key)
        if isinstance(value, int) and value > 2147483647:
            errors.append(f"{label} can't exceed 2,147,483,647.")

    data["skills"] = parse_skills_text(raw["skills"])
    return data, errors


def render_job_form(job, action):
    return render_template("job_form.html", job=job, action=action,
                           companies=db.get_all_companies(), job_types=JOB_TYPES)


@app.route("/jobs")
def jobs():
    return render_template("jobs.html", jobs=db.get_all_jobs())


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = db.get_job(job_id)
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("jobs"))
    return render_template("job_detail.html", job=job)


@app.route("/jobs/add", methods=["GET", "POST"])
def job_add():
    if request.method == "POST":
        raw = clean(request.form, JOB_FIELDS)
        data, errors = validate_job(raw)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_job_form(raw, "Add")
        db.add_job(data)
        flash("Job added.", "success")
        return redirect(url_for("jobs"))
    return render_job_form({}, "Add")


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    existing = db.get_job(job_id)
    if not existing:
        flash("Job not found.", "error")
        return redirect(url_for("jobs"))
    if request.method == "POST":
        raw = clean(request.form, JOB_FIELDS)
        data, errors = validate_job(raw)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_job_form(raw, "Edit")
        db.update_job(job_id, data)
        flash("Job updated.", "success")
        return redirect(url_for("jobs"))
    form = dict(existing)
    form["skills"] = ", ".join(existing["skills"])
    return render_job_form(form, "Edit")


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def job_delete(job_id):
    db.delete_job(job_id)
    flash("Job deleted.", "success")
    return redirect(url_for("jobs"))

# ---------- Applications ----------

APP_FIELDS = ["job_id", "application_date", "status", "resume_version",
              "cover_letter_sent", "notes", "round_type", "round_date"]
APPLICATION_STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]
ROUND_TYPES = ["Phone screen", "Technical", "Behavioral", "On-site", "Final round"]


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def validate_application(raw, existing_interview=None):
    """Returns (cleaned_data, errors). existing_interview keeps rounds already saved."""
    errors, data = [], dict(raw)

    try:
        data["job_id"] = int(raw["job_id"])
        if not db.get_job(data["job_id"]):
            errors.append("Choose a job from the list.")
    except (TypeError, ValueError):
        errors.append("Choose a job.")

    if not raw["application_date"]:
        errors.append("Application date is required.")
    else:
        try:
            applied = datetime.strptime(raw["application_date"], "%Y-%m-%d")
            if applied.date() > datetime.now().date():
                errors.append("Application date can't be in the future.")
        except ValueError:
            errors.append("Application date must be a valid date.")

    data["status"] = raw["status"] or "Applied"
    if data["status"] not in APPLICATION_STATUSES:
        errors.append("Choose a valid status.")

    if raw["resume_version"] and len(raw["resume_version"]) > 50:
        errors.append("Resume version must be 50 characters or fewer.")

    data["cover_letter_sent"] = bool(raw["cover_letter_sent"])

    if raw["notes"] and len(raw["notes"]) > 2000:
        errors.append("Interview notes must be 2,000 characters or fewer.")

    if raw["round_type"] and raw["round_type"] not in ROUND_TYPES:
        errors.append("Choose a valid interview type.")
    if raw["round_date"]:
        if not raw["round_type"]:
            errors.append("Choose an interview type for the interview date.")
        try:
            datetime.strptime(raw["round_date"], "%Y-%m-%d")
        except ValueError:
            errors.append("Interview date must be a valid date.")

    # Build the JSON stored in interview_data: keep saved rounds, update notes, add a new round.
    interview = dict(existing_interview or {})
    if raw["notes"]:
        interview["notes"] = raw["notes"]
    else:
        interview.pop("notes", None)
    if raw["round_type"]:
        rounds = list(interview.get("rounds") or [])
        rounds.append({"type": raw["round_type"], "date": raw["round_date"] or ""})
        interview["rounds"] = rounds
    data["interview"] = interview or None
    return data, errors


def render_application_form(form, action, rounds=None):
    return render_template("application_form.html", application=form, action=action,
                           jobs=db.get_all_jobs(), statuses=APPLICATION_STATUSES,
                           round_types=ROUND_TYPES, rounds=rounds or [])


@app.route("/applications")
def applications():
    return render_template("applications.html", applications=db.get_all_applications())


@app.route("/applications/<int:application_id>")
def application_detail(application_id):
    application = db.get_application(application_id)
    if not application:
        flash("Application not found.", "error")
        return redirect(url_for("applications"))
    return render_template("application_detail.html", application=application)


@app.route("/applications/add", methods=["GET", "POST"])
def application_add():
    if request.method == "POST":
        raw = clean(request.form, APP_FIELDS)
        data, errors = validate_application(raw)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_application_form(raw, "Add")
        db.add_application(data)
        flash("Application added.", "success")
        return redirect(url_for("applications"))
    form = {"job_id": request.args.get("job_id"),
            "application_date": today_str(), "status": "Applied"}
    return render_application_form(form, "Add")


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def application_edit(application_id):
    existing = db.get_application(application_id)
    if not existing:
        flash("Application not found.", "error")
        return redirect(url_for("applications"))
    rounds = existing["interview"].get("rounds") or []
    if request.method == "POST":
        raw = clean(request.form, APP_FIELDS)
        data, errors = validate_application(raw, existing["interview"])
        if errors:
            for e in errors:
                flash(e, "error")
            return render_application_form(raw, "Edit", rounds)
        db.update_application(application_id, data)
        flash("Application updated.", "success")
        return redirect(url_for("applications"))
    form = dict(existing)
    form["notes"] = existing["interview"].get("notes")
    return render_application_form(form, "Edit", rounds)


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def application_delete(application_id):
    db.delete_application(application_id)
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))


# ---------- Contacts ----------

CONTACT_FIELDS = [
    "company_id", "contact_name", "title", "email",
    "phone", "linkedin_url", "notes"
]


def validate_contact(raw):
    """Validate contact form data and prepare it for database insertion."""
    errors = []
    data = dict(raw)

    try:
        data["company_id"] = int(raw["company_id"])
        if not db.get_company(data["company_id"]):
            errors.append("Choose a company from the list.")
    except (TypeError, ValueError):
        errors.append("Choose a company.")

    if not raw["contact_name"]:
        errors.append("Contact name is required.")
    elif len(raw["contact_name"]) > 100:
        errors.append("Contact name must be 100 characters or fewer.")

    if raw["title"] and len(raw["title"]) > 100:
        errors.append("Title must be 100 characters or fewer.")

    if raw["email"]:
        if len(raw["email"]) > 100:
            errors.append("Email must be 100 characters or fewer.")
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw["email"]):
            errors.append("Enter a valid email address.")

    if raw["linkedin_url"] and not raw["linkedin_url"].startswith(
        ("http://", "https://")
    ):
        errors.append("LinkedIn URL must start with http:// or https://")
    if raw["linkedin_url"] and len(raw["linkedin_url"]) > 200:
        errors.append("LinkedIn URL must be 200 characters or fewer.")

    if raw["phone"] and len(raw["phone"]) > 20:
        errors.append("Phone must be 20 characters or fewer.")

    if raw["notes"] and len(raw["notes"]) > 2000:
        errors.append("Notes must be 2,000 characters or fewer.")

    return data, errors


def render_contact_form(contact, action):
    return render_template(
        "contact_form.html",
        contact=contact,
        action=action,
        companies=db.get_all_companies()
    )


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", contacts=db.get_all_contacts())


@app.route("/contacts/add", methods=["GET", "POST"])
def contact_add():
    if request.method == "POST":
        raw = clean(request.form, CONTACT_FIELDS)
        data, errors = validate_contact(raw)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_contact_form(raw, "Add")
        db.add_contact(data)
        flash("Contact added.", "success")
        return redirect(url_for("contacts"))

    return render_contact_form({}, "Add")


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    existing = db.get_contact(contact_id)
    if not existing:
        flash("Contact not found.", "error")
        return redirect(url_for("contacts"))

    if request.method == "POST":
        raw = clean(request.form, CONTACT_FIELDS)
        data, errors = validate_contact(raw)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_contact_form(raw, "Edit")
        db.update_contact(contact_id, data)
        flash("Contact updated.", "success")
        return redirect(url_for("contacts"))

    return render_contact_form(existing, "Edit")


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    db.delete_contact(contact_id)
    flash("Contact deleted.", "success")
    return redirect(url_for("contacts"))


# ---------- Dashboard ----------

@app.route("/dashboard")
def dashboard():
    counts = db.get_table_counts()
    status_counts = db.get_application_status_counts()
    recent_applications = db.get_recent_applications(5)
    return render_template(
        "dashboard.html",
        counts=counts,
        status_counts=status_counts,
        recent_applications=recent_applications
    )


# ---------- Job Match ----------

def normalize_skills(text):
    """Normalize comma-separated skills into unique lowercase strings."""
    seen = set()
    skills = []
    for item in (text or "").split(","):
        skill = item.strip().lower()
        if skill and skill not in seen:
            seen.add(skill)
            skills.append(skill)
    return skills


def calculate_job_matches(jobs, skills_text):
    """Return jobs with requirements sorted by skill match percentage."""
    user_skills = set(normalize_skills(skills_text))
    matches = []

    for job in jobs:
        requirements = job.get("skills") or []
        if not requirements:
            continue

        normalized_requirements = []
        normalized_lookup = set()
        for requirement in requirements:
            normalized = str(requirement).strip()
            lookup_key = normalized.lower()
            if normalized and lookup_key not in normalized_lookup:
                normalized_requirements.append(normalized)
                normalized_lookup.add(lookup_key)
        if not normalized_requirements:
            continue

        requirement_lookup = {
            skill.lower(): skill for skill in normalized_requirements
        }
        matched_names = [
            requirement_lookup[skill]
            for skill in requirement_lookup
            if skill in user_skills
        ]
        matched_count = len(matched_names)
        total_count = len(normalized_requirements)
        missing_names = [
            skill for skill in normalized_requirements
            if skill.lower() not in user_skills
        ]

        result = dict(job)
        result["percent"] = round((matched_count / total_count) * 100)
        result["matched_count"] = matched_count
        result["total_count"] = total_count
        result["matched_skills"] = matched_names
        result["missing_skills"] = missing_names
        matches.append(result)

    matches.sort(key=lambda job: (-job["percent"], job["job_title"].lower()))
    return matches


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_text = ""
    matches = []
    if request.method == "POST":
        skills_text = (request.form.get("skills") or "").strip()
        matches = calculate_job_matches(db.get_all_jobs(), skills_text)
    return render_template(
        "job_match.html",
        skills_text=skills_text,
        matches=matches
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(mysql.connector.Error)
def database_error(error):
    app.logger.error("Database error: %s", error)
    return render_template("database_error.html"), 500

# Keep this block LAST: routes defined below it would never be registered.
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))