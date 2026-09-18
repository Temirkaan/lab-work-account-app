-- Схема базы данных для системы учёта лабораторных работ

DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS lab_works;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name  TEXT NOT NULL,
    group_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE lab_works (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT NOT NULL,
    subject   TEXT NOT NULL,
    max_score INTEGER NOT NULL DEFAULT 10,
    deadline  TEXT
);

CREATE TABLE submissions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   INTEGER NOT NULL,
    lab_work_id  INTEGER NOT NULL,
    submitted_at TEXT NOT NULL,
    score        INTEGER,
    status       TEXT NOT NULL DEFAULT 'submitted'
                 CHECK (status IN ('submitted', 'checked', 'revision')),
    comment      TEXT,
    FOREIGN KEY (student_id)  REFERENCES students(id)  ON DELETE CASCADE,
    FOREIGN KEY (lab_work_id) REFERENCES lab_works(id) ON DELETE CASCADE
);