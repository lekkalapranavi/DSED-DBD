import sqlite3

DB_NAME = "job_portal.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


def show_table(title, query, columns):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    print(" | ".join(f"{col:<20}" for col in columns))
    print("-" * 100)

    rows = cursor.execute(query).fetchall()

    if not rows:
        print("No records found.")
    else:
        for row in rows:
            values = []
            for value in row:
                text = str(value) if value is not None else "NULL"
                text = text.replace("\n", " ")[:20]
                values.append(f"{text:<20}")
            print(" | ".join(values))

    print(f"\nTotal records: {len(rows)}")


print("\n")
print("╔" + "═" * 98 + "╗")
print("║" + "SKILLBRIDGE JOB PORTAL - DATABASE VIEWER".center(98) + "║")
print("╚" + "═" * 98 + "╝")


# USERS
show_table(
    "1. USERS",
    """
    SELECT user_id, name, email, role, company_name
    FROM users
    """,
    ["ID", "Name", "Email", "Role", "Company"]
)


# JOBS
show_table(
    "2. JOBS",
    """
    SELECT job_id, title, company, location, job_type, skills_required
    FROM jobs
    """,
    ["ID", "Title", "Company", "Location", "Type", "Required Skills"]
)


# RESUMES
show_table(
    "3. RESUMES",
    """
    SELECT resume_id, user_id, filename, skills
    FROM resumes
    """,
    ["ID", "User ID", "Filename", "Detected Skills"]
)


# APPLICATIONS
show_table(
    "4. APPLICATIONS",
    """
    SELECT application_id, job_id, user_id, resume_id, status
    FROM applications
    """,
    ["ID", "Job ID", "User ID", "Resume ID", "Status"]
)


# MATCHING RESULTS
show_table(
    "5. MATCHING RESULTS",
    """
    SELECT application_id, match_score, matched_skills, missing_skills
    FROM matching_results
    """,
    ["Application", "Score", "Matched Skills", "Missing Skills"]
)


print("\n" + "=" * 100)
print("DATABASE VIEW COMPLETE")
print("=" * 100)

conn.close()