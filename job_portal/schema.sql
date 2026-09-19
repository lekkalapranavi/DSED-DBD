DROP TABLE IF EXISTS matching_results;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS resumes;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('jobseeker', 'recruiter', 'admin')),
    company_name TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    parsed_text TEXT,
    skills TEXT,
    education TEXT,
    experience TEXT,
    certifications TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recruiter_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,

    job_type TEXT NOT NULL
        CHECK (job_type IN ('Full-time','Part-time','Internship','Remote')),

    salary_range TEXT,
    description TEXT NOT NULL,
    skills_required TEXT NOT NULL,

    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (recruiter_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    resume_id INTEGER NOT NULL,

    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending','Shortlisted','Rejected','Hired')),

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (resume_id)
        REFERENCES resumes(resume_id)
        ON DELETE CASCADE,

    UNIQUE(job_id, user_id)
);

CREATE TABLE matching_results (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,

    application_id INTEGER NOT NULL UNIQUE,
    resume_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,

    match_score REAL NOT NULL,

    matched_skills TEXT,
    missing_skills TEXT,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE,

    FOREIGN KEY (resume_id)
        REFERENCES resumes(resume_id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_id)
        REFERENCES jobs(job_id)
        ON DELETE CASCADE
);