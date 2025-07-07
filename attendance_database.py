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
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create attendance table
            self.cursor.execute('''
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
            self.cursor.execute('''
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
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_attendance_name_date 
                ON attendance(name, date)
            ''')
            
            self.conn.commit()
            print(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def add_employee(self, name: str, employee_id: Optional[str] = None, 
                    department: Optional[str] = None, position: Optional[str] = None) -> bool:
        """Add a new employee to the database"""
        if self.cursor is None:
            print("Database not initialized")
            return False
        try:
            self.cursor.execute('''
                INSERT INTO employees (name, employee_id, department, position)
                VALUES (?, ?, ?, ?)
            ''', (name, employee_id, department, position))
            self.conn.commit()
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
        if self.cursor is None:
            print("Database not initialized")
            return []
        try:
            self.cursor.execute('''
                SELECT id, name, employee_id, department, position 
                FROM employees 
                WHERE is_active = 1
                ORDER BY name
            ''')
            employees = []
            for row in self.cursor.fetchall():
                employees.append({
                    'id': row[0],
                    'name': row[1],
                    'employee_id': row[2],
                    'department': row[3],
                    'position': row[4]
                })
            return employees
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []
    
    def check_in(self, name: str, check_in_time: str = None) -> bool:
        """Record check-in for an employee"""
        try:
            if check_in_time is None:
                check_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if already checked in today
            self.cursor.execute('''
                SELECT id FROM attendance 
                WHERE name = ? AND date = ? AND check_in_time IS NOT NULL
            ''', (name, current_date))
            
            if self.cursor.fetchone():
                print(f"{name} already checked in today")
                return False
            
            # Record check-in
            self.cursor.execute('''
                INSERT INTO attendance (name, date, check_in_time)
                VALUES (?, ?, ?)
            ''', (name, current_date, check_in_time))
            
            self.conn.commit()
            print(f"{name} checked in at {check_in_time}")
            return True
            
        except Exception as e:
            print(f"Error during check-in: {e}")
            return False
    
    def check_out(self, name: str, check_out_time: str = None) -> bool:
        """Record check-out for an employee"""
        try:
            if check_out_time is None:
                check_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Find today's check-in record
            self.cursor.execute('''
                SELECT id, check_in_time FROM attendance 
                WHERE name = ? AND date = ? AND check_in_time IS NOT NULL
            ''', (name, current_date))
            
            record = self.cursor.fetchone()
            if not record:
                print(f"No check-in record found for {name} today")
                return False
            
            attendance_id, check_in_time = record
            
            # Calculate total hours
            check_in_dt = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
            check_out_dt = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:%S")
            total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
            
            # Update check-out time
            self.cursor.execute('''
                UPDATE attendance 
                SET check_out_time = ?, total_hours = ?
                WHERE id = ?
            ''', (check_out_time, total_hours, attendance_id))
            
            self.conn.commit()
            print(f"{name} checked out at {check_out_time} (Total hours: {total_hours:.2f})")
            return True
            
        except Exception as e:
            print(f"Error during check-out: {e}")
            return False
    
    def get_attendance_report(self, start_date: str = None, end_date: str = None, 
                            employee_name: str = None) -> List[Dict]:
        """Get attendance report with optional filters"""
        try:
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
            
            self.cursor.execute(query, params)
            records = []
            for row in self.cursor.fetchall():
                records.append({
                    'name': row[0],
                    'date': row[1],
                    'check_in_time': row[2],
                    'check_out_time': row[3],
                    'total_hours': row[4],
                    'status': row[5]
                })
            return records
            
        except Exception as e:
            print(f"Error getting attendance report: {e}")
            return []
    
    def get_daily_summary(self, target_date: str = None) -> Dict:
        """Get daily attendance summary"""
        try:
            if target_date is None:
                target_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get total employees
            self.cursor.execute('SELECT COUNT(*) FROM employees WHERE is_active = 1')
            total_employees = self.cursor.fetchone()[0]
            
            # Get present employees
            self.cursor.execute('''
                SELECT COUNT(DISTINCT name) FROM attendance 
                WHERE date = ? AND check_in_time IS NOT NULL
            ''', (target_date,))
            present_employees = self.cursor.fetchone()[0]
            
            # Get absent employees
            absent_employees = total_employees - present_employees
            
            # Get average hours worked
            self.cursor.execute('''
                SELECT AVG(total_hours) FROM attendance 
                WHERE date = ? AND total_hours IS NOT NULL
            ''', (target_date,))
            avg_hours = self.cursor.fetchone()[0] or 0
            
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
                            self.cursor.execute('''
                                SELECT id FROM attendance 
                                WHERE name = ? AND date = ?
                            ''', (name, date_str))
                            
                            if not self.cursor.fetchone():
                                # This is a check-in
                                self.cursor.execute('''
                                    INSERT INTO attendance (name, date, check_in_time)
                                    VALUES (?, ?, ?)
                                ''', (name, date_str, time_str))
                            
                        except ValueError as e:
                            print(f"Error parsing datetime {datetime_str}: {e}")
                            continue
            
            self.conn.commit()
            print(f"Successfully imported data from {csv_file}")
            return True
            
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return False
    
    def export_to_csv(self, filename: str, start_date: str = None, end_date: str = None) -> bool:
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
                start_date = (datetime.now() - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
            else:
                # Fallback without pandas
                from datetime import timedelta
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            return self.get_attendance_report(start_date, end_date, employee_name)
            
        except Exception as e:
            print(f"Error getting employee attendance: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

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