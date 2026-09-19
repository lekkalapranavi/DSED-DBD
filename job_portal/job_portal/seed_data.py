from werkzeug.security import generate_password_hash


def run(conn):

    # =========================================================
    # USERS
    # =========================================================

    users = [

        (
            "Ananya Sharma",
            "ananya@technova.com",
            generate_password_hash("password123"),
            "recruiter",
            "TechNova Solutions",
            "9876543210"
        ),

        (
            "Rahul Mehta",
            "rahul@cloudcore.com",
            generate_password_hash("password123"),
            "recruiter",
            "CloudCore Technologies",
            "9876543211"
        ),

        (
            "Sneha Reddy",
            "sneha@dataworks.com",
            generate_password_hash("password123"),
            "recruiter",
            "DataWorks India",
            "9876543212"
        ),

        (
            "Vikram Rao",
            "vikram@fintechlabs.com",
            generate_password_hash("password123"),
            "recruiter",
            "FinTech Labs",
            "9876543213"
        ),

        (
            "Priya Kumar",
            "priya@example.com",
            generate_password_hash("password123"),
            "jobseeker",
            None,
            "9876543214"
        ),

        (
            "System Administrator",
            "admin@jobportal.com",
            generate_password_hash("admin123"),
            "admin",
            None,
            "9876543215"
        )
    ]

    for user in users:

        conn.execute(
            """
            INSERT OR IGNORE INTO users
            (
                name,
                email,
                password_hash,
                role,
                company_name,
                phone
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            user
        )


    # =========================================================
    # GET RECRUITER IDS
    # =========================================================

    recruiters = {}

    for email in [
        "ananya@technova.com",
        "rahul@cloudcore.com",
        "sneha@dataworks.com",
        "vikram@fintechlabs.com"
    ]:

        row = conn.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        recruiters[email] = row["user_id"]


    # =========================================================
    # JOBS
    # =========================================================

    jobs = [

        # -----------------------------------------------------
        # TECHNOVA
        # -----------------------------------------------------

        (
            recruiters["ananya@technova.com"],
            "Python Developer",
            "TechNova Solutions",
            "Hyderabad",
            "Full-time",
            "6-9 LPA",
            "Develop and maintain Python web applications and backend services. Work with the development team to build scalable APIs and database-driven applications.",
            "Python, Flask, SQL, REST API, Git"
        ),

        (
            recruiters["ananya@technova.com"],
            "Frontend Developer",
            "TechNova Solutions",
            "Bangalore",
            "Full-time",
            "5-8 LPA",
            "Build responsive and interactive web interfaces for modern business applications.",
            "HTML, CSS, JavaScript, React, Git"
        ),

        (
            recruiters["ananya@technova.com"],
            "Full Stack Developer",
            "TechNova Solutions",
            "Hyderabad",
            "Full-time",
            "8-12 LPA",
            "Work across frontend and backend technologies to develop complete web applications.",
            "HTML, CSS, JavaScript, React, Python, Flask, SQL"
        ),

        (
            recruiters["ananya@technova.com"],
            "Python Development Intern",
            "TechNova Solutions",
            "Hyderabad",
            "Internship",
            "20K-30K/month",
            "Assist the development team in building Python applications, APIs and database solutions.",
            "Python, Flask, SQL, Git"
        ),

        (
            recruiters["ananya@technova.com"],
            "UI/UX Designer",
            "TechNova Solutions",
            "Bangalore",
            "Full-time",
            "5-8 LPA",
            "Design intuitive user experiences and modern interfaces for web and mobile products.",
            "Figma, Adobe XD, Wireframing, UI/UX"
        ),

        (
            recruiters["ananya@technova.com"],
            "Software Testing Engineer",
            "TechNova Solutions",
            "Pune",
            "Full-time",
            "5-8 LPA",
            "Design and execute software testing processes and identify defects in web applications.",
            "Testing, Java, SQL, Git, Agile"
        ),


        # -----------------------------------------------------
        # CLOUDCORE
        # -----------------------------------------------------

        (
            recruiters["rahul@cloudcore.com"],
            "Cloud Engineer",
            "CloudCore Technologies",
            "Hyderabad",
            "Full-time",
            "8-14 LPA",
            "Design, deploy and maintain cloud infrastructure and scalable application environments.",
            "AWS, Linux, Docker, Git, Python"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "DevOps Engineer",
            "CloudCore Technologies",
            "Bangalore",
            "Full-time",
            "9-15 LPA",
            "Build CI/CD pipelines and automate deployment and infrastructure management.",
            "Docker, Kubernetes, AWS, Linux, Git"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "AWS Intern",
            "CloudCore Technologies",
            "Hyderabad",
            "Internship",
            "20K-35K/month",
            "Learn and assist with cloud infrastructure, deployment and monitoring.",
            "AWS, Linux, Docker, Git"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "Backend Developer",
            "CloudCore Technologies",
            "Chennai",
            "Full-time",
            "7-12 LPA",
            "Develop backend services and REST APIs for cloud-based applications.",
            "Python, Java, REST API, SQL, Docker"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "Kubernetes Engineer",
            "CloudCore Technologies",
            "Bangalore",
            "Full-time",
            "10-16 LPA",
            "Manage containerized applications and Kubernetes-based infrastructure.",
            "Kubernetes, Docker, Linux, AWS"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "Cloud Support Engineer",
            "CloudCore Technologies",
            "Remote",
            "Remote",
            "5-9 LPA",
            "Provide technical support for cloud infrastructure and troubleshoot deployment issues.",
            "AWS, Linux, Python, Communication"
        ),


        # -----------------------------------------------------
        # DATAWORKS
        # -----------------------------------------------------

        (
            recruiters["sneha@dataworks.com"],
            "Data Analyst",
            "DataWorks India",
            "Hyderabad",
            "Full-time",
            "6-10 LPA",
            "Analyze business data and create dashboards and reports to support business decisions.",
            "Python, SQL, Excel, Power BI, Statistics"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "Data Scientist",
            "DataWorks India",
            "Bangalore",
            "Full-time",
            "10-16 LPA",
            "Develop statistical and machine learning models to solve business problems.",
            "Python, Machine Learning, Pandas, NumPy, Statistics"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "Machine Learning Engineer",
            "DataWorks India",
            "Pune",
            "Full-time",
            "10-18 LPA",
            "Build and deploy machine learning models and data pipelines.",
            "Python, Machine Learning, TensorFlow, Pandas, NumPy"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "AI Engineer",
            "DataWorks India",
            "Hyderabad",
            "Full-time",
            "12-20 LPA",
            "Develop artificial intelligence solutions using machine learning and deep learning techniques.",
            "Python, Machine Learning, Deep Learning, TensorFlow"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "Data Analyst Intern",
            "DataWorks India",
            "Hyderabad",
            "Internship",
            "18K-25K/month",
            "Assist analysts in preparing datasets, creating reports and developing dashboards.",
            "Python, SQL, Excel, Power BI"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "Business Intelligence Analyst",
            "DataWorks India",
            "Mumbai",
            "Full-time",
            "7-12 LPA",
            "Create dashboards and business reports using analytical tools.",
            "SQL, Power BI, Excel, Statistics"
        ),


        # -----------------------------------------------------
        # FINTECH LABS
        # -----------------------------------------------------

        (
            recruiters["vikram@fintechlabs.com"],
            "Java Developer",
            "FinTech Labs",
            "Bangalore",
            "Full-time",
            "7-12 LPA",
            "Develop enterprise applications using Java and Spring Boot.",
            "Java, Spring Boot, SQL, REST API, Git"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "Java Backend Engineer",
            "FinTech Labs",
            "Pune",
            "Full-time",
            "8-14 LPA",
            "Build secure and scalable backend services for financial applications.",
            "Java, Spring Boot, SQL, REST API"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "React Developer",
            "FinTech Labs",
            "Mumbai",
            "Full-time",
            "6-11 LPA",
            "Develop high-performance user interfaces for financial applications.",
            "JavaScript, React, HTML, CSS, Git"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "Software Engineer Intern",
            "FinTech Labs",
            "Pune",
            "Internship",
            "20K-30K/month",
            "Work with engineers to develop and test software applications.",
            "Java, Python, SQL, Git"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "QA Automation Engineer",
            "FinTech Labs",
            "Bangalore",
            "Full-time",
            "6-10 LPA",
            "Create automated tests and ensure application quality.",
            "Testing, Java, Python, SQL, Git"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "Cybersecurity Analyst",
            "FinTech Labs",
            "Hyderabad",
            "Full-time",
            "7-13 LPA",
            "Monitor security events and help protect financial applications and systems.",
            "Linux, Testing, Python, Communication"
        ),


        # -----------------------------------------------------
        # GENERAL / REMOTE
        # -----------------------------------------------------

        (
            recruiters["ananya@technova.com"],
            "Web Developer",
            "TechNova Solutions",
            "Chennai",
            "Full-time",
            "5-8 LPA",
            "Develop and maintain responsive websites and web applications.",
            "HTML, CSS, JavaScript, SQL"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "Technical Support Engineer",
            "CloudCore Technologies",
            "Remote",
            "Remote",
            "4-7 LPA",
            "Provide technical assistance to customers and troubleshoot software issues.",
            "Linux, SQL, Communication, Testing"
        ),

        (
            recruiters["sneha@dataworks.com"],
            "Excel Data Analyst",
            "DataWorks India",
            "Delhi",
            "Part-time",
            "25K-40K/month",
            "Analyze operational data and prepare regular reports and dashboards.",
            "Excel, SQL, Statistics, Power BI"
        ),

        (
            recruiters["vikram@fintechlabs.com"],
            "Project Coordinator",
            "FinTech Labs",
            "Mumbai",
            "Full-time",
            "5-9 LPA",
            "Coordinate project activities, schedules and communication between teams.",
            "Project Management, Communication, Agile, Excel"
        ),

        (
            recruiters["ananya@technova.com"],
            "React Developer Intern",
            "TechNova Solutions",
            "Bangalore",
            "Internship",
            "18K-28K/month",
            "Assist frontend engineers in creating React-based web applications.",
            "React, JavaScript, HTML, CSS"
        ),

        (
            recruiters["rahul@cloudcore.com"],
            "Linux System Administrator",
            "CloudCore Technologies",
            "Hyderabad",
            "Full-time",
            "6-10 LPA",
            "Manage Linux servers, troubleshoot system issues and maintain infrastructure.",
            "Linux, AWS, Docker, Testing"
        )

    ]


    # =========================================================
    # INSERT JOBS
    # =========================================================

    for job in jobs:

        # Avoid inserting duplicate demo jobs
        existing = conn.execute(
            """
            SELECT job_id
            FROM jobs
            WHERE title = ?
            AND company = ?
            AND location = ?
            """,
            (
                job[1],
                job[2],
                job[3]
            )
        ).fetchone()

        if not existing:

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
                job
            )


    conn.commit()

    print(
        f"[seed_data] Added {len(jobs)} realistic demo jobs."
    )