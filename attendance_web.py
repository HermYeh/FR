'''
Attendance Database Web Interface
Flask-based web application for attendance management
'''

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
import os
from attendance_database import AttendanceDatabase

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Global database instance
db = None

def get_db():
    """Get database instance"""
    global db
    if db is None:
        db = AttendanceDatabase()
    return db

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with summary"""
    db = get_db()
    summary = db.get_daily_summary()
    recent_records = db.get_attendance_report()[:10]
    employees = db.get_employees()
    
    return render_template('dashboard.html', 
                         summary=summary, 
                         recent_records=recent_records,
                         employees=employees)

@app.route('/check_in', methods=['GET', 'POST'])
def check_in():
    """Check in page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            db = get_db()
            if db.check_in(name):
                flash(f'{name} checked in successfully!', 'success')
            else:
                flash(f'{name} already checked in today or error occurred.', 'error')
        else:
            flash('Name is required.', 'error')
        return redirect(url_for('check_in'))
    
    return render_template('check_in.html')

@app.route('/check_out', methods=['GET', 'POST'])
def check_out():
    """Check out page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            db = get_db()
            if db.check_out(name):
                flash(f'{name} checked out successfully!', 'success')
            else:
                flash(f'No check-in record found for {name} today.', 'error')
        else:
            flash('Name is required.', 'error')
        return redirect(url_for('check_out'))
    
    return render_template('check_out.html')

@app.route('/employees')
def employees():
    """Employees list page"""
    db = get_db()
    employees = db.get_employees()
    return render_template('employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    """Add employee page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()
        
        if name:
            db = get_db()
            if db.add_employee(name, employee_id, department, position):
                flash(f'Employee {name} added successfully!', 'success')
            else:
                flash(f'Employee {name} already exists.', 'error')
        else:
            flash('Name is required.', 'error')
        return redirect(url_for('employees'))
    
    return render_template('add_employee.html')

@app.route('/reports')
def reports():
    """Reports page"""
    db = get_db()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    employee = request.args.get('employee', '')
    
    records = db.get_attendance_report(
        start_date if start_date else None,
        end_date if end_date else None,
        employee if employee else None
    )
    
    return render_template('reports.html', records=records)

@app.route('/api/check_in', methods=['POST'])
def api_check_in():
    """API endpoint for check-in"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'})
    
    db = get_db()
    if db.check_in(name):
        return jsonify({'success': True, 'message': f'{name} checked in successfully!'})
    else:
        return jsonify({'success': False, 'message': f'{name} already checked in today'})

@app.route('/api/check_out', methods=['POST'])
def api_check_out():
    """API endpoint for check-out"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required'})
    
    db = get_db()
    if db.check_out(name):
        return jsonify({'success': True, 'message': f'{name} checked out successfully!'})
    else:
        return jsonify({'success': False, 'message': f'No check-in record found for {name} today'})

@app.route('/api/summary')
def api_summary():
    """API endpoint for daily summary"""
    db = get_db()
    summary = db.get_daily_summary()
    return jsonify(summary)


def create_templates():
    """Create basic HTML templates"""
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Attendance Database{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; }
        .card { margin-bottom: 20px; }
        .alert { margin-top: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Attendance System</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/dashboard">Dashboard</a>
                <a class="nav-link" href="/check_in">Check In</a>
                <a class="nav-link" href="/check_out">Check Out</a>
                <a class="nav-link" href="/employees">Employees</a>
                <a class="nav-link" href="/reports">Reports</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''

    # Index template
    index_template = '''{% extends "base.html" %}
{% block title %}Home - Attendance Database{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1 class="mb-4">Welcome to Attendance Database System</h1>
        <p class="lead">Manage employee attendance with ease.</p>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Quick Check In</h5>
                <p class="card-text">Record employee check-ins</p>
                <a href="/check_in" class="btn btn-primary">Check In</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Quick Check Out</h5>
                <p class="card-text">Record employee check-outs</p>
                <a href="/check_out" class="btn btn-success">Check Out</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">View Reports</h5>
                <p class="card-text">Generate attendance reports</p>
                <a href="/reports" class="btn btn-info">Reports</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard - Attendance Database{% endblock %}

{% block content %}
<h1 class="mb-4">Dashboard</h1>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Daily Summary</h5>
            </div>
            <div class="card-body">
                <p><strong>Date:</strong> {{ summary.date }}</p>
                <p><strong>Total Employees:</strong> {{ summary.total_employees }}</p>
                <p><strong>Present:</strong> {{ summary.present_employees }}</p>
                <p><strong>Absent:</strong> {{ summary.absent_employees }}</p>
                <p><strong>Attendance Rate:</strong> {{ "%.1f"|format(summary.attendance_rate) }}%</p>
                <p><strong>Average Hours:</strong> {{ summary.average_hours }}</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Recent Activity</h5>
            </div>
            <div class="card-body">
                {% if recent_records %}
                    {% for record in recent_records %}
                        <div class="mb-2">
                            <strong>{{ record.name }}</strong> - {{ record.date }}<br>
                            <small>Check-in: {{ record.check_in_time or 'N/A' }} | 
                                   Check-out: {{ record.check_out_time or 'N/A' }}</small>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>No recent activity</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Check-in template
    check_in_template = '''{% extends "base.html" %}
{% block title %}Check In - Attendance Database{% endblock %}

{% block content %}
<h1 class="mb-4">Check In</h1>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Manual Check In</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Employee Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Check In</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Check-out template
    check_out_template = '''{% extends "base.html" %}
{% block title %}Check Out - Attendance Database{% endblock %}

{% block content %}
<h1 class="mb-4">Check Out</h1>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Manual Check Out</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Employee Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <button type="submit" class="btn btn-success">Check Out</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Employees template
    employees_template = '''{% extends "base.html" %}
{% block title %}Employees - Attendance Database{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>Employees</h1>
    <a href="/add_employee" class="btn btn-primary">Add Employee</a>
</div>

<div class="card">
    <div class="card-header">
        <h5 class="card-title mb-0">Employee List</h5>
    </div>
    <div class="card-body">
        {% if employees %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Employee ID</th>
                            <th>Department</th>
                            <th>Position</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for emp in employees %}
                        <tr>
                            <td>{{ emp.name }}</td>
                            <td>{{ emp.employee_id or 'N/A' }}</td>
                            <td>{{ emp.department or 'N/A' }}</td>
                            <td>{{ emp.position or 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p>No employees found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}'''

    # Add employee template
    add_employee_template = '''{% extends "base.html" %}
{% block title %}Add Employee - Attendance Database{% endblock %}

{% block content %}
<h1 class="mb-4">Add Employee</h1>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Employee Information</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Name *</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="employee_id" class="form-label">Employee ID</label>
                        <input type="text" class="form-control" id="employee_id" name="employee_id">
                    </div>
                    <div class="mb-3">
                        <label for="department" class="form-label">Department</label>
                        <input type="text" class="form-control" id="department" name="department">
                    </div>
                    <div class="mb-3">
                        <label for="position" class="form-label">Position</label>
                        <input type="text" class="form-control" id="position" name="position">
                    </div>
                    <button type="submit" class="btn btn-primary">Add Employee</button>
                    <a href="/employees" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Reports template
    reports_template = '''{% extends "base.html" %}
{% block title %}Reports - Attendance Database{% endblock %}

{% block content %}
<h1 class="mb-4">Attendance Reports</h1>

<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">Filter Options</h5>
            </div>
            <div class="card-body">
                <form method="GET" class="row">
                    <div class="col-md-3">
                        <label for="start_date" class="form-label">Start Date</label>
                        <input type="date" class="form-control" id="start_date" name="start_date" 
                               value="{{ request.args.get('start_date', '') }}">
                    </div>
                    <div class="col-md-3">
                        <label for="end_date" class="form-label">End Date</label>
                        <input type="date" class="form-control" id="end_date" name="end_date"
                               value="{{ request.args.get('end_date', '') }}">
                    </div>
                    <div class="col-md-3">
                        <label for="employee" class="form-label">Employee</label>
                        <input type="text" class="form-control" id="employee" name="employee"
                               value="{{ request.args.get('employee', '') }}">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">&nbsp;</label>
                        <button type="submit" class="btn btn-primary d-block">Filter</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h5 class="card-title mb-0">Attendance Records ({{ records|length }} records)</h5>
    </div>
    <div class="card-body">
        {% if records %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Date</th>
                            <th>Check In</th>
                            <th>Check Out</th>
                            <th>Total Hours</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for record in records %}
                        <tr>
                            <td>{{ record.name }}</td>
                            <td>{{ record.date }}</td>
                            <td>{{ record.check_in_time or 'N/A' }}</td>
                            <td>{{ record.check_out_time or 'N/A' }}</td>
                            <td>{{ record.total_hours or 'N/A' }}</td>
                            <td>{{ record.status }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p>No records found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}'''

    # Write templates to files
    templates = {
        'base.html': base_template,
        'index.html': index_template,
        'dashboard.html': dashboard_template,
        'check_in.html': check_in_template,
        'check_out.html': check_out_template,
        'employees.html': employees_template,
        'add_employee.html': add_employee_template,
        'reports.html': reports_template
    }
    
    for filename, content in templates.items():
        with open(f'templates/{filename}', 'w') as f:
            f.write(content) 

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create basic templates
    create_templates()
    
    print("Starting Attendance Database Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
