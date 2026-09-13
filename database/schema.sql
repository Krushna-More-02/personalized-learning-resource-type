-- ============================================================
-- Personalized Learning Resource System — MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS learning_resource_db;
USE learning_resource_db;

CREATE TABLE students (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    class_grade     VARCHAR(20)  NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subjects (
    subject_id      INT AUTO_INCREMENT PRIMARY KEY,
    subject_name    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE topics (
    topic_id        INT AUTO_INCREMENT PRIMARY KEY,
    subject_id      INT NOT NULL,
    topic_name      VARCHAR(150) NOT NULL,
    topic_weight    DECIMAL(3,2) DEFAULT 1.00,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

CREATE TABLE exams (
    exam_id         INT AUTO_INCREMENT PRIMARY KEY,
    exam_name       VARCHAR(150) NOT NULL,
    subject_id      INT NOT NULL,
    exam_date       DATE NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
);

CREATE TABLE marks (
    mark_id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    topic_id        INT NOT NULL,
    exam_id         INT NOT NULL,
    marks_obtained  DECIMAL(5,2) NOT NULL,
    max_marks       DECIMAL(5,2) NOT NULL,
    recorded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id)   REFERENCES topics(topic_id)     ON DELETE CASCADE,
    FOREIGN KEY (exam_id)    REFERENCES exams(exam_id)       ON DELETE CASCADE
);

CREATE TABLE resources (
    resource_id     INT AUTO_INCREMENT PRIMARY KEY,
    topic_id        INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    resource_type   ENUM('video','article','pdf','practice_set','course') NOT NULL,
    url             VARCHAR(500) NOT NULL,
    difficulty      ENUM('beginner','intermediate','advanced') NOT NULL,
    est_minutes     INT DEFAULT 15,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

CREATE TABLE recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    topic_id        INT NOT NULL,
    resource_id     INT NOT NULL,
    severity        ENUM('critical','weak','moderate') NOT NULL,
    generated_on    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('pending','in_progress','completed') DEFAULT 'pending',
    FOREIGN KEY (student_id)  REFERENCES students(student_id)   ON DELETE CASCADE,
    FOREIGN KEY (topic_id)    REFERENCES topics(topic_id)       ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE
);

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT INTO subjects (subject_name) VALUES ('Mathematics'), ('Physics'), ('English');

INSERT INTO topics (subject_id, topic_name, topic_weight) VALUES
(1, 'Quadratic Equations', 0.9),
(1, 'Trigonometry',        0.8),
(1, 'Probability',         0.6),
(2, 'Newtons Laws of Motion', 0.9),
(2, 'Optics',               0.5),
(3, 'Grammar Fundamentals', 0.7),
(3, 'Essay Writing',        0.6);

INSERT INTO exams (exam_name, subject_id, exam_date) VALUES
('Unit Test 1', 1, '2026-07-10'),
('Unit Test 2', 1, '2026-08-14'),
('Unit Test 1', 2, '2026-07-12'),
('Unit Test 1', 3, '2026-07-15');

-- Demo student: email demo@student.com / password "password123"
INSERT INTO students (full_name, email, password_hash, class_grade) VALUES
('Aarav Sharma', 'demo@student.com', 'PLACEHOLDER_HASH', '10th');

INSERT INTO marks (student_id, topic_id, exam_id, marks_obtained, max_marks) VALUES
(1, 1, 1, 12, 25),
(1, 1, 2, 10, 25),
(1, 2, 1, 20, 25),
(1, 3, 1, 15, 25),
(1, 4, 3, 22, 25),
(1, 5, 3, 9,  25),
(1, 6, 4, 18, 25),
(1, 7, 4, 13, 25);

INSERT INTO resources (topic_id, title, resource_type, url, difficulty, est_minutes) VALUES
(1, 'Quadratic Equations — Visual Introduction', 'video', 'https://example.com/quad-intro', 'beginner', 12),
(1, 'Solving Quadratics by Factoring — Practice Set', 'practice_set', 'https://example.com/quad-practice', 'beginner', 25),
(1, 'Quadratic Formula Deep Dive', 'article', 'https://example.com/quad-formula', 'intermediate', 15),
(3, 'Probability Basics Explained', 'video', 'https://example.com/prob-basics', 'beginner', 10),
(3, 'Probability Practice Problems', 'practice_set', 'https://example.com/prob-practice', 'intermediate', 20),
(5, 'Optics 101 — Reflection & Refraction', 'video', 'https://example.com/optics-101', 'beginner', 14),
(5, 'Ray Diagrams Walkthrough', 'article', 'https://example.com/ray-diagrams', 'beginner', 10),
(7, 'Essay Writing Structure Guide', 'article', 'https://example.com/essay-structure', 'beginner', 12),
(7, 'Essay Writing Practice Prompts', 'practice_set', 'https://example.com/essay-prompts', 'intermediate', 20);