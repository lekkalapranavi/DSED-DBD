import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ============================================================
# MATCHER
# ============================================================

# Supports your existing matcher.py as well as the newer version.
try:
    from matcher import (
        extract_text,
        extract_resume_details,
        compute_match_score
    )
except ImportError:
    from matcher import (
        extract_text_from_pdf,
        detect_skills,
        compute_match_score
    )

    def extract_text(filepath):
        return extract_text_from_pdf(filepath)

    def extract_resume_details(text):
        skills = detect_skills(text)

        return {
            "skills": skills,
            "education": "",
            "experience": "",
            "certifications": ""
        }


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(
    BASE_DIR,
    "job_portal.db"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

app = Flask(__name__)

app.secret_key = "college-project-secret-key"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def init_db_if_needed():

    if not os.path.exists(DATABASE):

        print("[app] Creating database...")

        conn = get_db()

        schema_path = os.path.join(
            BASE_DIR,
            "schema.sql"
        )

        with open(
            schema_path,
            "r",
            encoding="utf-8"
        ) as file:

            conn.executescript(
                file.read()
            )

        conn.commit()
        conn.close()

        # Add demo data if available
        try:
            import seed_data

            conn = get_db()

            seed_data.run(conn)

            conn.close()

        except Exception as e:

            print(
                "[app] Seed data skipped:",
                e
            )

        print(
            "[app] Database created successfully."
        )


# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def current_user():

    if "user_id" not in session:
        return None

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()

    conn.close()

    return user


def login_required(role=None):

    def decorator(function):

        @wraps(function)
        def wrapped(*args, **kwargs):

            user = current_user()

            if user is None:

                flash(
                    "Please log in to continue.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            if role and user["role"] != role:

                flash(
                    "You don't have access to that page.",
                    "error"
                )

                return redirect(
                    url_for("home")
                )

            return function(
                *args,
                **kwargs
            )

        return wrapped

    return decorator


@app.context_processor
def inject_user():

    return {
        "logged_in_user": current_user()
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    conn = get_db()

    stats = {
        "jobs": conn.execute(
            "SELECT COUNT(*) AS c FROM jobs"
        ).fetchone()["c"],

        "companies": conn.execute(
            """
            SELECT COUNT(DISTINCT company) AS c
            FROM jobs
            """
        ).fetchone()["c"],

        "seekers": conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM users
            WHERE role = 'jobseeker'
            """
        ).fetchone()["c"]
    }

    featured_jobs = conn.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY posted_at DESC
        LIMIT 3
        """
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        stats=stats,
        featured_jobs=featured_jobs
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        )

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        if not name or not email or not password:

            flash(
                "Please complete all required fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if role not in {
            "jobseeker",
            "recruiter"
        }:

            flash(
                "Invalid account type.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if role == "recruiter" and not company_name:

            flash(
                "Recruiters must provide a company name.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        conn = get_db()

        existing = conn.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
            """,
            (
                email,
            )
        ).fetchone()

        if existing:

            conn.close()

            flash(
                "An account with that email already exists.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        conn.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                role,
                company_name
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                generate_password_hash(password),
                role,
                company_name or None
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Account created successfully. Please log in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (
                email,
            )
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.clear()

            session["user_id"] = user["user_id"]
            session["role"] = user["role"]

            flash(
                f"Welcome back, {user['name']}!",
                "success"
            )

            if user["role"] == "recruiter":

                return redirect(
                    url_for(
                        "recruiter_dashboard"
                    )
                )

            return redirect(
                url_for(
                    "jobseeker_dashboard"
                )
            )

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# BROWSE JOBS + SEARCH
# ============================================================

@app.route("/jobs")
def jobs():

    conn = get_db()

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    job_type = request.args.get(
        "job_type",
        ""
    ).strip()

    query = """
        SELECT *
        FROM jobs
        WHERE 1 = 1
    """

    params = []

    # Search title/company/location/
    # description/skills
    if keyword:

        query += """
            AND (
                title LIKE ?
                OR company LIKE ?
                OR location LIKE ?
                OR description LIKE ?
                OR skills_required LIKE ?
            )
        """

        value = f"%{keyword}%"

        params.extend([
            value,
            value,
            value,
            value,
            value
        ])

    if location:

        query += """
            AND location LIKE ?
        """

        params.append(
            f"%{location}%"
        )

    if job_type:

        query += """
            AND job_type = ?
        """

        params.append(
            job_type
        )

    query += """
        ORDER BY posted_at DESC
    """

    job_rows = conn.execute(
        query,
        params
    ).fetchall()

    all_locations = [
        row["location"]
        for row in conn.execute(
            """
            SELECT DISTINCT location
            FROM jobs
            ORDER BY location
            """
        ).fetchall()
    ]

    conn.close()

    return render_template(
        "jobs.html",
        jobs=job_rows,
        keyword=keyword,
        location=location,
        job_type=job_type,
        all_locations=all_locations
    )


# ============================================================
# JOB DETAILS
# ============================================================

@app.route(
    "/job/<int:job_id>"
)
def job_details(job_id):

    conn = get_db()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        """,
        (
            job_id,
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash(
            "That job could not be found.",
            "error"
        )

        return redirect(
            url_for("jobs")
        )

    already_applied = None
    user_resumes = []

    user = current_user()

    if user and user["role"] == "jobseeker":

        already_applied = conn.execute(
            """
            SELECT 1
            FROM applications
            WHERE job_id = ?
            AND user_id = ?
            """,
            (
                job_id,
                user["user_id"]
            )
        ).fetchone()

        user_resumes = conn.execute(
            """
            SELECT *
            FROM resumes
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            """,
            (
                user["user_id"],
            )
        ).fetchall()

    recruiter = conn.execute(
        """
        SELECT
            name,
            company_name
        FROM users
        WHERE user_id = ?
        """,
        (
            job["recruiter_id"],
        )
    ).fetchone()

    conn.close()

    return render_template(
        "job_details.html",
        job=job,
        already_applied=already_applied,
        recruiter=recruiter,
        user_resumes=user_resumes
    )


# ============================================================
# JOB SEEKER DASHBOARD
# ============================================================

@app.route(
    "/jobseeker/dashboard"
)
@login_required(
    role="jobseeker"
)
def jobseeker_dashboard():

    user = current_user()

    conn = get_db()

    # --------------------------------------------------------
    # RESUMES
    # --------------------------------------------------------

    resumes = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """,
        (
            user["user_id"],
        )
    ).fetchall()

    # --------------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------------

    applications = conn.execute(
        """
        SELECT
            a.*,
            j.title,
            j.company,
            j.location,
            j.job_type,
            m.match_score,
            m.matched_skills,
            m.missing_skills
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.job_id
        LEFT JOIN matching_results m
            ON m.application_id = a.application_id
        WHERE a.user_id = ?
        ORDER BY a.applied_at DESC
        """,
        (
            user["user_id"],
        )
    ).fetchall()

    # ========================================================
    # REAL RESUME-BASED RECOMMENDATIONS
    # ========================================================

    recommended_jobs = []

    if resumes:

        # Latest uploaded resume
        latest_resume = resumes[0]

        # Convert stored skills into a list
        resume_skills = [
            skill.strip().lower()
            for skill in (
                latest_resume["skills"] or ""
            ).split(",")
            if skill.strip()
        ]

        # Get EVERY job from database
        all_jobs = conn.execute(
            """
            SELECT *
            FROM jobs
            ORDER BY posted_at DESC
            """
        ).fetchall()

        # Compare resume against every job
        for job in all_jobs:

            score, matched, missing = compute_match_score(
                resume_skills,
                job["skills_required"]
            )

            recommended_jobs.append({

                "job": job,

                "score": score,

                "matched_skills": matched,

                "missing_skills": missing

            })

        # Highest match first
        recommended_jobs.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # Display top 6
        recommended_jobs = recommended_jobs[:6]

    conn.close()

    return render_template(
        "jobseeker_dashboard.html",
        resumes=resumes,
        applications=applications,
        recommended_jobs=recommended_jobs
    )


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.route(
    "/resume/upload",
    methods=["GET", "POST"]
)
@login_required(
    role="jobseeker"
)
def upload_resume():

    user = current_user()

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )

        if not file or file.filename == "":

            flash(
                "Please choose a PDF or DOCX resume.",
                "error"
            )

            return redirect(
                url_for("upload_resume")
            )

        if not allowed_file(
            file.filename
        ):

            flash(
                "Only PDF and DOCX files are supported.",
                "error"
            )

            return redirect(
                url_for("upload_resume")
            )

        original_filename = secure_filename(
            file.filename
        )

        timestamp = int(
            datetime.now().timestamp()
        )

        filename = (
            f"user{user['user_id']}_"
            f"{timestamp}_"
            f"{original_filename}"
        )

        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        # ----------------------------------------------------
        # Parse resume
        # ----------------------------------------------------

        parsed_text = extract_text(
            filepath
        )

        if not parsed_text:

            try:
                os.remove(filepath)
            except Exception:
                pass

            flash(
                "Could not read the resume. Please upload a text-based PDF or DOCX file.",
                "error"
            )

            return redirect(
                url_for("upload_resume")
            )

        details = extract_resume_details(
            parsed_text
        )

        skills = details.get(
            "skills",
            []
        )

        education = details.get(
            "education",
            ""
        )

        experience = details.get(
            "experience",
            ""
        )

        certifications = details.get(
            "certifications",
            ""
        )

        # ----------------------------------------------------
        # Store resume
        # ----------------------------------------------------

        conn = get_db()

        conn.execute(
            """
            INSERT INTO resumes
            (
                user_id,
                filename,
                filepath,
                parsed_text,
                skills
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["user_id"],
                original_filename,
                f"uploads/{filename}",
                parsed_text,
                ", ".join(skills)
            )
        )

        conn.commit()
        conn.close()

        print(
            "\n======================================"
        )

        print(
            "RESUME PARSING RESULT"
        )

        print(
            "======================================"
        )

        print(
            "File:",
            original_filename
        )

        print(
            "Skills:",
            ", ".join(skills)
        )

        print(
            "Education:",
            education
        )

        print(
            "Experience:",
            experience
        )

        print(
            "Certifications:",
            certifications
        )

        print(
            "======================================\n"
        )

        flash(
            "Resume uploaded and parsed successfully!",
            "success"
        )

        return redirect(
            url_for(
                "jobseeker_dashboard"
            )
        )

    return render_template(
        "upload_resume.html"
    )


# ============================================================
# APPLY TO JOB
# ============================================================

@app.route(
    "/apply/<int:job_id>",
    methods=["POST"]
)
@login_required(
    role="jobseeker"
)
def apply_to_job(job_id):

    user = current_user()

    resume_id = request.form.get(
        "resume_id"
    )

    conn = get_db()

    if not resume_id:

        conn.close()

        flash(
            "Please upload a resume before applying.",
            "error"
        )

        return redirect(
            url_for("upload_resume")
        )

    # Check duplicate
    existing = conn.execute(
        """
        SELECT 1
        FROM applications
        WHERE job_id = ?
        AND user_id = ?
        """,
        (
            job_id,
            user["user_id"]
        )
    ).fetchone()

    if existing:

        conn.close()

        flash(
            "You have already applied to this job.",
            "error"
        )

        return redirect(
            url_for(
                "job_details",
                job_id=job_id
            )
        )

    # Get job
    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        """,
        (
            job_id,
        )
    ).fetchone()

    # Get resume
    resume = conn.execute(
        """
        SELECT *
        FROM resumes
        WHERE resume_id = ?
        AND user_id = ?
        """,
        (
            resume_id,
            user["user_id"]
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash(
            "That job could not be found.",
            "error"
        )

        return redirect(
            url_for("jobs")
        )

    if resume is None:

        conn.close()

        flash(
            "Please choose one of your own resumes.",
            "error"
        )

        return redirect(
            url_for(
                "job_details",
                job_id=job_id
            )
        )

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    resume_skills = [
        skill.strip().lower()
        for skill in (
            resume["skills"] or ""
        ).split(",")
        if skill.strip()
    ]

    score, matched, missing = compute_match_score(
        resume_skills,
        job["skills_required"]
    )

    # --------------------------------------------------------
    # Create application
    # --------------------------------------------------------

    cursor = conn.execute(
        """
        INSERT INTO applications
        (
            job_id,
            user_id,
            resume_id
        )
        VALUES (?, ?, ?)
        """,
        (
            job_id,
            user["user_id"],
            resume_id
        )
    )

    application_id = cursor.lastrowid

    # --------------------------------------------------------
    # Store matching result
    # --------------------------------------------------------

    conn.execute(
        """
        INSERT INTO matching_results
        (
            application_id,
            resume_id,
            job_id,
            match_score,
            matched_skills,
            missing_skills
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            application_id,
            resume_id,
            job_id,
            score,
            ", ".join(matched),
            ", ".join(missing)
        )
    )

    conn.commit()
    conn.close()

    flash(
        f"Application submitted! Your match score is {score}%.",
        "success"
    )

    return redirect(
        url_for("applications")
    )


# ============================================================
# MY APPLICATIONS
# ============================================================

@app.route(
    "/applications"
)
@login_required(
    role="jobseeker"
)
def applications():

    user = current_user()

    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            a.*,
            j.title,
            j.company,
            j.location,
            j.job_type,
            m.match_score,
            m.matched_skills,
            m.missing_skills
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.job_id
        LEFT JOIN matching_results m
            ON m.application_id = a.application_id
        WHERE a.user_id = ?
        ORDER BY a.applied_at DESC
        """,
        (
            user["user_id"],
        )
    ).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=rows
    )


# ============================================================
# RECRUITER DASHBOARD
# ============================================================

@app.route(
    "/recruiter/dashboard"
)
@login_required(
    role="recruiter"
)
def recruiter_dashboard():

    user = current_user()

    conn = get_db()

    my_jobs = conn.execute(
        """
        SELECT
            j.*,
            COUNT(a.application_id)
            AS applicant_count
        FROM jobs j
        LEFT JOIN applications a
            ON a.job_id = j.job_id
        WHERE j.recruiter_id = ?
        GROUP BY j.job_id
        ORDER BY j.posted_at DESC
        """,
        (
            user["user_id"],
        )
    ).fetchall()

    total_applicants = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.job_id
        WHERE j.recruiter_id = ?
        """,
        (
            user["user_id"],
        )
    ).fetchone()["c"]

    conn.close()

    return render_template(
        "recruiter_dashboard.html",
        jobs=my_jobs,
        total_applicants=total_applicants
    )


# ============================================================
# POST JOB
# ============================================================

@app.route(
    "/recruiter/post-job",
    methods=["GET", "POST"]
)
@login_required(
    role="recruiter"
)
def post_job():

    user = current_user()

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        if not company:

            company = (
                user["company_name"]
                or user["name"]
            )

        location = request.form.get(
            "location",
            ""
        ).strip()

        job_type = request.form.get(
            "job_type",
            ""
        ).strip()

        salary_range = request.form.get(
            "salary_range",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        skills_required = request.form.get(
            "skills_required",
            ""
        ).strip()

        valid_types = {
            "Full-time",
            "Part-time",
            "Internship",
            "Remote"
        }

        if (
            not title
            or not location
            or not description
            or not skills_required
            or job_type not in valid_types
        ):

            flash(
                "Please complete all required job fields.",
                "error"
            )

            return render_template(
                "post_job.html"
            )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO jobs
            (
                recruiter_id,
                title,
                company,
                location,
                job_type,
                salary_range,
                description,
                skills_required
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["user_id"],
                title,
                company,
                location,
                job_type,
                salary_range,
                description,
                skills_required
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Job posted successfully! It is now visible to job seekers.",
            "success"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    return render_template(
        "post_job.html"
    )


# ============================================================
# EDIT JOB
# ============================================================

@app.route(
    "/recruiter/job/<int:job_id>/edit",
    methods=["GET", "POST"]
)
@login_required(
    role="recruiter"
)
def edit_job(job_id):

    user = current_user()

    conn = get_db()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        AND recruiter_id = ?
        """,
        (
            job_id,
            user["user_id"]
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash(
            "Job not found or you do not own this posting.",
            "error"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        if not company:

            company = (
                user["company_name"]
                or user["name"]
            )

        location = request.form.get(
            "location",
            ""
        ).strip()

        job_type = request.form.get(
            "job_type",
            ""
        ).strip()

        salary_range = request.form.get(
            "salary_range",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        skills_required = request.form.get(
            "skills_required",
            ""
        ).strip()

        valid_types = {
            "Full-time",
            "Part-time",
            "Internship",
            "Remote"
        }

        if (
            not title
            or not location
            or not description
            or not skills_required
            or job_type not in valid_types
        ):

            conn.close()

            flash(
                "Please complete all required job fields.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_job",
                    job_id=job_id
                )
            )

        conn.execute(
            """
            UPDATE jobs
            SET
                title = ?,
                company = ?,
                location = ?,
                job_type = ?,
                salary_range = ?,
                description = ?,
                skills_required = ?
            WHERE job_id = ?
            AND recruiter_id = ?
            """,
            (
                title,
                company,
                location,
                job_type,
                salary_range,
                description,
                skills_required,
                job_id,
                user["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Job updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )


# ============================================================
# DELETE JOB
# ============================================================

@app.route(
    "/recruiter/job/<int:job_id>/delete",
    methods=["POST"]
)
@login_required(
    role="recruiter"
)
def delete_job(job_id):

    user = current_user()

    conn = get_db()

    job = conn.execute(
        """
        SELECT job_id
        FROM jobs
        WHERE job_id = ?
        AND recruiter_id = ?
        """,
        (
            job_id,
            user["user_id"]
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash(
            "Job not found or you do not own this posting.",
            "error"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    conn.execute(
        """
        DELETE FROM jobs
        WHERE job_id = ?
        AND recruiter_id = ?
        """,
        (
            job_id,
            user["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Job deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "recruiter_dashboard"
        )
    )


# ============================================================
# VIEW APPLICANTS
# ============================================================

@app.route(
    "/recruiter/job/<int:job_id>/applicants"
)
@login_required(
    role="recruiter"
)
def view_applicants(job_id):

    user = current_user()

    conn = get_db()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE job_id = ?
        AND recruiter_id = ?
        """,
        (
            job_id,
            user["user_id"]
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash(
            "Job not found.",
            "error"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    applicants = conn.execute(
        """
        SELECT
            a.*,
            u.name,
            u.email,
            u.phone,
            r.filename,
            r.filepath,
            m.match_score,
            m.matched_skills,
            m.missing_skills
        FROM applications a
        JOIN users u
            ON a.user_id = u.user_id
        JOIN resumes r
            ON a.resume_id = r.resume_id
        LEFT JOIN matching_results m
            ON m.application_id = a.application_id
        WHERE a.job_id = ?
        ORDER BY m.match_score DESC
        """,
        (
            job_id,
        )
    ).fetchall()

    conn.close()

    return render_template(
        "applicants.html",
        job=job,
        applicants=applicants
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

@app.route(
    "/recruiter/application/<int:application_id>/status",
    methods=["POST"]
)
@login_required(
    role="recruiter"
)
def update_status(application_id):

    new_status = request.form.get(
        "status",
        ""
    )

    valid_statuses = {
        "Pending",
        "Shortlisted",
        "Rejected",
        "Hired"
    }

    if new_status not in valid_statuses:

        flash(
            "Invalid application status.",
            "error"
        )

        return redirect(
            url_for(
                "recruiter_dashboard"
            )
        )

    conn = get_db()

    application = conn.execute(
        """
        SELECT
            a.job_id
        FROM applications a
        JOIN jobs j
            ON a.job_id = j.job_id
        WHERE a.application_id = ?
        AND j.recruiter_id = ?
        """,
        (
            application_id,
            session["user_id"]
        )
    ).fetchone()

    if application:

        conn.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE application_id = ?
            """,
            (
                new_status,
                application_id
            )
        )

        conn.commit()

        job_id = application["job_id"]

        conn.close()

        flash(
            "Application status updated.",
            "success"
        )

        return redirect(
            url_for(
                "view_applicants",
                job_id=job_id
            )
        )

    conn.close()

    flash(
        "Application not found.",
        "error"
    )

    return redirect(
        url_for(
            "recruiter_dashboard"
        )
    )


# ============================================================
# SERVE RESUMES
# ============================================================

@app.route(
    "/static/uploads/<path:filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    init_db_if_needed()

    print()
    print("==============================================")
    print("          SKILLBRIDGE JOB PORTAL")
    print("==============================================")
    print("Server: http://127.0.0.1:5000")
    print("Recommendations: ENABLED")
    print("Search: ENABLED")
    print("Resume matching: ENABLED")
    print("Recruiter job posting: ENABLED")
    print("==============================================")
    print()

    app.run(
        debug=True
    )