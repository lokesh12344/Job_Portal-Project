from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os
import models
import requests  # Add this import

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure database exists
if not os.path.exists('database.db'):
    with app.app_context():
        models.init_db()

@app.teardown_appcontext
def close_connection(exception):
    models.close_db()

# Jobicy API integration
def fetch_remote_jobs(count=10):
    """
    Fetches remote jobs from the Jobicy API.

    Args:
        count (int): Number of jobs to fetch.
    Returns:
        list: List of remote jobs (dicts) or empty list on error.
    """
    url = "https://jobicy.com/api/v2/remote-jobs"
    params = {"count": count}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("jobs", [])
    except requests.exceptions.RequestException:
        return []

@app.route('/')
def index():
    jobs = models.get_all_jobs()
    # Mock-up jobs
    mock_jobs = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Solutions',
            'location': 'Bengaluru, Karnataka',
            'salary': '₹15,00,000/year',
        },
        {
            'title': 'Data Analyst',
            'company': 'DataCorp',
            'location': 'Hyderabad, Telangana',
            'salary': '₹10,00,000/year',
        },
        {
            'title': 'Frontend Developer',
            'company': 'WebWorks',
            'location': 'Pune, Maharashtra',
            'salary': '₹12,00,000/year',
        },
        {
            'title': 'Digital Marketing Specialist',
            'company': 'MarketGenius',
            'location': 'Mumbai, Maharashtra',
            'salary': '₹9,00,000/year',
        },
        {
            'title': 'AI Creator',
            'company': 'InnovateAI',
            'location': 'Gurugram, Haryana',
            'salary': '₹18,00,000/year',
        },
    ]
    return render_template('index.html', jobs=jobs, mock_jobs=mock_jobs)

# NEW ROUTE FOR REMOTE JOBS
@app.route('/remote-jobs')
def remote_jobs():
    jobs = fetch_remote_jobs(10)
    if jobs:
        print('First job object:', jobs[0])  # Debug: print the first job dict to terminal
    return render_template('remote_jobs.html', jobs=jobs)

@app.route('/jobs')
def jobs():
    jobs = models.get_all_jobs()
    return render_template('jobs/list.html', jobs=jobs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role')
        user = models.get_user_by_email(email)
        if user and user['password'] == password and user['role'] == role:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to home after login
        else:
            flash('Invalid email, password, or role', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        if models.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')
        if models.register_user(username, email, password, role):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    """
    Logs out the current user by clearing the session.
    Redirects to the login page.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = models.get_user_by_id(session['user_id'])
    if user['role'] == 'admin':
        # Admin: manage users & jobs
        return render_template('dashboard/admin.html')
    elif user['role'] == 'employer':
        # Employer: post jobs, manage listings
        jobs = models.get_jobs_by_employer(user['id'])
        return render_template('dashboard/employer.html', jobs=jobs)
    else:
        # Seeker: view applications
        applications = models.get_applications_by_seeker(user['id'])
        return render_template('dashboard/seeker.html', applications=applications)

@app.route('/jobs/create', methods=['GET', 'POST'])
def create_job():
    if not session.get('user_id') or session.get('role') != 'employer':
        flash('Only employers can post jobs.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        salary = request.form.get('salary', '')
        category = 'General'
        employer_id = session['user_id']
        models.create_job(title, description, 'Your Company', location, salary, category, employer_id)
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('jobs/create.html')

@app.route('/jobs/detail/<int:job_id>')
def job_detail(job_id):
    job = models.get_job_by_id(job_id)
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('jobs/detail.html', job=job)

@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if not session.get('user_id') or session.get('role') != 'employer':
        flash('Only employers can delete jobs.', 'danger')
        return redirect(url_for('index'))
    job = models.get_job_by_id(job_id)
    if not job or job['employer_id'] != session['user_id']:
        flash('You can only delete your own jobs.', 'danger')
        return redirect(url_for('index'))
    models.delete_job(job_id)
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
