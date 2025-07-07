'''
Attendance Database Demo
Demonstrates the attendance database functionality
'''

from attendance_database import AttendanceDatabase
from datetime import datetime, timedelta
import time

def demo_attendance_system():
    """Demonstrate the attendance database system"""
    print("=== Attendance Database Demo ===")
    print()
    
    # Initialize database
    db = AttendanceDatabase()
    
    # Add sample employees
    print("1. Adding sample employees...")
    employees = [
        ("John Smith", "EMP001", "Engineering", "Developer"),
        ("Jane Doe", "EMP002", "Marketing", "Manager"),
        ("Bob Johnson", "EMP003", "Sales", "Representative"),
        ("Alice Brown", "EMP004", "HR", "Coordinator")
    ]
    
    for emp in employees:
        db.add_employee(*emp)
    
    print("\n2. Simulating check-ins...")
    # Simulate check-ins for today
    current_time = datetime.now()
    
    # John Smith checks in at 9:00 AM
    check_in_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    db.check_in("John Smith", check_in_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Jane Doe checks in at 8:45 AM
    check_in_time = current_time.replace(hour=8, minute=45, second=0, microsecond=0)
    db.check_in("Jane Doe", check_in_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Bob Johnson checks in at 9:15 AM
    check_in_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
    db.check_in("Bob Johnson", check_in_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    print("\n3. Simulating check-outs...")
    # Simulate check-outs
    # John Smith checks out at 5:30 PM
    check_out_time = current_time.replace(hour=17, minute=30, second=0, microsecond=0)
    db.check_out("John Smith", check_out_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Jane Doe checks out at 5:45 PM
    check_out_time = current_time.replace(hour=17, minute=45, second=0, microsecond=0)
    db.check_out("Jane Doe", check_out_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    print("\n4. Showing daily summary...")
    summary = db.get_daily_summary()
    print("=== Daily Summary ===")
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n5. Showing attendance report...")
    records = db.get_attendance_report()
    print("=== Attendance Report ===")
    for record in records:
        print(f"{record['name']} | {record['date']} | "
              f"Check-in: {record['check_in_time'] or 'N/A'} | "
              f"Check-out: {record['check_out_time'] or 'N/A'} | "
              f"Hours: {record['total_hours'] or 'N/A'}")
    
    print("\n6. Showing employee list...")
    employees = db.get_employees()
    print("=== Employees ===")
    for emp in employees:
        print(f"{emp['name']} | ID: {emp['employee_id']} | "
              f"Dept: {emp['department']} | Position: {emp['position']}")
    
    print("\n7. Exporting to CSV...")
    db.export_to_csv("demo_attendance_report.csv")
    
    print("\n8. Testing manual operations...")
    # Test manual check-in
    print("Testing manual check-in for Alice Brown...")
    db.check_in("Alice Brown")
    
    # Test manual check-out
    print("Testing manual check-out for Alice Brown...")
    db.check_out("Alice Brown")
    
    print("\n9. Final attendance report...")
    records = db.get_attendance_report()
    print("=== Final Attendance Report ===")
    for record in records:
        print(f"{record['name']} | {record['date']} | "
              f"Check-in: {record['check_in_time'] or 'N/A'} | "
              f"Check-out: {record['check_out_time'] or 'N/A'} | "
              f"Hours: {record['total_hours'] or 'N/A'}")
    
    # Clean up
    db.close()
    print("\n=== Demo completed successfully! ===")

def demo_import_export():
    """Demonstrate import/export functionality"""
    print("\n=== Import/Export Demo ===")
    
    db = AttendanceDatabase("demo_import.db")
    
    # Add some employees
    db.add_employee("Demo User 1", "DEMO001", "Demo", "Tester")
    db.add_employee("Demo User 2", "DEMO002", "Demo", "Tester")
    
    # Simulate some attendance
    db.check_in("Demo User 1")
    time.sleep(1)  # Small delay
    db.check_out("Demo User 1")
    
    db.check_in("Demo User 2")
    time.sleep(1)  # Small delay
    db.check_out("Demo User 2")
    
    # Export data
    print("Exporting attendance data...")
    db.export_to_csv("demo_export.csv")
    
    # Create new database and import
    db2 = AttendanceDatabase("demo_import2.db")
    print("Importing attendance data...")
    db2.import_from_csv("demo_export.csv")
    
    # Show imported data
    records = db2.get_attendance_report()
    print("=== Imported Data ===")
    for record in records:
        print(f"{record['name']} | {record['date']} | "
              f"Check-in: {record['check_in_time'] or 'N/A'}")
    
    db.close()
    db2.close()
    print("Import/Export demo completed!")

if __name__ == "__main__":
    try:
        demo_attendance_system()
        demo_import_export()
    except Exception as e:
        print(f"Demo error: {e}") 