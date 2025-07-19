'''
Attendance Database Command Line Interface
Simple CLI for managing attendance records
'''

import argparse
import sys
from datetime import datetime, date
from attendance_database import AttendanceDatabase

def print_header():
    """Print application header"""
    print("=" * 50)
    print("           ATTENDANCE DATABASE SYSTEM")
    print("=" * 50)

def print_menu():
    """Print main menu options"""
    print("\nMain Menu:")
    print("1. Check In")
    print("2. Check Out")
    print("3. View Daily Summary")
    print("4. View Attendance Report")
    print("5. Add Employee")
    print("6. List Employees")
    print("7. Import from CSV")
    print("8. Export to CSV")
    print("9. View Employee History")
    print("0. Exit")

def interactive_mode():
    """Run interactive mode"""
    db = AttendanceDatabase()
    
    while True:
        print_header()
        print_menu()
        
        try:
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
                
            elif choice == '1':
                name = input("Enter employee name: ").strip()
                if name:
                    db.check_in(name)
                else:
                    print("Name cannot be empty")
                    
            elif choice == '2':
                name = input("Enter employee name: ").strip()
                if name:
                    db.check_out(name)
                else:
                    print("Name cannot be empty")
                    
            elif choice == '3':
                target_date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
                summary = db.get_daily_summary(target_date if target_date else None)
                print("\n=== Daily Summary ===")
                for key, value in summary.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                    
            elif choice == '4':
                start_date = input("Enter start date (YYYY-MM-DD) or press Enter for all: ").strip()
                end_date = input("Enter end date (YYYY-MM-DD) or press Enter for all: ").strip()
                employee = input("Enter employee name or press Enter for all: ").strip()
                
                records = db.get_attendance_report(
                    start_date if start_date else None,
                    end_date if end_date else None,
                    employee if employee else None
                )
                
                print(f"\n=== Attendance Report ({len(records)} records) ===")
                for record in records:
                    print(f"{record['name']} | {record['date']} | "
                          f"Check-in: {record['check_in_time'] or 'N/A'} | "
                          f"Check-out: {record['check_out_time'] or 'N/A'} | "
                          f"Hours: {record['total_hours'] or 'N/A'}")
                          
            elif choice == '5':
                name = input("Enter employee name: ").strip()
                employee_id = input("Enter employee ID (optional): ").strip()
                department = input("Enter department (optional): ").strip()
                position = input("Enter position (optional): ").strip()
                
                if name:
                    db.add_employee(name, employee_id, department, position)
                else:
                    print("Name cannot be empty")
                    
            elif choice == '6':
                employees = db.get_employees()
                print(f"\n=== Employees ({len(employees)}) ===")
                for emp in employees:
                    print(f"{emp['name']} | ID: {emp['employee_id'] or 'N/A'} | "
                          f"Dept: {emp['department'] or 'N/A'} | "
                          f"Position: {emp['position'] or 'N/A'}")
                          
            elif choice == '7':
                csv_file = input("Enter CSV file path: ").strip()
                if csv_file:
                    db.import_from_csv(csv_file)
                else:
                    print("File path cannot be empty")
                    
            elif choice == '8':
                filename = input("Enter output filename: ").strip()
                start_date = input("Enter start date (YYYY-MM-DD) or press Enter for all: ").strip()
                end_date = input("Enter end date (YYYY-MM-DD) or press Enter for all: ").strip()
                
                if filename:
                    db.export_to_csv(filename, start_date if start_date else None, 
                                   end_date if end_date else None)
                else:
                    print("Filename cannot be empty")
                    
            elif choice == '9':
                name = input("Enter employee name: ").strip()
                days = input("Enter number of days (default 30): ").strip()
                
                if name:
                    try:
                        days_int = int(days) if days else 30
                        records = db.get_employee_attendance(name, days_int)
                        print(f"\n=== {name}'s Attendance History ({len(records)} records) ===")
                        for record in records:
                            print(f"{record['date']} | "
                                  f"Check-in: {record['check_in_time'] or 'N/A'} | "
                                  f"Check-out: {record['check_out_time'] or 'N/A'} | "
                                  f"Hours: {record['total_hours'] or 'N/A'}")
                    except ValueError:
                        print("Invalid number of days")
                else:
                    print("Name cannot be empty")
                    
            else:
                print("Invalid choice. Please enter a number between 0-9.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Attendance Database System')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--check-in', type=str, help='Check in employee')
    parser.add_argument('--check-out', type=str, help='Check out employee')
    parser.add_argument('--summary', action='store_true', help='Show daily summary')
    parser.add_argument('--report', action='store_true', help='Show attendance report')
    parser.add_argument('--add-employee', type=str, help='Add employee name')
    parser.add_argument('--list-employees', action='store_true', help='List all employees')
    parser.add_argument('--import-csv', type=str, help='Import from CSV file')
    parser.add_argument('--export-csv', type=str, help='Export to CSV file')
    parser.add_argument('--employee-history', type=str, help='Show employee history')
    parser.add_argument('--days', type=int, default=30, help='Number of days for history')
    
    args = parser.parse_args()
    
    db = AttendanceDatabase()
    
    try:
        if args.interactive:
            interactive_mode()
        elif args.check_in:
            db.check_in(args.check_in)
        elif args.check_out:
            db.check_out(args.check_out)
        elif args.summary:
            summary = db.get_daily_summary()
            print("=== Daily Summary ===")
            for key, value in summary.items():
                print(f"{key}: {value}")
        elif args.report:
            records = db.get_attendance_report()
            print("=== Attendance Report ===")
            for record in records:
                print(f"{record['name']} | {record['date']} | "
                      f"Check-in: {record['check_in_time'] or 'N/A'} | "
                      f"Check-out: {record['check_out_time'] or 'N/A'}")
        elif args.add_employee:
            db.add_employee(args.add_employee)
        elif args.list_employees:
            employees = db.get_employees()
            print("=== Employees ===")
            for emp in employees:
                print(f"{emp['name']} | {emp['employee_id'] or 'N/A'}")
        elif args.import_csv:
            db.import_from_csv(args.import_csv)
        elif args.export_csv:
            db.export_to_csv(args.export_csv)
        elif args.employee_history:
            records = db.get_employee_attendance(args.employee_history, args.days)
            print(f"=== {args.employee_history}'s History ===")
            for record in records:
                print(f"{record['date']} | "
                      f"Check-in: {record['check_in_time'] or 'N/A'} | "
                      f"Check-out: {record['check_out_time'] or 'N/A'}")
        else:
            # No arguments provided, show help
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 