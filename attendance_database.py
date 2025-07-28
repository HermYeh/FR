'''
Attendance Database System
SQLite-based attendance tracking with check-in/check-out functionality
'''

import sqlite3
import csv
import os
from datetime import datetime, date
try:
    import pandas as pd
except ImportError:
    # Fallback if pandas is not available
    pd = None
from typing import List, Dict, Optional, Tuple

class AttendanceDatabase:
    def __init__(self, db_path: str = "attendance.db"):
        """Initialize the attendance database"""
        self.db_path = db_path
        # Remove persistent connection attributes
        self.init_database()
    
    def _get_connection(self):
        """Get a new database connection for the current thread"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    check_in_time TEXT,
                    check_out_time TEXT,
                    total_hours REAL,
                    status TEXT DEFAULT 'present',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create employees table for registered users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    employee_id TEXT UNIQUE,
                    department TEXT,
                    position TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_attendance_name_date 
                ON attendance(name, date)
            ''')
            
            conn.commit()
            conn.close()
            print(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def add_employee(self, name: str, employee_id: Optional[str] = None, 
                    department: Optional[str] = None, position: Optional[str] = None) -> bool:
        """Add a new employee to the database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employees (name, employee_id, department, position)
                VALUES (?, ?, ?, ?)
            ''', (name, employee_id, department, position))
            conn.commit()
            conn.close()
            print(f"Employee {name} added successfully")
            return True
        except sqlite3.IntegrityError:
            print(f"Employee {name} already exists")
            return False
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False
    
    def get_employees(self) -> List[Dict]:
        """Get all active employees"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, employee_id, department, position 
                FROM employees 
                WHERE is_active = 1
                ORDER BY name
            ''')
            employees = []
            for row in cursor.fetchall():
                employees.append({
                    'id': row[0],
                    'name': row[1],
                    'employee_id': row[2],
                    'department': row[3],
                    'position': row[4]
                })
            conn.close()
            return employees
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []
    
    def check_in(self, name: str, check_in_time: Optional[str] = None) -> bool:
        """Record check-in for an employee"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if check_in_time is None:
                check_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if already checked in today
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE name = ? AND date = ? AND check_in_time IS NOT NULL
            ''', (name, current_date))
            
            if cursor.fetchone():
                conn.close()
                print(f"{name} already checked in today")
                return False
            
            # Record check-in
            cursor.execute('''
                INSERT INTO attendance (name, date, check_in_time)
                VALUES (?, ?, ?)
            ''', (name, current_date, check_in_time))
            
            conn.commit()
            conn.close()
            print(f"{name} checked in at {check_in_time}")
            return True
            
        except Exception as e:
            print(f"Error during check-in: {e}")
            return False
    
    def check_out(self, name: str, check_out_time: Optional[str] = None) -> bool:
        """Record check-out for an employee"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if check_out_time is None:
                check_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Find today's check-in record
            cursor.execute('''
                SELECT id, check_in_time FROM attendance 
                WHERE name = ? AND date = ? AND check_in_time IS NOT NULL
            ''', (name, current_date))
            
            record = cursor.fetchone()
            if not record:
                conn.close()
                print(f"No check-in record found for {name} today")
                return False
            
            attendance_id, check_in_time = record
            
            # Calculate total hours
            check_in_dt = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
            check_out_dt = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:%S")
            total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
            
            # Update check-out time
            cursor.execute('''
                UPDATE attendance 
                SET check_out_time = ?, total_hours = ?
                WHERE id = ?
            ''', (check_out_time, total_hours, attendance_id))
            
            conn.commit()
            conn.close()
            print(f"{name} checked out at {check_out_time} (Total hours: {total_hours:.2f})")
            return True
            
        except Exception as e:
            print(f"Error during check-out: {e}")
            return False
    
    def delete_checkin(self, name: str, check_in_time: str) -> bool:
        """Delete a specific check-in record"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Find and delete the specific check-in record
            cursor.execute('''
                DELETE FROM attendance 
                WHERE name = ? AND date = ? AND check_in_time = ?
            ''', (name, current_date, check_in_time))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                print(f"Deleted check-in for {name} at {check_in_time}")
                return True
            else:
                print(f"No check-in record found for {name} at {check_in_time}")
                return False
                
        except Exception as e:
            print(f"Error deleting check-in: {e}")
            return False
    
    def get_attendance_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                            employee_name: Optional[str] = None) -> List[Dict]:
        """Get attendance report with optional filters"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT name, date, check_in_time, check_out_time, total_hours, status
                FROM attendance
                WHERE 1=1
            '''
            params = []
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            if employee_name:
                query += " AND name = ?"
                params.append(employee_name)
            
            query += " ORDER BY date DESC, name"
            
            cursor.execute(query, params)
            records = []
            for row in cursor.fetchall():
                records.append({
                    'name': row[0],
                    'date': row[1],
                    'check_in_time': row[2],
                    'check_out_time': row[3],
                    'total_hours': row[4],
                    'status': row[5]
                })
            conn.close()
            return records
            
        except Exception as e:
            print(f"Error getting attendance report: {e}")
            return []
    
    def get_daily_summary(self, target_date: Optional[str] = None) -> Dict:
        """Get daily attendance summary"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if target_date is None:
                target_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get total employees
            cursor.execute('SELECT COUNT(*) FROM employees WHERE is_active = 1')
            total_employees = cursor.fetchone()[0]
            
            # Get present employees
            cursor.execute('''
                SELECT COUNT(DISTINCT name) FROM attendance 
                WHERE date = ? AND check_in_time IS NOT NULL
            ''', (target_date,))
            present_employees = cursor.fetchone()[0]
            
            # Get absent employees
            absent_employees = total_employees - present_employees
            
            # Get average hours worked
            cursor.execute('''
                SELECT AVG(total_hours) FROM attendance 
                WHERE date = ? AND total_hours IS NOT NULL
            ''', (target_date,))
            avg_hours = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'date': target_date,
                'total_employees': total_employees,
                'present_employees': present_employees,
                'absent_employees': absent_employees,
                'attendance_rate': (present_employees / total_employees * 100) if total_employees > 0 else 0,
                'average_hours': round(avg_hours, 2)
            }
            
        except Exception as e:
            print(f"Error getting daily summary: {e}")
            return {}
    
    def import_from_csv(self, csv_file: str) -> bool:
        """Import attendance data from CSV file"""
        try:
            if not os.path.exists(csv_file):
                print(f"CSV file not found: {csv_file}")
                return False
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    name = row.get('Name', '').strip()
                    datetime_str = row.get('Datetime', '').strip()
                    
                    if name and datetime_str and name != 'Unknown':
                        # Parse datetime
                        try:
                            dt = datetime.strptime(datetime_str, "%Y/%m/%d, %H:%M:%S")
                            date_str = dt.strftime("%Y-%m-%d")
                            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Check if this is a check-in (first record of the day for this person)
                            cursor.execute('''
                                SELECT id FROM attendance 
                                WHERE name = ? AND date = ?
                            ''', (name, date_str))
                            
                            if not cursor.fetchone():
                                # This is a check-in
                                cursor.execute('''
                                    INSERT INTO attendance (name, date, check_in_time)
                                    VALUES (?, ?, ?)
                                ''', (name, date_str, time_str))
                            
                        except ValueError as e:
                            print(f"Error parsing datetime {datetime_str}: {e}")
                            continue
            
            conn.commit()
            conn.close()
            print(f"Successfully imported data from {csv_file}")
            return True
            
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False
    
    def export_to_csv(self, filename: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> bool:
        """Export attendance data to CSV"""
        try:
            records = self.get_attendance_report(start_date, end_date)
            
            with open(filename, 'w', newline='') as file:
                fieldnames = ['Name', 'Date', 'Check In Time', 'Check Out Time', 'Total Hours', 'Status']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in records:
                    writer.writerow({
                        'Name': record['name'],
                        'Date': record['date'],
                        'Check In Time': record['check_in_time'] or '',
                        'Check Out Time': record['check_out_time'] or '',
                        'Total Hours': record['total_hours'] or '',
                        'Status': record['status']
                    })
            
            print(f"Attendance data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_employee_attendance(self, employee_name: str, days: int = 30) -> List[Dict]:
        """Get attendance history for a specific employee"""
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            if pd is not None:
                try:
                    from datetime import timedelta
                    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                except (AttributeError, TypeError, ValueError):
                    # Fallback: use current date
                    start_date = datetime.now().strftime("%Y-%m-%d")
            else:
                from datetime import timedelta
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            return self.get_attendance_report(start_date, end_date, employee_name)
        except Exception as e:
            print(f"Error getting employee attendance: {e}")
            return []
    

    def get_checked_in_employees(self) -> List[Dict]:
        """Get all employees who are currently checked in (no check-out yet today)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT name, check_in_time 
                FROM attendance 
                WHERE date = ? AND check_in_time IS NOT NULL AND check_out_time IS NULL
                ORDER BY name
            ''', (current_date,))
            
            checked_in = []
            for row in cursor.fetchall():
                checked_in.append({
                    'name': row[0],
                    'check_in_time': row[1]
                })
            conn.close()
            return checked_in
            
        except Exception as e:
            print(f"Error getting checked-in employees: {e}")
            return []
    
    def delete_employee(self, employee_name: str) -> bool:
        """Delete an employee and all their attendance records"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # First check if employee exists
            cursor.execute('''
                SELECT id FROM employees WHERE name = ?
            ''', (employee_name,))
            
            if not cursor.fetchone():
                conn.close()
                print(f"Employee {employee_name} not found")
                return False
            
            # Delete all attendance records for this employee
            cursor.execute('''
                DELETE FROM attendance WHERE name = ?
            ''', (employee_name,))
            
            # Delete the employee record
            cursor.execute('''
                DELETE FROM employees WHERE name = ?
            ''', (employee_name,))
            
            conn.commit()
            conn.close()
            print(f"Employee {employee_name} and all their records deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting employee {employee_name}: {e}")
            return False
    
    def close(self):
        """Close database connection - now this is a no-op since we don't maintain persistent connections"""
        print("Database connections are now managed per-operation")

def main():
    """Main function to demonstrate the attendance database"""
    db = AttendanceDatabase()
    
    # Add some sample employees
    employees = [
        ("HERMAN YEH", "EMP001", "Engineering", "Developer"),
        ("ELON MUSK", "EMP002", "Management", "CEO"),
        ("ELON MUSK2", "EMP003", "Engineering", "CTO"),
        ("Bill Gates", "EMP004", "Management", "Advisor")
    ]
    
    for emp in employees:
        db.add_employee(*emp)
    
    # Import existing CSV data
    if os.path.exists("20250704_register_log.csv"):
        db.import_from_csv("20250704_register_log.csv")
    
    if os.path.exists("20250705_register_log.csv"):
        db.import_from_csv("20250705_register_log.csv")
    
    # Show daily summary
    summary = db.get_daily_summary()
    print("\n=== Daily Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Show attendance report
    print("\n=== Recent Attendance ===")
    records = db.get_attendance_report()
    for record in records[:10]:  # Show last 10 records
        print(f"{record['name']} - {record['date']} - Check-in: {record['check_in_time']} - Check-out: {record['check_out_time']}")
    
    db.close()

if __name__ == "__main__":
    main() 