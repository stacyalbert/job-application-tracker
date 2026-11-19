-- Job Application Tracker schema
DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

CREATE TABLE companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
);

CREATE TABLE jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT NOT NULL,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT NOT NULL,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE
);

CREATE TABLE contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

-- Sample data
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp', 'Technology', 'https://www.techcorp.example.com', 'Miami', 'Florida', 'Referred by a professor'),
('DataCo', 'Analytics', 'https://www.dataco.example.com', 'Orlando', 'Florida', 'Hybrid work'),
('CyberShield', 'Cybersecurity', 'https://www.cybershield.example.com', 'Tampa', 'Florida', 'Strong internship program'),
('CloudNine Systems', 'Cloud Computing', 'https://www.cloudnine.example.com', 'Austin', 'Texas', 'Fully remote'),
('HealthFirst Tech', 'Healthcare IT', 'https://www.healthfirst.example.com', 'Atlanta', 'Georgia', NULL);

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer', 'Full-time', 70000, 95000, 'https://www.techcorp.example.com/jobs/1', '2026-10-01', '["Python","SQL","Flask"]'),
(2, 'Data Analyst', 'Full-time', 60000, 80000, 'https://www.dataco.example.com/jobs/2', '2026-10-03', '["Python","SQL","Tableau"]'),
(3, 'Security Analyst', 'Full-time', 75000, 100000, 'https://www.cybershield.example.com/jobs/3', '2026-10-05', '["Python","Networking","SIEM","Linux"]'),
(3, 'Cybersecurity Intern', 'Internship', 20000, 28000, 'https://www.cybershield.example.com/jobs/4', '2026-10-06', '["Linux","Networking","Python"]'),
(4, 'Cloud Engineer', 'Full-time', 85000, 115000, 'https://www.cloudnine.example.com/jobs/5', '2026-10-08', '["AWS","Python","Linux","Docker"]'),
(4, 'DevOps Intern', 'Internship', 22000, 30000, 'https://www.cloudnine.example.com/jobs/6', '2026-10-10', '["Docker","Git","Linux"]'),
(5, 'Backend Developer', 'Contract', 65000, 90000, 'https://www.healthfirst.example.com/jobs/7', '2026-10-12', '["Python","Flask","SQL","MySQL"]'),
(2, 'Junior Data Engineer', 'Full-time', 68000, 88000, 'https://www.dataco.example.com/jobs/8', '2026-10-15', '["Python","SQL","ETL","AWS"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-10-05', 'Interview', 'v2', TRUE, '{"rounds": [{"type": "Phone screen", "date": "2026-10-15"}], "notes": "Asked about Flask projects"}'),
(2, '2026-10-07', 'Applied', 'v2', FALSE, NULL),
(4, '2026-10-09', 'Screening', 'v3', TRUE, '{"rounds": [], "notes": "Recruiter emailed"}'),
(5, '2026-10-12', 'Rejected', 'v2', TRUE, NULL),
(7, '2026-10-14', 'Offer', 'v3', TRUE, '{"rounds": [{"type": "Technical", "date": "2026-10-22"}], "notes": "Offer pending response"}'),
(3, '2026-10-18', 'Applied', 'v3', FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Maria Lopez', 'Technical Recruiter', 'maria.lopez@techcorp.example.com', '305-555-0101', 'https://www.linkedin.com/in/example-maria', 'Met at career fair'),
(2, 'James Carter', 'Hiring Manager', 'james.carter@dataco.example.com', '407-555-0102', NULL, NULL),
(3, 'Priya Nair', 'Engineering Lead', 'priya.nair@cybershield.example.com', '813-555-0103', 'https://www.linkedin.com/in/example-priya', 'Alumni connection'),
(4, 'Daniel Kim', 'Recruiter', 'daniel.kim@cloudnine.example.com', '512-555-0104', NULL, NULL),
(5, 'Sofia Reyes', 'HR Coordinator', 'sofia.reyes@healthfirst.example.com', '404-555-0105', NULL, 'Sent offer details');