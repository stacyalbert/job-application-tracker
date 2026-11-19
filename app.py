from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
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
    return redirect(url_for("companies"))


# ---------- Companies ----------

COMPANY_FIELDS = ["company_name", "industry", "website", "city", "state", "notes"]


def validate_company(d):
    errors = []
    if not d["company_name"]:
        errors.append("Company name is required.")
    elif len(d["company_name"]) > 100:
        errors.append("Company name must be 100 characters or fewer.")
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

    if raw["date_posted"]:
        try:
            datetime.strptime(raw["date_posted"], "%Y-%m-%d")
        except ValueError:
            errors.append("Date posted must be a valid date.")

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


# Keep this block LAST: routes defined below it would never be registered.
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))