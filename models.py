# Database interaction functions
# models.py

import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    '''Connect to the database.'''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    '''Close the database connection.'''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    '''Initialize the database with schema.'''
    with open('schema.sql', 'r') as f:
        get_db().executescript(f.read())
    get_db().commit()

# User model functions
def register_user(username, email, password, role):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
            (username, email, password, role)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_email(email):
    cursor = get_db().cursor()
    user = cursor.execute(
        'SELECT * FROM users WHERE email = ?',
        (email,)
    ).fetchone()
    return user

def get_user_by_id(user_id):
    cursor = get_db().cursor()
    user = cursor.execute(
        'SELECT * FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    return user

# Job model functions
def create_job(title, description, company, location, salary, category, employer_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO jobs (title, description, company, location, salary, category, employer_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (title, description, company, location, salary, category, employer_id)
    )
    db.commit()
    return cursor.lastrowid

def get_all_jobs():
    cursor = get_db().cursor()
    jobs = cursor.execute(
        'SELECT j.*, u.username as employer_name FROM jobs j JOIN users u ON j.employer_id = u.id ORDER BY j.created_at DESC'
    ).fetchall()
    return jobs

def get_job_by_id(job_id):
    cursor = get_db().cursor()
    job = cursor.execute(
        'SELECT j.*, u.username as employer_name FROM jobs j JOIN users u ON j.employer_id = u.id WHERE j.id = ?',
        (job_id,)
    ).fetchone()
    return job

def get_applications_by_seeker(seeker_id):
    cursor = get_db().cursor()
    applications = cursor.execute(
        'SELECT a.*, j.title as job_title FROM applications a JOIN jobs j ON a.job_id = j.id WHERE a.seeker_id = ? ORDER BY a.created_at DESC',
        (seeker_id,)
    ).fetchall()
    return applications

def get_jobs_by_employer(employer_id):
    cursor = get_db().cursor()
    jobs = cursor.execute(
        'SELECT * FROM jobs WHERE employer_id = ? ORDER BY created_at DESC',
        (employer_id,)
    ).fetchall()
    return jobs

def delete_job(job_id):
    db = get_db()
    db.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    db.commit()
