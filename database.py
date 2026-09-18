"""
Модуль работы с базой данных SQLite.
"""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lab_works.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    first_run = not os.path.exists(DB_PATH)
    conn = get_connection()
    cur = conn.cursor()

    if first_run:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
        conn.commit()
        _insert_demo_data(conn)
        print("[db] База данных создана и заполнена демо-данными.")
    else:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        if cur.fetchone() is None:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                cur.executescript(f.read())
            conn.commit()
            _insert_demo_data(conn)
            print("[db] Таблицы пересозданы.")

    conn.close()


def _insert_demo_data(conn):
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    students = [
        ("Алексеева Мария", "ИС-21", now),
        ("Иванов Никита", "ИС-21", now),
        ("Петрова Анна", "ИС-22", now),
        ("Сидоров Пётр", "ИС-22", now),
    ]
    cur.executemany(
        "INSERT INTO students (full_name, group_name, created_at) VALUES (?, ?, ?)",
        students,
    )

    labs = [
        ("Лабораторная работа №1", "Программирование", 10, "2026-05-01"),
        ("Лабораторная работа №2", "Базы данных", 8, "2026-05-15"),
    ]
    cur.executemany(
        "INSERT INTO lab_works (title, subject, max_score, deadline) VALUES (?, ?, ?, ?)",
        labs,
    )

    submissions = [
        (1, 1, now, 5, "checked", "Работа принята"),
        (2, 1, now, None, "submitted", "Сдана на проверку"),
        (3, 2, now, 3, "revision", "Нужно исправить вывод"),
    ]
    cur.executemany(
        """INSERT INTO submissions
           (student_id, lab_work_id, submitted_at, score, status, comment)
           VALUES (?, ?, ?, ?, ?, ?)""",
        submissions,
    )
    conn.commit()


def get_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY group_name, full_name").fetchall()
    conn.close()
    return rows


def add_student(full_name, group_name):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (full_name, group_name, created_at) VALUES (?, ?, ?)",
        (full_name, group_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def count_students():
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return n


def get_labs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM lab_works ORDER BY id").fetchall()
    conn.close()
    return rows


def add_lab(title, subject, max_score, deadline):
    conn = get_connection()
    conn.execute(
        "INSERT INTO lab_works (title, subject, max_score, deadline) VALUES (?, ?, ?, ?)",
        (title, subject, int(max_score), deadline),
    )
    conn.commit()
    conn.close()


def count_labs():
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM lab_works").fetchone()[0]
    conn.close()
    return n


def get_submissions(status=None, group=None):
    query = """
        SELECT
            submissions.id            AS id,
            students.full_name        AS full_name,
            students.group_name       AS group_name,
            lab_works.title           AS title,
            lab_works.subject         AS subject,
            lab_works.deadline        AS deadline,
            lab_works.max_score       AS max_score,
            submissions.submitted_at  AS submitted_at,
            submissions.score         AS score,
            submissions.status        AS status,
            submissions.comment       AS comment
        FROM submissions
        JOIN students  ON students.id  = submissions.student_id
        JOIN lab_works ON lab_works.id = submissions.lab_work_id
        WHERE 1 = 1
    """
    params = []

    if status:
        query += " AND submissions.status = ?"
        params.append(status)

    if group:
        query += " AND students.group_name = ?"
        params.append(group)

    query += " ORDER BY submissions.id DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def add_submission(student_id, lab_work_id, comment):
    conn = get_connection()
    conn.execute(
        """INSERT INTO submissions
           (student_id, lab_work_id, submitted_at, score, status, comment)
           VALUES (?, ?, ?, NULL, 'submitted', ?)""",
        (int(student_id), int(lab_work_id),
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), comment or None),
    )
    conn.commit()
    conn.close()


def check_submission(submission_id, score, comment):
    conn = get_connection()
    conn.execute(
        """UPDATE submissions
           SET score = ?, status = 'checked', comment = ?
           WHERE id = ?""",
        (int(score), comment or None, int(submission_id)),
    )
    conn.commit()
    conn.close()


def send_to_revision(submission_id, comment=None):
    conn = get_connection()
    conn.execute(
        """UPDATE submissions
           SET status = 'revision', comment = ?
           WHERE id = ?""",
        (comment or None, int(submission_id)),
    )
    conn.commit()
    conn.close()


def count_by_status(status):
    conn = get_connection()
    n = conn.execute(
        "SELECT COUNT(*) FROM submissions WHERE status = ?", (status,)
    ).fetchone()[0]
    conn.close()
    return n