import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path('assessment.db')

@contextmanager
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with get_db() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS groups_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            qualification TEXT NOT NULL DEFAULT '',
            academic_year TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_no TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            group_id INTEGER,
            FOREIGN KEY(group_id) REFERENCES groups_table(id)
        );
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            module_name TEXT NOT NULL DEFAULT '',
            learning_outcome TEXT NOT NULL DEFAULT '',
            criterion TEXT NOT NULL DEFAULT '',
            teacher_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question_no INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            question_type TEXT NOT NULL DEFAULT 'mcq',
            correct_answer TEXT NOT NULL,
            points REAL NOT NULL DEFAULT 1,
            FOREIGN KEY(assessment_id) REFERENCES assessments(id)
        );
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            student_id INTEGER,
            source_file TEXT,
            score REAL NOT NULL DEFAULT 0,
            max_score REAL NOT NULL DEFAULT 0,
            percent REAL NOT NULL DEFAULT 0,
            correct_count INTEGER NOT NULL DEFAULT 0,
            wrong_count INTEGER NOT NULL DEFAULT 0,
            blank_count INTEGER NOT NULL DEFAULT 0,
            needs_review TEXT NOT NULL DEFAULT '',
            approved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(assessment_id) REFERENCES assessments(id),
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''')
