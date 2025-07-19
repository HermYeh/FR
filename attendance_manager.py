import time
import csv
from datetime import datetime
from attendance_database import AttendanceDatabase
from ui_dialogs import CustomDialog
import tkinter as tk

class AttendanceManager:
    """Handles attendance-related operations"""
    
    def __init__(self):
        self.attendance_db = None
        self.last_recognition_time = {}
        self.recognition_cooldown = 1
        self.last_checkin_name = ""
        self.last_checkin_time = ""
        self.has_checkins_today = False
        self.last_recognized_employee = None  # Track the last recognized employee for checkout
        
    def initialize_attendance_database(self):
        """Initialize attendance database"""
        try:
            self.attendance_db = AttendanceDatabase()
            print("Attendance database initialized")
            return True
        except Exception as e:
            print(f"Error initializing attendance database: {e}")
            self.attendance_db = None
            return False
    
    def handle_attendance_optimized(self, name):
        """Optimized attendance handling with database-based checking"""
        if not self.attendance_db:
            return False
        
        current_time = time.time()
        if name in self.last_recognition_time:
            if current_time - self.last_recognition_time[name] < self.recognition_cooldown:
                return False
        
        self.last_recognition_time[name] = current_time
        
        # Update last recognized employee for potential checkout
        self.last_recognized_employee = name
        
        try:
            # The database check_in method already handles checking if person checked in today
            if self.attendance_db.check_in(name):
                print(f"✅ {name} checked in at {datetime.now().strftime('%H:%M:%S')}")
                return True
            else:
                print(f"ℹ️  {name} already checked in today at {datetime.now().strftime('%H:%M:%S')}")
                return False
        except Exception as e:
            print(f"Error checking in {name}: {e}")
            return False
    
    def handle_checkout_optimized(self, name):
        """Handle checkout for the specified employee"""
        if not self.attendance_db:
            return False
        
        try:
            if self.attendance_db.check_out(name):
                print(f"✅ {name} checked out at {datetime.now().strftime('%H:%M:%S')}")
                return True
            else:
                print(f"ℹ️  {name} check-out failed - no check-in record found or already checked out")
                return False
        except Exception as e:
            print(f"Error checking out {name}: {e}")
            return False
    
    def sync_dataset_with_database(self):
        """Sync existing dataset users with the attendance database"""
        if not self.attendance_db:
            print("No attendance database available for sync")
            return
            
        try:
            import os
            # Get all existing users from dataset
            dataset_users = set()
            if os.path.exists('dataset'):
                for dirname in os.listdir('dataset'):
                    dir_path = os.path.join('dataset', dirname)
                    if os.path.isdir(dir_path):
                        txt_file = os.path.join(dir_path, f"{dirname}.txt")
                        if os.path.exists(txt_file):
                            with open(txt_file, 'r') as f:
                                name = f.read().strip()
                                if name:
                                    dataset_users.add(name)
            
            # Get existing employees from database
            existing_employees = set()
            try:
                employees = self.attendance_db.get_employees()
                for employee in employees:
                    existing_employees.add(employee['name'])
            except:
                pass
            
            # Find users in dataset but not in database
            new_users = dataset_users - existing_employees
            
            # Add missing users to database
            added_count = 0
            for user_name in new_users:
                try:
                    success = self.attendance_db.add_employee(
                        name=user_name,
                        employee_id=None,
                        department="Face Recognition",
                        position="Employee"
                    )
                    if success:
                        added_count += 1
                        print(f"Synced '{user_name}' to database")
                except Exception as e:
                    print(f"Failed to sync '{user_name}': {e}")
            
            if added_count > 0:
                print(f"Synced {added_count} users from dataset to database")
            elif len(dataset_users) > 0:
                print(f"All {len(dataset_users)} dataset users are already in database")
            else:
                print("No users found in dataset to sync")
                
        except Exception as e:
            print(f"Error syncing dataset with database: {e}")
    
    def is_employee_in_database(self, name):
        """Check if employee already exists in the database"""
        if not self.attendance_db:
            return False
        
        try:
            employees = self.attendance_db.get_employees()
            for employee in employees:
                if employee['name'].lower() == name.lower():
                    return True
            return False
        except Exception as e:
            print(f"Error checking employee database: {e}")
            return False
    
    def add_employee_to_database(self, name):
        """Add new employee to attendance database"""
        if not self.attendance_db:
            return False
        
        try:
            success = self.attendance_db.add_employee(
                name=name,
                employee_id=None,
                department="Face Recognition",
                position="Employee"
            )
            return success
        except Exception as e:
            print(f"Error adding employee to database: {e}")
            return False
    
    def load_existing_checkins(self, textbox):
        """Load today's existing check-ins from the database and display them in the textbox"""
        if not self.attendance_db:
            # If no database, just show the default message
            textbox.config(state=tk.NORMAL)
            textbox.delete(1.0, tk.END)
            textbox.insert(tk.END, "No check-ins today\n")
            textbox.config(state=tk.DISABLED)
            return
        
        try:
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get today's attendance records
            records = self.attendance_db.get_attendance_report(today, today)
            
            # Filter for records with check-in times
            checkins = [record for record in records if record.get('check_in_time')]
            
            # Update the textbox
            textbox.config(state=tk.NORMAL)
            textbox.delete(1.0, tk.END)
            
            if checkins:
                self.has_checkins_today = True
                # Sort by check-in time
                checkins.sort(key=lambda x: x['check_in_time'])
                
                for record in checkins:
                    name = record['name']
                    # Parse and format the check-in time
                    check_in_time = record['check_in_time']
                    if isinstance(check_in_time, str):
                        try:
                            # Try to parse the time string and format it
                            time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                            formatted_time = time_obj.strftime("%H:%M:%S")
                        except:
                            # If parsing fails, use the original string
                            formatted_time = check_in_time
                    else:
                        formatted_time = str(check_in_time)
                    
                    entry = f"✅ {name} - {formatted_time}\n"
                    textbox.insert(tk.END, entry)
                
                # Auto-scroll to the bottom
                textbox.see(tk.END)
                print(f"Loaded {len(checkins)} existing check-ins for today")
            else:
                self.has_checkins_today = False
                textbox.insert(tk.END, "No check-ins today\n")
            
            textbox.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading existing check-ins: {e}")
            # Show default message on error
            textbox.config(state=tk.NORMAL)
            textbox.delete(1.0, tk.END)
            textbox.insert(tk.END, "No check-ins today\n")
            textbox.config(state=tk.DISABLED)
    
    def update_last_checkin_display(self, name, textbox):
        """Update the check-in history in the textbox"""
        self.last_checkin_name = name
        self.last_checkin_time = datetime.now().strftime("%H:%M:%S")
        
        # Enable text editing
        textbox.config(state=tk.NORMAL)
        
        # Clear the initial message on first check-in
        if not self.has_checkins_today:
            textbox.delete(1.0, tk.END)
            self.has_checkins_today = True
        
        # Add new check-in entry with timestamp and name
        entry = f"✅ {name} - {self.last_checkin_time}\n"
        textbox.insert(tk.END, entry)
        
        # Auto-scroll to the bottom to show the latest entry
        textbox.see(tk.END)
        
        # Disable text editing to prevent user modification
        textbox.config(state=tk.DISABLED)
    
    def export_attendance_report(self, root):
        """Export attendance report to CSV"""
        if not self.attendance_db:
            CustomDialog.show_warning(root, "Warning", "Attendance database not available")
            return
        
        try:
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get attendance records
            records = self.attendance_db.get_attendance_report(today, today)
            
            if not records:
                CustomDialog.show_info(root, "Export Report", "No attendance records found for today.")
                return
            
            # Create CSV filename
            filename = f"attendance_report_{today}.csv"
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'date', 'check_in_time', 'check_out_time', 'total_hours']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in records:
                    writer.writerow(record)
            
            CustomDialog.show_info(root, "Export Complete", f"Attendance report exported to: {filename}")
            
        except Exception as e:
            CustomDialog.show_error(root, "Error", f"Failed to export report: {e}")
    
    def show_attendance_summary(self, root):
        """Show attendance summary"""
        if self.attendance_db is None:
            CustomDialog.show_warning(root, "Warning", "Attendance database not available")
            return
        
        try:
            summary = self.attendance_db.get_daily_summary()
            
            # Get registered employees
            employees = self.attendance_db.get_employees()
            employee_count = len(employees)
            
            # Get today's checked-in count from database
            current_date = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(current_date, current_date)
            checked_in_count = len([record for record in records if record['check_in_time']])
            
            summary_text = f"""Today's Attendance Summary:

Date: {summary['date']}
Total Employees: {summary['total_employees']}
Present: {summary['present_employees']}
Absent: {summary['absent_employees']}
Attendance Rate: {summary['attendance_rate']:.1f}%
Average Hours: {summary['average_hours']}

Checked in today: {checked_in_count} people

Registered Employees in Database: {employee_count}"""
            
            CustomDialog.show_info(root, "Attendance Summary", summary_text)
            
        except Exception as e:
            CustomDialog.show_error(root, "Error", f"Failed to get attendance summary: {e}")
    
    def manual_check_in(self, root):
        """Manual check-in dialog"""
        if self.attendance_db is None:
            CustomDialog.show_warning(root, "Warning", "Attendance database not available")
            return
        
        from tkinter import simpledialog
        name = simpledialog.askstring("Manual Check-in", "Enter employee name:")
        if name and name.strip():
            name = name.strip()
            try:
                if self.attendance_db.check_in(name):
                    CustomDialog.show_info(root, "Success", f"{name} checked in successfully!")
                    return name
                else:
                    CustomDialog.show_warning(root, "Warning", f"{name} already checked in today")
                    return None
            except Exception as e:
                CustomDialog.show_error(root, "Error", f"Failed to check in {name}: {e}")
                return None
        return None
    
    def cleanup_database(self):
        """Clean up database resources"""
        if self.attendance_db is not None:
            self.attendance_db.close() 