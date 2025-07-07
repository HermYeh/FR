# Attendance Database System

A comprehensive attendance tracking system with SQLite backend, supporting check-in/check-out functionality, employee management, and reporting.

## Features

- **Employee Management**: Add, list, and manage employees
- **Check-in/Check-out**: Record employee attendance with timestamps
- **Automatic Hours Calculation**: Calculate total hours worked
- **Reporting**: Generate attendance reports with filtering options
- **Data Import/Export**: Import from existing CSV files, export to CSV
- **Multiple Interfaces**: Command-line, interactive CLI, and web interface
- **Daily Summaries**: View attendance statistics and summaries

## Database Schema

### Attendance Table
- `id`: Primary key
- `name`: Employee name
- `date`: Attendance date (YYYY-MM-DD)
- `check_in_time`: Check-in timestamp
- `check_out_time`: Check-out timestamp
- `total_hours`: Calculated hours worked
- `status`: Attendance status (present, absent, etc.)
- `created_at`: Record creation timestamp

### Employees Table
- `id`: Primary key
- `name`: Employee name (unique)
- `employee_id`: Employee ID (unique)
- `department`: Department name
- `position`: Job position
- `is_active`: Active status
- `created_at`: Record creation timestamp

## Installation

1. **Install Dependencies**:
   ```bash
   pip install flask pandas
   ```

2. **Run the System**:
   - For command-line interface: `python attendance_cli.py --interactive`
   - For web interface: `python attendance_web.py`
   - For direct database operations: `python attendance_database.py`

## Usage

### Command Line Interface

#### Interactive Mode
```bash
python attendance_cli.py --interactive
```

#### Direct Commands
```bash
# Check in an employee
python attendance_cli.py --check-in "John Doe"

# Check out an employee
python attendance_cli.py --check-out "John Doe"

# Show daily summary
python attendance_cli.py --summary

# Show attendance report
python attendance_cli.py --report

# Add employee
python attendance_cli.py --add-employee "John Doe"

# List employees
python attendance_cli.py --list-employees

# Import from CSV
python attendance_cli.py --import-csv "data.csv"

# Export to CSV
python attendance_cli.py --export-csv "output.csv"

# Show employee history
python attendance_cli.py --employee-history "John Doe" --days 30
```

### Web Interface

1. **Start the web server**:
   ```bash
   python attendance_web.py
   ```

2. **Open your browser** and go to: `http://localhost:5000`

3. **Available pages**:
   - **Dashboard**: Overview with daily summary and recent activity
   - **Check In**: Record employee check-ins
   - **Check Out**: Record employee check-outs
   - **Employees**: Manage employee list
   - **Reports**: Generate filtered attendance reports

### Direct Database Operations

```python
from attendance_database import AttendanceDatabase

# Initialize database
db = AttendanceDatabase()

# Add employee
db.add_employee("John Doe", "EMP001", "Engineering", "Developer")

# Check in
db.check_in("John Doe")

# Check out
db.check_out("John Doe")

# Get daily summary
summary = db.get_daily_summary()

# Get attendance report
records = db.get_attendance_report()

# Import from existing CSV
db.import_from_csv("20250704_register_log.csv")

# Export to CSV
db.export_to_csv("attendance_report.csv")
```

## Importing Existing Data

The system can import data from your existing CSV files:

```bash
# Import from existing log files
python attendance_cli.py --import-csv "20250704_register_log.csv"
python attendance_cli.py --import-csv "20250705_register_log.csv"
```

The import function will:
- Parse the existing datetime format
- Create check-in records for each unique person per day
- Handle "Unknown" entries appropriately
- Maintain data integrity

## API Endpoints (Web Interface)

### REST API
- `POST /api/check_in`: Check in an employee
- `POST /api/check_out`: Check out an employee
- `GET /api/summary`: Get daily summary

### Example API Usage
```javascript
// Check in
fetch('/api/check_in', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'John Doe'})
});

// Get summary
fetch('/api/summary')
    .then(response => response.json())
    .then(data => console.log(data));
```

## File Structure

```
attendance_database.py      # Core database functionality
attendance_cli.py          # Command-line interface
attendance_web.py          # Web interface
templates/                 # HTML templates (auto-generated)
├── base.html
├── index.html
├── dashboard.html
├── check_in.html
├── check_out.html
├── employees.html
├── add_employee.html
└── reports.html
attendance.db              # SQLite database (auto-created)
```

## Database Operations

### Adding Employees
```python
db.add_employee("John Doe", "EMP001", "Engineering", "Developer")
```

### Check-in/Check-out
```python
# Check in (automatic timestamp)
db.check_in("John Doe")

# Check out (automatic timestamp and hours calculation)
db.check_out("John Doe")
```

### Reporting
```python
# Get all records
records = db.get_attendance_report()

# Get filtered records
records = db.get_attendance_report(
    start_date="2025-01-01",
    end_date="2025-01-31",
    employee_name="John Doe"
)

# Get daily summary
summary = db.get_daily_summary("2025-01-15")

# Get employee history
history = db.get_employee_attendance("John Doe", days=30)
```

## Integration with Face Recognition

The attendance database can be integrated with your existing face recognition system:

```python
# In your face recognition system, after successful recognition:
from attendance_database import AttendanceDatabase

db = AttendanceDatabase()

# When a face is recognized
if recognized_name != "Unknown":
    db.check_in(recognized_name)
    print(f"{recognized_name} checked in successfully!")
```

## Data Export

Export attendance data to CSV for external analysis:

```python
# Export all data
db.export_to_csv("attendance_report.csv")

# Export filtered data
db.export_to_csv("january_report.csv", 
                 start_date="2025-01-01", 
                 end_date="2025-01-31")
```

## Error Handling

The system includes comprehensive error handling:
- Duplicate check-ins are prevented
- Missing check-in records for check-outs are handled
- Invalid data formats are caught and reported
- Database connection errors are handled gracefully

## Security Considerations

- Change the Flask secret key in production
- Implement proper authentication for web interface
- Use HTTPS in production environments
- Regular database backups recommended

## Troubleshooting

### Common Issues

1. **Database not found**: The database file is created automatically on first run
2. **Import errors**: Check CSV format matches expected structure
3. **Web interface not loading**: Ensure Flask is installed and port 5000 is available
4. **Permission errors**: Check file/directory permissions

### Debug Mode

Enable debug mode for detailed error messages:
```python
# In attendance_web.py
app.run(debug=True)
```

## Performance

- SQLite database for lightweight deployment
- Indexed queries for fast performance
- Efficient data structures for large datasets
- Minimal memory footprint

## Future Enhancements

- User authentication and authorization
- Email notifications
- Advanced reporting with charts
- Mobile app integration
- Real-time attendance monitoring
- Integration with payroll systems

## License

This project is open source and available under the MIT License. 