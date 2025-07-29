import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
from ui_dialogs import CustomDialog
from attendance_database import AttendanceDatabase
from virtual_keyboard import VirtualKeyboard


class MenuManager:
    """Handles menu windows and UI management"""
    
    def __init__(self):
        self.menu_window = None
        self.current_page = 0
        self.dates_per_page = 30
        self.selected_date = None
        self.attendance_db = AttendanceDatabase()
        self._injected_start_capture = lambda menu_window=None: None
        self.active_keyboards = []  # Track active virtual keyboards
    
    def setup_virtual_keyboard_for_entry(self, entry_widget, text_var, parent_container, confirm_callback=None):
        """Set up virtual keyboard for an entry widget"""
        try:
            # Create a container for the virtual keyboard if it doesn't exist
            if not hasattr(parent_container, 'keyboard_container'):
                parent_container.keyboard_container = tk.Frame(parent_container, bg='#2c3e50')
                parent_container.keyboard_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            # Hide other keyboards in this container
            self.hide_all_keyboards_in_container(parent_container)
            
            # Create virtual keyboard
            virtual_keyboard = VirtualKeyboard(parent_container.keyboard_container, text_var)
            virtual_keyboard.setup_dynamic_keyboard(entry_widget, confirm_callback)
            
            # Track this keyboard
            self.active_keyboards.append(virtual_keyboard)
            
            return virtual_keyboard
            
        except Exception as e:
            print(f"Error setting up virtual keyboard: {e}")
            return None
    
    def hide_all_keyboards_in_container(self, container):
        """Hide all virtual keyboards in a container"""
        try:
            # Hide keyboards that might be showing
            for keyboard in self.active_keyboards:
                if keyboard.is_visible:
                    keyboard.hide_keyboard()
        except Exception as e:
            print(f"Error hiding keyboards: {e}")
    
    def cleanup_keyboards(self):
        """Clean up all virtual keyboards"""
        try:
            for keyboard in self.active_keyboards:
                keyboard.destroy()
            self.active_keyboards.clear()
        except Exception as e:
            print(f"Error cleaning up keyboards: {e}")
    
    def change_hour(self, delta):
        """Change hour value with wrapping (0-23)"""
        current_hour = self.hour_var.get()
        new_hour = (current_hour + delta) % 24
        self.hour_var.set(new_hour)
        selected_time = f"{self.hour_var.get():02d}:{self.minute_var.get():02d}"
        self.time_var.set(selected_time)
    
    def change_minute(self, delta):
        """Change minute value (only 00 or 30)"""
        current_minute = self.minute_var.get()
        current_hour = self.hour_var.get()

        if delta > 0:  # Up button
        
            if current_minute == 0:
                new_minute = 30 
            else:
                new_minute=0
                current_hour=current_hour+1
                self.hour_var.set(current_hour)
        else:  # Down button
            if current_minute == 30:
                new_minute = 0
            else:
                new_minute=30
                current_hour=current_hour-1
                self.hour_var.set(current_hour)
        self.minute_var.set(new_minute)
        selected_time = f"{self.hour_var.get():02d}:{self.minute_var.get():02d}"
        self.time_var.set(selected_time)
       
    def show_main_menu_window(self, root):
        self.menu_window = tk.Toplevel(root)
        self.menu_window.grab_set()  
        self.menu_window.transient(root)
    
        self.menu_window.title("TS Ma's Attendance System")
        self.menu_window.configure(bg='#2c3e50')
        
        # Set window size and center it
        window_width = 800
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.menu_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        # Make window resizable for user flexibility
        self.menu_window.resizable(True, True)
        self.menu_window.minsize(800, 600)  # Set minimum size
        self.menu_window.protocol("WM_DELETE_WINDOW", self.close_menu_window)

        # Center the window
        self.show_menu()
    
    def show_menu(self):
        # Main container
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Title (larger font)
        title_label = tk.Label(main_frame, text="Main Menu", 
                              font=('Arial', 28, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 30))
        
        # Create sections
        self.create_employee_section(main_frame)
        self.create_edit_section(main_frame)
        self.create_settings_section(main_frame)
        self.create_system_section(main_frame)
    
    def create_employee_section(self, parent):
        """Create Employee Check-in Details section"""
        # Section frame (larger font)
        section_frame = tk.LabelFrame(parent, text="Employee Management", 
                                    font=('Arial', 16, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations (larger font)
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 19, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Single Employee Check-in Details button with click protection
        employee_detail_btn = tk.Button(buttons_frame, text="Employee Details", 
                                       command=lambda: self.show_employee(parent),
                                       bg='#3498db', fg='white', **button_config)
        employee_detail_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Additional utility buttons with click protection
        photos_btn = tk.Button(buttons_frame, text="Check-in Details", 
                              command=self.show_checkin,
                              bg='#e67e22', fg='white', **button_config)
        photos_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export Report button with click protection
        export_btn = tk.Button(buttons_frame, text="Export Report", 
                              command=self.export_attendance_report,
                              bg='#27ae60', fg='white', **button_config)
        export_btn.pack(side=tk.LEFT)
    
    def create_edit_section(self, parent):
        """Create Edit section"""
        # Section frame (larger font)
        section_frame = tk.LabelFrame(parent, text="Edit & Manage", 
                                    font=('Arial', 16, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations (larger font)
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 19, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Edit Today's Check-ins button with click protection
        edit_btn = tk.Button(buttons_frame, text="Edit Check-ins", 
                            command=self.show_edit,
                            bg='#e74c3c', fg='white', **button_config)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        edit_employee_btn = tk.Button(buttons_frame, text="Add Employee", 
                            command=self.start_capture,
                            bg='#27ae60', fg='white', **button_config)
        edit_employee_btn.pack(side=tk.LEFT)
    
    def create_settings_section(self, parent):
        """Create Settings section"""
        # Section frame (larger font)
        section_frame = tk.LabelFrame(parent, text="System Settings", 
                                    font=('Arial', 16, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations (larger font)
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 19, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        attendance_btn = tk.Button(buttons_frame, text="Attendance", 
                              command=lambda: self.show_attendance_settings(parent),
                              bg='#34495e', fg='white', **button_config)
        attendance_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Camera Settings button with click protection
        camera_btn = tk.Button(buttons_frame, text="Camera", 
                              command=self.show_camera_settings,
                              bg='#34495e', fg='white', **button_config)
        camera_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Recognition Settings button with click protection
        recognition_btn = tk.Button(buttons_frame, text="Recognition", 
                                  command=self.show_recognition_settings,
                                  bg='#34495e', fg='white', **button_config)
        recognition_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Database Settings button with click protection
        db_btn = tk.Button(buttons_frame, text="Database Settings", 
                          command=self.show_database_settings,
                          bg='#34495e', fg='white', **button_config)
        db_btn.pack(side=tk.LEFT)
    
    def create_system_section(self, parent):
        """Create System section"""
        # Section frame (larger font)
        section_frame = tk.LabelFrame(parent, text="System Control", 
                                    font=('Arial', 16, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations (larger font)
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 19, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Reset System button with click protection
        reset_btn = tk.Button(buttons_frame, text="Reset System", 
                             command=self.reset_system,
                             bg='#f39c12', fg='white', **button_config)
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button with click protection
        exit_btn = tk.Button(buttons_frame, text="Exit System", 
                            command=self.cleanup_and_exit,
                            bg='#e74c3c', fg='white', **button_config)
        exit_btn.pack(side=tk.LEFT)
        
        # Close Menu button with click protection
        close_btn = tk.Button(buttons_frame, text="Close Menu", 
                             command=self.close_menu_window,
                             bg='#95a5a6', fg='white', **button_config)
        close_btn.pack(side=tk.RIGHT)
        close_btn.focus_set()
    
    def close_menu_window(self):
        if self.menu_window:
            self.menu_window.destroy()
    
    
    def show_employee(self, parent):
        parent.destroy()
        self.show_employee_detail_window()
    
    def show_employee_detail_window(self):
        """Show comprehensive employee detail window"""
        # Main container
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        # Title (larger font)
        title_label = tk.Label(main_frame, text="Employee Check-in Details", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        # Create main content frame
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left section - Employee List
        self.create_employee_list_section(content_frame)
        # Right section - Employee Details
        self.create_employee_details_section(content_frame)
        # Bottom buttons
        self.create_employee_window_buttons(main_frame)
        # Load employee data
        self.load_employee_data()
    
    def create_employee_list_section(self, parent):
        """Create employee list section on the left"""
        # Left frame
        left_frame = tk.Frame(parent, bg='#2c3e50')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Employee list label (larger font)
        list_label = tk.Label(left_frame, text="Employee List", 
                             font=('Arial', 18, 'bold'), 
                             fg='#ecf0f1', bg='#2c3e50')
        list_label.pack(pady=(0, 10))
        
        # List frame with scrollbar
        list_container = tk.Frame(left_frame, bg='#2c3e50')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Employee listbox (larger for easier selection)
        self.employee_listbox = tk.Listbox(list_container, 
                                          font=('Arial', 16, 'bold'),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#3498db',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2,
                                          height=12)
        
        # Scrollbar for employee list
        employee_scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                         command=self.employee_listbox.yview)
        self.employee_listbox.config(yscrollcommand=employee_scrollbar.set)
        
        # Pack employee list components
        self.employee_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        employee_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.employee_listbox.bind('<<ListboxSelect>>', self.on_employee_detail_select)
    
    def create_employee_details_section(self, parent):
        """Create employee details section on the right"""
        # Right frame
        right_frame = tk.Frame(parent, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Employee details label (larger font)
        details_label = tk.Label(right_frame, text="Employee Details", 
                                font=('Arial', 18, 'bold'), 
                                fg='#ecf0f1', bg='#2c3e50')
        details_label.pack(pady=(0, 10))
        
        # Details container frame
        details_container = tk.Frame(right_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        details_container.pack(fill=tk.BOTH, expand=True)
        
        # Details content frame
        self.details_content = tk.Frame(details_container, bg='#34495e')
        self.details_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Initial message
        self.show_no_selection_message()
    
    def create_employee_window_buttons(self, parent):
        """Create buttons for employee window"""
        button_frame = tk.Frame(parent, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side buttons (actions)
        left_buttons = tk.Frame(button_frame, bg='#2c3e50')
        left_buttons.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Register New Employee button
        register_btn = tk.Button(left_buttons, text="Register New Employee", 
                                command=self.show_add_employee,
                                font=('Arial', 12, 'bold'),
                                bg='#27ae60', fg='white',
                                width=18, height=2,
                                relief=tk.RAISED, bd=2)
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete Employee button (warning color)
        delete_btn = tk.Button(left_buttons, text="Delete Employee", 
                              command=self.delete_selected_employee,
                              font=('Arial', 12, 'bold'),
                              bg='#e74c3c', fg='white',
                              width=15, height=2,
                              relief=tk.RAISED, bd=2)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side buttons (utility)
        right_buttons = tk.Frame(button_frame, bg='#2c3e50')
        right_buttons.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_btn = tk.Button(right_buttons, text="Refresh", 
                               command=self.refresh_employee_data,
                               font=('Arial', 12, 'bold'),
                               bg='#3498db', fg='white',
                               width=12, height=2,
                               relief=tk.RAISED, bd=2)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(right_buttons, text="Close", 
                             command=self.close_employee_window,
                             font=('Arial', 12, 'bold'),
                             bg='#95a5a6', fg='white',
                             width=12, height=2,
                             relief=tk.RAISED, bd=2)
        close_btn.pack(side=tk.LEFT)
        close_btn.focus_set()
    
    def close_employee_window(self):
        # Clear the current frame and show main menu
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.show_menu()
    


    def load_employee_data(self):

        """Load employee data into the listbox"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window, "Error", "Attendance database not initialized.")
            return
        try:
            employees = self.attendance_db.get_employees()
            
            # Clear existing items
            self.employee_listbox.delete(0, tk.END)
            
            # Store employee data
            self.employee_data = employees
            
            if not employees:
                self.employee_listbox.insert(tk.END, "No employees found")
                return
            
            # Add employees to listbox
            for employee in employees:
                name = employee['name']
                dept = employee.get('department', 'N/A')
                display_text = f"{name} ({dept})"
                self.employee_listbox.insert(tk.END, display_text)
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window, "Error", f"Failed to load employee data: {e}")
    
    def on_employee_detail_select(self, event):
        """Handle employee selection"""
        selection = self.employee_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.employee_data):
            return
        
        # Get selected employee
        selected_employee = self.employee_data[index]
        self.show_employee_details(selected_employee)
    
    def show_employee_details(self, employee):
        """Show detailed information for selected employee"""
        # Clear previous content
        for widget in self.details_content.winfo_children():
            widget.destroy()
        
        # Selected employee header with visual emphasis
        header_frame = tk.Frame(self.details_content, bg='#3498db', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        # Employee name with emphasis
        name_label = tk.Label(header_frame, text=f"{employee['name']}", 
                             font=('Arial', 16, 'bold'), 
                             fg='white', bg='#3498db')
        name_label.pack(pady=(0, 5))
        
        # Basic info frame
        info_frame = tk.Frame(self.details_content, bg='#34495e')
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Department
        dept_label = tk.Label(info_frame, text=f"Department: {employee.get('department', 'N/A')}", 
                             font=('Arial', 11), 
                             fg='#bdc3c7', bg='#34495e')
        dept_label.pack(anchor=tk.W, pady=2)
        
        # Position
        pos_label = tk.Label(info_frame, text=f"Position: {employee.get('position', 'N/A')}", 
                            font=('Arial', 11), 
                            fg='#bdc3c7', bg='#34495e')
        pos_label.pack(anchor=tk.W, pady=2)
        
        # Employee ID
        id_label = tk.Label(info_frame, text=f"Employee ID: {employee.get('employee_id', 'N/A')}", 
                           font=('Arial', 11), 
                           fg='#bdc3c7', bg='#34495e')
        id_label.pack(anchor=tk.W, pady=2)
        
        # Separator
        separator = tk.Frame(self.details_content, bg='#7f8c8d', height=2)
        separator.pack(fill=tk.X, pady=10)
        
        # Work statistics
        stats_label = tk.Label(self.details_content, text="Work Statistics", 
                              font=('Arial', 12, 'bold'), 
                              fg='#ecf0f1', bg='#34495e')
        stats_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Calculate and display statistics
        self.calculate_and_display_statistics(employee['name'])
    
    def calculate_and_display_statistics(self, employee_name):
        """Calculate and display work statistics for employee"""
        if not self.attendance_db:
            error_label = tk.Label(self.details_content, text="Attendance database not initialized.", 
                                  font=('Arial', 10), 
                                  fg='#e74c3c', bg='#34495e')
            error_label.pack(anchor=tk.W, pady=5)
            return
        try:
            from datetime import datetime, timedelta
            
            # Get current date
            today = datetime.now()
            
            # Calculate date ranges
            # Last week (7 days ago to today)
            last_week_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            last_week_end = today.strftime("%Y-%m-%d")
            
            # Current month
            month_start = today.replace(day=1).strftime("%Y-%m-%d")
            month_end = today.strftime("%Y-%m-%d")
            
            # Get attendance records
            week_records = self.attendance_db.get_attendance_report(
                last_week_start, last_week_end, employee_name)
            month_records = self.attendance_db.get_attendance_report(
                month_start, month_end, employee_name)
            
            # Calculate statistics
            # Hours worked last week
            total_hours_week = 0
            for record in week_records:
                if record.get('total_hours'):
                    total_hours_week += record['total_hours']
            
            # Days worked this month
            days_worked_month = len([r for r in month_records if r.get('check_in_time')])
            
            # Today's status
            today_str = today.strftime("%Y-%m-%d")
            today_records = self.attendance_db.get_attendance_report(
                today_str, today_str, employee_name)
            
            today_status = "Present" if today_records else "Not checked in"
            
            # Display statistics
            stats_frame = tk.Frame(self.details_content, bg='#34495e')
            stats_frame.pack(fill=tk.X, pady=5)
            
            # Today's status
            today_label = tk.Label(stats_frame, text=f"Today's Status: {today_status}", 
                                  font=('Arial', 11), 
                                  fg='#27ae60' if today_status == "Present" else '#e74c3c', 
                                  bg='#34495e')
            today_label.pack(anchor=tk.W, pady=2)
            
            # Hours last week
            hours_label = tk.Label(stats_frame, text=f"Hours worked last week: {total_hours_week:.1f} hours", 
                                  font=('Arial', 11), 
                                  fg='#3498db', bg='#34495e')
            hours_label.pack(anchor=tk.W, pady=2)
            
            # Days this month
            days_label = tk.Label(stats_frame, text=f"Days worked this month: {days_worked_month} days", 
                                 font=('Arial', 11), 
                                 fg='#9b59b6', bg='#34495e')
            days_label.pack(anchor=tk.W, pady=2)
            
            # Recent check-ins
            recent_label = tk.Label(self.details_content, text="Recent Check-ins", 
                                   font=('Arial', 12, 'bold'), 
                                   fg='#ecf0f1', bg='#34495e')
            recent_label.pack(anchor=tk.W, pady=(15, 5))
            
            # Show recent check-ins (last 5)
            recent_frame = tk.Frame(self.details_content, bg='#2c3e50', relief=tk.SUNKEN, bd=1)
            recent_frame.pack(fill=tk.X, pady=5)
            
            recent_records = week_records[-5:] if week_records else []
            
            if recent_records:
                for record in reversed(recent_records):
                    if record.get('check_in_time'):
                        date_str = record['date']
                        time_str = record['check_in_time'].split(' ')[1] if ' ' in record['check_in_time'] else record['check_in_time']
                        hours = f" ({record['total_hours']:.1f}h)" if record.get('total_hours') else ""
                        
                        record_text = f"• {date_str} at {time_str}{hours}"
                        record_label = tk.Label(recent_frame, text=record_text, 
                                               font=('Arial', 10), 
                                               fg='#ecf0f1', bg='#2c3e50')
                        record_label.pack(anchor=tk.W, padx=10, pady=2)
            else:
                no_records_label = tk.Label(recent_frame, text="No recent check-ins found", 
                                           font=('Arial', 10), 
                                           fg='#95a5a6', bg='#2c3e50')
                no_records_label.pack(anchor=tk.W, padx=10, pady=5)
        
            
        except Exception as e:
            error_label = tk.Label(self.details_content, text=f"Error calculating statistics: {e}", 
                                  font=('Arial', 10), 
                                  fg='#e74c3c', bg='#34495e')
            error_label.pack(anchor=tk.W, pady=5)
    
    def show_no_selection_message(self):
        """Show message when no employee is selected"""
        # Clear previous content
        for widget in self.details_content.winfo_children():
            widget.destroy()
        
        # No selection message
        message_label = tk.Label(self.details_content, 
                                text="Select an employee from the list\nto view details", 
                                font=('Arial', 12), 
                                fg='#95a5a6', bg='#34495e',
                                justify=tk.CENTER)
        message_label.pack(expand=True)
    
    def refresh_employee_data(self):
        """Refresh employee data"""
        self.load_employee_data()
        self.show_no_selection_message()
        CustomDialog.show_info(self.menu_window, "Refresh", "Employee data refreshed successfully")

        # Restore employee detail button
        #self.restore_button_on_window_close("employee_detail_btn")
    
    def delete_selected_employee(self):
        """Delete the currently selected employee with confirmation"""
        try:
            # Check if an employee is selected
            if not hasattr(self, 'employee_listbox') or not self.employee_listbox.curselection():
                CustomDialog.show_warning(self.menu_window, "No Selection", 
                                        "Please select an employee to delete.")
                return
            
            # Get selected employee
            selection = self.employee_listbox.curselection()[0]
            employee_data = self.employee_listbox.get(selection)
            
            # Extract employee name (format: "Name (ID) - Department")
            employee_name = employee_data.split(' (')[0].strip()
            
            # Confirmation dialog
            confirm_message = f"""Are you sure you want to delete employee '{employee_name}'?

This action will:
• Remove the employee from the database
• Delete ALL their attendance records
• Cannot be undone

Do you want to continue?"""
            
            if CustomDialog.ask_yes_no(self.menu_window, "Confirm Deletion", confirm_message):
                # Perform deletion
                if self.attendance_db and self.attendance_db.delete_employee(employee_name):
                    CustomDialog.show_info(self.menu_window, "Success", 
                                         f"Employee '{employee_name}' has been deleted successfully.")
                    
                    # Refresh the employee list
                    self.load_employee_data()
                    
                    # Show success message in details area
                    for widget in self.details_content.winfo_children():
                        widget.destroy()
                    
                    success_label = tk.Label(self.details_content, 
                                           text=f"Employee '{employee_name}'\nsuccessfully deleted", 
                                           font=('Arial', 16, 'bold'), 
                                           fg='#27ae60', bg='#34495e')
                    success_label.pack(expand=True)
                    
                else:
                    CustomDialog.show_error(self.menu_window, "Error", 
                                          f"Failed to delete employee '{employee_name}'. Please try again.")
            
        except Exception as e:
            print(f"Error deleting employee: {e}")
            CustomDialog.show_error(self.menu_window, "Error", f"An error occurred while deleting the employee: {e}")
  
    def show_todays_checkins(self):
        """Show detailed view of today's check-ins"""
        if not self.attendance_db:
            CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            
            if not checkins:
                CustomDialog.show_info(self.menu_window, "Today's Check-ins", "No check-ins recorded for today.")
                return
            
            # Create detailed report
            report = f"Today's Check-ins ({today})\n\n"
            report += f"Total Check-ins: {len(checkins)}\n\n"
            
            # Sort by check-in time
            checkins.sort(key=lambda x: x['check_in_time'])
            
            for i, record in enumerate(checkins, 1):
                name = record['name']
                check_in_time = record['check_in_time']
                
                # Format time
                if isinstance(check_in_time, str):
                    try:
                        time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                        formatted_time = time_obj.strftime("%H:%M:%S")
                    except:
                        formatted_time = check_in_time
                else:
                    formatted_time = str(check_in_time)
                
                report += f"{i}. {name} - {formatted_time}\n"
            
            CustomDialog.show_info(self.menu_window,"Today's Check-ins", report)
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to get today's check-ins: {e}")
    def show_employee_list(self):
        """Show list of all registered employees"""
        if not self.attendance_db:
            CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
            return
        
        try:
            employees = self.attendance_db.get_employees()
            
            if not employees:
                CustomDialog.show_info(self.menu_window,"Employee List", "No employees registered in the system.")
                return
            
            report = f"Registered Employees ({len(employees)} total)\n\n"
            
            for i, employee in enumerate(employees, 1):
                name = employee['name']
                dept = employee.get('department', 'N/A')
                position = employee.get('position', 'N/A')
                report += f"{i}. {name}\n   Department: {dept}\n   Position: {position}\n\n"
            
            CustomDialog.show_info(self.menu_window,"Employee List", report)
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to get employee list: {e}")

    def show_add_employee(self):
        """Show add employee dialog"""
        self.show_add_employee_dialog()
    
    def show_add_employee_dialog(self):
        """Show dialog to add a new employee"""
        # Create dialog window
        dialog = tk.Toplevel(self.menu_window)
        dialog.grab_set()
        dialog.title("Add New Employee")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        dialog.transient(self.menu_window)
        
        # Center dialog relative to parent
        dialog.update_idletasks()
        width = 500
        height = 450
        
        # Get parent window position and size
        if self.menu_window:
            self.menu_window.update_idletasks()
            parent_x = self.menu_window.winfo_x()
            parent_y = self.menu_window.winfo_y()
            parent_width = self.menu_window.winfo_width()
            parent_height = self.menu_window.winfo_height()
        else:
            parent_x = parent_y = parent_width = parent_height = 0
        
        # Calculate center position relative to parent
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Add New Employee", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Form content
        content_frame = tk.Frame(form_frame, bg='#34495e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form fields with virtual keyboard support
        fields = {}
        field_vars = {}
        
        # Name field (required)
        name_label = tk.Label(content_frame, text="Name *", 
                             font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        field_vars['name'] = tk.StringVar()
        fields['name'] = tk.Entry(content_frame, textvariable=field_vars['name'], 
                                 font=('Arial', 12), 
                                 bg='#ffffff', fg='#2c3e50', width=40)
        fields['name'].pack(fill=tk.X, pady=(0, 15))
        fields['name'].focus_set()
        
        # Employee ID field
        id_label = tk.Label(content_frame, text="Employee ID", 
                           font=('Arial', 12, 'bold'), 
                           fg='#ecf0f1', bg='#34495e')
        id_label.pack(anchor=tk.W, pady=(0, 5))
        
        field_vars['employee_id'] = tk.StringVar()
        fields['employee_id'] = tk.Entry(content_frame, textvariable=field_vars['employee_id'],
                                        font=('Arial', 12), 
                                        bg='#ffffff', fg='#2c3e50', width=40)
        fields['employee_id'].pack(fill=tk.X, pady=(0, 15))
        
        # Department field
        dept_label = tk.Label(content_frame, text="Department", 
                             font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        dept_label.pack(anchor=tk.W, pady=(0, 5))
        
        field_vars['department'] = tk.StringVar()
        fields['department'] = tk.Entry(content_frame, textvariable=field_vars['department'],
                                       font=('Arial', 12), 
                                       bg='#ffffff', fg='#2c3e50', width=40)
        fields['department'].pack(fill=tk.X, pady=(0, 15))
        
        # Position field
        pos_label = tk.Label(content_frame, text="Position", 
                            font=('Arial', 12, 'bold'), 
                            fg='#ecf0f1', bg='#34495e')
        pos_label.pack(anchor=tk.W, pady=(0, 5))
        
        field_vars['position'] = tk.StringVar()
        fields['position'] = tk.Entry(content_frame, textvariable=field_vars['position'],
                                     font=('Arial', 12), 
                                     bg='#ffffff', fg='#2c3e50', width=40)
        fields['position'].pack(fill=tk.X, pady=(0, 15))
        
        # Set up virtual keyboards for all entry fields
        for field_name, entry_widget in fields.items():
            self.setup_virtual_keyboard_for_entry(entry_widget, field_vars[field_name], main_frame)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X)
        
        # Result storage
        result = {'success': False}
        
        def on_save():
            """Handle save button click"""
            name = field_vars['name'].get().strip()
            employee_id = field_vars['employee_id'].get().strip() or None
            department = field_vars['department'].get().strip() or None
            position = field_vars['position'].get().strip() or None
            
            # Validate required fields
            if not name:
                CustomDialog.show_error(dialog, "Validation Error", "Name is required!")
                fields['name'].focus_set()
                return
            
            try:
                # Add employee to database
                success = self.attendance_db.add_employee(
                    name=name,
                    employee_id=employee_id,
                    department=department,
                    position=position
                )
                
                if success:
                    result['success'] = True
                    CustomDialog.show_info(dialog, "Success", f"Employee '{name}' added successfully!")
                    self.cleanup_keyboards()
                    dialog.destroy()
                else:
                    CustomDialog.show_error(dialog, "Error", f"Employee '{name}' already exists!")
                    
            except Exception as e:
                CustomDialog.show_error(dialog, "Database Error", f"Failed to add employee: {e}")
        
        def on_cancel():
            """Handle cancel button click"""
            self.cleanup_keyboards()
            dialog.destroy()
        
        # Save button
        save_btn = tk.Button(button_frame, text="Save Employee", 
                            command=on_save,
                            font=('Arial', 14, 'bold'),
                            bg='#27ae60', fg='white',
                            width=15, height=2,
                            relief=tk.RAISED, bd=3,
                            cursor='hand2')
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=on_cancel,
                              font=('Arial', 14, 'bold'),
                              bg='#e74c3c', fg='white',
                              width=15, height=2,
                              relief=tk.RAISED, bd=3,
                              cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        
        # Handle window close
        def on_window_close():
            self.cleanup_keyboards()
            on_cancel()
        dialog.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Bind Enter and Escape keys
        def on_enter(event):
            on_save()
        
        def on_escape(event):
            on_cancel()
        
        dialog.bind('<Return>', on_enter)
        dialog.bind('<Escape>', on_escape)
        
        # Focus and wait
        dialog.focus()
        dialog.wait_window()
        
        return result.get('success', False)

    def show_edit(self):
        # Clear the current frame and show edit interface
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.edit_todays_checkins()
    
    def edit_todays_checkins(self):
        """Edit today's check-ins with video pause and deletion options - shows all employees"""
        if not self.attendance_db:
            CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get all employees
            all_employees = self.attendance_db.get_employees()
            
            # Get today's attendance records
            attendance_records = self.attendance_db.get_attendance_report(today, today)
            
            # Create a dictionary of attendance records by employee name
            attendance_dict = {}
            for record in attendance_records:
                attendance_dict[record['name']] = record
            
            # Combine all employees with their attendance status
            combined_data = []
            
            # Add not checked-in employees first
            for employee in all_employees:
                if employee['name'] not in attendance_dict:
                    combined_data.append({
                        'name': employee['name'],
                        'check_in_time': None,
                        'check_out_time': None,
                        'status': 'Not Checked In',
                        'total_hours': None,
                        'date': today,
                        'is_checked_in': False
                    })
            
            # Add checked-in employees, sorted by latest check-in to oldest
            checked_in_employees = []
            for employee in all_employees:
                if employee['name'] in attendance_dict:
                    record = attendance_dict[employee['name']]
                    record['is_checked_in'] = True
                    checked_in_employees.append(record)
            
            # Sort checked-in employees by check-in time (latest first)
            checked_in_employees.sort(key=lambda x: x.get('check_in_time', ''), reverse=True)
            
            # Combine: not checked-in first, then checked-in (latest to oldest)
            combined_data.extend(checked_in_employees)
            
            # Create edit window with all employee data
            self.create_edit_checkins_window(combined_data)
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window, "Error", f"Failed to load employee data: {e}")
    
    def show_checkin(self):
        # Clear the current frame and show checkin photos interface
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.show_checkin_photos()

    def close_edit_window(self):
      if self.menu_window:
        for widget in self.menu_window.winfo_children():
            widget.destroy()
        self.show_menu()

    def create_edit_checkins_window(self, checkins):
    
        # Main container
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title (larger font)
        title_label = tk.Label(main_frame, text="Today's Employee Attendance", 
                              font=('Arial', 22, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Instructions (larger font)
        instruction_label = tk.Label(main_frame, 
                                   text="All employees shown: Not checked-in employees first, then latest check-ins.\nClick entry to delete check-in record. Video is paused during editing.",
                                   font=('Arial', 14), 
                                   fg='#bdc3c7', bg='#2c3e50')
        instruction_label.pack(pady=(0, 15))
        
        # Create frame for table and scrollbar
        table_frame = tk.Frame(main_frame, bg='#2c3e50')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create Treeview for table display
        columns = ('name', 'check_in', 'check_out', 'status')
        self.employee_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=18)
        
        # Define column headings and widths
        self.employee_table.heading('name', text='Employee Name')
        self.employee_table.heading('check_in', text='Check-In Time')
        self.employee_table.heading('check_out', text='Check-Out Time')
        self.employee_table.heading('status', text='Status')
        
        # Configure column widths
        self.employee_table.column('name', width=200, minwidth=150)
        self.employee_table.column('check_in', width=120, minwidth=100)
        self.employee_table.column('check_out', width=120, minwidth=100)
        self.employee_table.column('status', width=150, minwidth=100)
        
        # Configure table styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', 
                       background='#34495e',
                       foreground='#ecf0f1',
                       fieldbackground='#34495e',
                       font=('Arial', 12))
        style.configure('Treeview.Heading',
                       background='#2c3e50',
                       foreground='#ecf0f1',
                       font=('Arial', 12, 'bold'))
        style.map('Treeview', 
                 background=[('selected', '#4a6741')])
        
        # Scrollbar for table
        scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.employee_table.yview)
        self.employee_table.config(yscrollcommand=scrollbar.set)
         
        # Pack table and scrollbar
        self.employee_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate table with employee data
        self.populate_employee_table(checkins)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Delete button (larger font) with click protection
        delete_button = tk.Button(button_frame, text="Delete Selected", 
                                command=self.delete_selected_checkin,
                                font=('Arial', 16, 'bold'),
                                bg='#e74c3c', fg='white',
                                relief=tk.RAISED, bd=3,
                                cursor='hand2')
        delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button (larger font) with click protection
        refresh_button = tk.Button(button_frame, text="Refresh List", 
                                 command=self.refresh_checkins_list,
                                 font=('Arial', 16, 'bold'),
                                 bg='#3498db', fg='white',
                                 relief=tk.RAISED, bd=3,
                                 cursor='hand2')
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button (larger font) with click protection
        close_button = tk.Button(button_frame, text="Close", 
                               command=self.close_edit_window,
                               font=('Arial', 16, 'bold'),
                               bg='#95a5a6', fg='white',
                               relief=tk.RAISED, bd=3,
                               cursor='hand2')
        close_button.pack(side=tk.RIGHT)
        
        # Bind double-click event
        self.employee_table.bind('<Double-Button-1>', self.on_checkin_double_click)
        
        # Store checkins data for reference
        self.edit_checkins_data = checkins
    def refresh_checkins_list(self):
        """Refresh the check-ins list - shows all employees with their attendance status"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window, "Error", "Attendance database not initialized.")
            return
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get all employees
            all_employees = self.attendance_db.get_employees()
            
            # Get today's attendance records
            attendance_records = self.attendance_db.get_attendance_report(today, today)
            
            # Create a dictionary of attendance records by employee name
            attendance_dict = {}
            for record in attendance_records:
                attendance_dict[record['name']] = record
            
            # Combine all employees with their attendance status
            combined_data = []
            
            # Add not checked-in employees first
            for employee in all_employees:
                if employee['name'] not in attendance_dict:
                    combined_data.append({
                        'name': employee['name'],
                        'check_in_time': None,
                        'check_out_time': None,
                        'status': 'Not Checked In',
                        'total_hours': None,
                        'date': today,
                        'is_checked_in': False
                    })
            
            # Add checked-in employees, sorted by latest check-in to oldest
            checked_in_employees = []
            for employee in all_employees:
                if employee['name'] in attendance_dict:
                    record = attendance_dict[employee['name']]
                    record['is_checked_in'] = True
                    checked_in_employees.append(record)
            
            # Sort checked-in employees by check-in time (latest first)
            checked_in_employees.sort(key=lambda x: x.get('check_in_time', ''), reverse=True)
            
            # Combine: not checked-in first, then checked-in (latest to oldest)
            combined_data.extend(checked_in_employees)
            
            # Store and populate the updated data
            self.edit_checkins_data = combined_data
            self.populate_employee_table(combined_data)
            
            CustomDialog.show_info(self.menu_window, "Refresh Complete", f"List refreshed. {len(all_employees)} total employees, {len(checked_in_employees)} checked in.")
                
        except Exception as e:
            CustomDialog.show_error(self.menu_window, "Error", f"Failed to refresh list: {e}")
    
 
    



    def populate_employee_table(self, employee_data):
        """Populate the table with employee entries including check-out time and status"""
        self.employee_table.delete(*self.employee_table.get_children())
        
        for record in employee_data:
            name = record['name']
            check_in_time = record.get('check_in_time')
            check_out_time = record.get('check_out_time')
            
            # Format check-in time
            if check_in_time:
                if isinstance(check_in_time, str):
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                        formatted_check_in = time_obj.strftime("%H:%M:%S")
                    except:
                        formatted_check_in = check_in_time
                else:
                    formatted_check_in = str(check_in_time)
            else:
                formatted_check_in = "Not Checked In"
            
            # Format check-out time
            if check_out_time:
                if isinstance(check_out_time, str):
                    try:
                        from datetime import datetime
                        time_obj = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:%S")
                        formatted_check_out = time_obj.strftime("%H:%M:%S")
                    except:
                        formatted_check_out = check_out_time
                else:
                    formatted_check_out = str(check_out_time)
            else:
                formatted_check_out = "Not Checked Out" if check_in_time else "N/A"
            
            # Determine status display
            if not check_in_time:
                status_display = "Not Checked In"
            elif check_out_time:
                status_display = "Checked Out"
            else:
                status_display = "Checked In"
            
            # Insert row into table
            self.employee_table.insert('', 'end', values=(name, formatted_check_in, formatted_check_out, status_display))
    
    def on_checkin_double_click(self, event):
        """Handle double-click on check-in entry"""
        selection = self.employee_table.selection()
        if selection:
            self.delete_selected_checkin()
    


    def delete_selected_checkin(self):
        """Delete the selected check-in entry - only allows deletion of actual check-in records"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window, "Error", "Attendance database not initialized.")
            return
            
        selection = self.employee_table.selection()
        print(f"Selection: {selection}")
        
        if not selection:
            CustomDialog.show_warning(self.menu_window, "Warning", "Please select an entry to delete.")
            return
        
        # Get the selected item
        selected_item = selection[0]
        item_values = self.employee_table.item(selected_item, 'values')
        
        if not item_values:
            CustomDialog.show_error(self.menu_window, "Error", "Invalid selection.")
            return
        
        # Extract employee name from the table row
        name = item_values[0]
        formatted_check_in = item_values[1]
        status_display = item_values[3]
        
        # Find the corresponding record in our data
        record_to_delete = None
        for record in self.edit_checkins_data:
            if record['name'] == name:
                record_to_delete = record
                break
        
        if not record_to_delete:
            CustomDialog.show_error(self.menu_window, "Error", "Could not find employee record.")
            return
        
        check_in_time = record_to_delete.get('check_in_time')
        
        # Check if this is a "Not Checked In" employee
        if not check_in_time or not record_to_delete.get('is_checked_in', True):
            CustomDialog.show_info(self.menu_window, "Cannot Delete", 
                                 f"{name} has not checked in today.\n\n"
                                 "Only actual check-in records can be deleted.")
            return
        
        print(f"Attempting to delete check-in for {name} at {check_in_time}")

        # Confirm deletion using the formatted time from the table
        result = CustomDialog.ask_yes_no(self.menu_window, "Confirm Deletion", 
                                   f"Are you sure you want to delete this check-in?\n\n"
                                   f"Employee: {name}\n"
                                   f"Check-in Time: {formatted_check_in}\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                print(f"User confirmed deletion, calling database delete...")
                # Delete from database
                success = self.attendance_db.delete_checkin(name, check_in_time)
                print(f"Database delete result: {success}")
                    
                if success:
                    print("Database deletion successful, updating UI...")
                    
                    # Refresh using the same logic as refresh_checkins_list
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    # Get all employees
                    all_employees = self.attendance_db.get_employees()
                    
                    # Get today's attendance records
                    attendance_records = self.attendance_db.get_attendance_report(today, today)
                    
                    # Create a dictionary of attendance records by employee name
                    attendance_dict = {}
                    for record in attendance_records:
                        attendance_dict[record['name']] = record
                    
                    # Combine all employees with their attendance status
                    combined_data = []
                    
                    # Add not checked-in employees first
                    for employee in all_employees:
                        if employee['name'] not in attendance_dict:
                            combined_data.append({
                                'name': employee['name'],
                                'check_in_time': None,
                                'check_out_time': None,
                                'status': 'Not Checked In',
                                'total_hours': None,
                                'date': today,
                                'is_checked_in': False
                            })
                    
                    # Add checked-in employees, sorted by latest check-in to oldest
                    checked_in_employees = []
                    for employee in all_employees:
                        if employee['name'] in attendance_dict:
                            record = attendance_dict[employee['name']]
                            record['is_checked_in'] = True
                            checked_in_employees.append(record)
                    
                    # Sort checked-in employees by check-in time (latest first)
                    checked_in_employees.sort(key=lambda x: x.get('check_in_time', ''), reverse=True)
                    
                    # Combine: not checked-in first, then checked-in (latest to oldest)
                    combined_data.extend(checked_in_employees)
                    
                    # Update data and UI
                    self.edit_checkins_data = combined_data
                    
                    print(f"Refreshed data from database, now have {len(self.edit_checkins_data)} total employees")
                    
                    # Clear table completely and repopulate
                    self.employee_table.delete(*self.employee_table.get_children())
                    self.populate_employee_table(self.edit_checkins_data)
                    
                    CustomDialog.show_info(self.menu_window, "Success", f"Check-in for {name} deleted successfully.")
                    print("Table repopulated with remaining data")
                else:
                    print("Database deletion failed")
                    CustomDialog.show_error(self.menu_window, "Error", f"Failed to delete check-in for {name}.")
                     
            except Exception as e:
                print(f"Exception during deletion: {e}")
                CustomDialog.show_error(self.menu_window, "Error", f"Failed to delete check-in: {e}")
        else:
            print("User cancelled deletion")
    

    def sync_dataset_with_database(self):
        """Sync existing dataset users with the attendance database"""
        if not self.attendance_db:
            print("No attendance database available for sync")
            return
            
        try:
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
                        department="Kitchen",
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
    

    def show_checkin_photos(self):

        if not self.attendance_db:
            CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
            return

        # Bind window close event
        # Initialize state variables
        self.current_page = 0
        self.dates_per_page = 30
        self.selected_date = None
        
        # Main container
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title (larger font)
        title_label = tk.Label(main_frame, text="Check-in Details", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Create main content frame
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left section - Date/Employee List
        self.create_checkin_left_sections(content_frame)
        
        # Right section - Check-in Photo
        self.create_checkin_right_section(content_frame)
        
        # Bottom pagination and controls
        self.create_checkin_bottom_controls(main_frame)
        
        # Load initial data
        self.load_checkin_dates()
    
    def create_checkin_left_sections(self, parent):
        """Create left sections for dates (upper) and employees (lower)"""
        # Left container frame
        left_container = tk.Frame(parent, bg='#2c3e50')
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Upper left section - Dates
        self.create_dates_section(left_container)
        
        # Lower left section - Employees
        self.create_employees_section(left_container)
    
    def create_dates_section(self, parent):
        """Create upper left section for dates"""
        # Date section frame
        date_frame = tk.Frame(parent, bg='#2c3e50')
        date_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Date header (larger font)
        date_header = tk.Label(date_frame, text="Check-in Dates", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        date_header.pack(pady=(0, 10))
        
        # Date list container
        date_list_container = tk.Frame(date_frame, bg='#2c3e50')
        date_list_container.pack(fill=tk.BOTH, expand=True)
        
        # Date listbox (larger for easier selection)
        self.checkin_listbox = tk.Listbox(date_list_container, 
                                         font=('Arial', 16, 'bold'),
                                         bg='#34495e', 
                                         fg='#ecf0f1',
                                         selectbackground='#3498db',
                                         selectforeground='white',
                                         relief=tk.SUNKEN,
                                         bd=2,
                                         height=10)
        
        # Date scrollbar
        date_scrollbar = tk.Scrollbar(date_list_container, orient=tk.VERTICAL, 
                                     command=self.checkin_listbox.yview)
        self.checkin_listbox.config(yscrollcommand=date_scrollbar.set)
        
        # Pack date components
        self.checkin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        date_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.checkin_listbox.bind('<<ListboxSelect>>', self.on_date_select)
    
    def create_employees_section(self, parent):
        """Create lower left section for employees"""
        # Employee section frame
        employee_frame = tk.Frame(parent, bg='#2c3e50')
        employee_frame.pack(fill=tk.BOTH, expand=True)
        
        # Employee header (larger font)
        self.employee_header = tk.Label(employee_frame, text="Employees (Select a date)", 
                                       font=('Arial', 18, 'bold'), 
                                       fg='#ecf0f1', bg='#2c3e50')
        self.employee_header.pack(pady=(0, 10))
        
        # Employee list container
        employee_list_container = tk.Frame(employee_frame, bg='#2c3e50')
        employee_list_container.pack(fill=tk.BOTH, expand=True)
        
        # Employee listbox (larger for easier selection)
        self.employee_listbox = tk.Listbox(employee_list_container, 
                                          font=('Arial', 16, 'bold'),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#27ae60',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2,
                                          height=10)
        
        # Employee scrollbar
        employee_scrollbar = tk.Scrollbar(employee_list_container, orient=tk.VERTICAL, 
                                         command=self.employee_listbox.yview)
        self.employee_listbox.config(yscrollcommand=employee_scrollbar.set)
        
        # Pack employee components
        self.employee_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        employee_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.employee_listbox.bind('<<ListboxSelect>>', self.on_employee_select)
        
        # Initial message
        self.employee_listbox.insert(tk.END, "Select a date to view employees")
    
    def on_date_select(self, event):
        """Handle date selection"""
        selection = self.checkin_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index < len(self.checkin_dates_data):
            selected_date = self.checkin_dates_data[index]
            self.load_employees_for_selected_date(selected_date)
    
    def on_employee_select(self, event):
        """Handle employee selection"""
        selection = self.employee_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if hasattr(self, 'employee_checkin_data') and index < len(self.employee_checkin_data):
            selected_record = self.employee_checkin_data[index]
            self.show_checkin_photo(selected_record)
    
    def load_employees_for_selected_date(self, selected_date):
        """Load employees for the selected date"""
        try:
            if not self.attendance_db:
                CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
                return

            # Get check-ins for selected date
            records = self.attendance_db.get_attendance_report(selected_date, selected_date)
            checkins = [r for r in records if r.get('check_in_time')]

            # Update employee header
            try:
                formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').strftime('%B %d, %Y')
            except:
                formatted_date = selected_date
            self.employee_header.config(text=f"Employees on {formatted_date}")
            
            # Clear and populate employee listbox
            self.employee_listbox.delete(0, tk.END)
            self.employee_checkin_data = checkins
            
            if not checkins:
                self.employee_listbox.insert(tk.END, "No check-ins found for this date")
                return
            
            # Sort by check-in time
            checkins.sort(key=lambda x: x['check_in_time'])
            
            # Add employees to listbox
            for record in checkins:
                name = record['name']
                check_in_time = record['check_in_time']
                
                # Format time
                try:
                    time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                    formatted_time = time_obj.strftime("%H:%M:%S")
                except:
                    formatted_time = check_in_time
                
                display_text = f"{name} - {formatted_time}"
                self.employee_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to load employees for date: {e}")
    
    def create_checkin_right_section(self, parent):
        """Create right section for check-in photos"""
        # Right frame
        right_frame = tk.Frame(parent, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Photo section label (larger font)
        photo_label = tk.Label(right_frame, text="Check-in Photo", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        photo_label.pack(pady=(0, 10))
        
        # Photo container
        self.photo_container = tk.Frame(right_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        self.photo_container.pack(fill=tk.BOTH, expand=True)
        
        # Photo content frame
        self.photo_content = tk.Frame(self.photo_container, bg='#34495e')
        self.photo_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Initial message
        self.show_no_photo_message()
    
    def create_checkin_bottom_controls(self, parent):
        """Create bottom controls for pagination and navigation"""
        # Bottom frame
        bottom_frame = tk.Frame(parent, bg='#2c3e50')
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left side - Navigation buttons
        nav_frame = tk.Frame(bottom_frame, bg='#2c3e50')
        nav_frame.pack(side=tk.LEFT)
        
        # Back button (initially hidden)
        self.back_button = tk.Button(nav_frame, text="← Back to Dates", 
                                    command=self.back_to_dates,
                                    font=('Arial', 10, 'bold'),
                                    bg='#95a5a6', fg='white',
                                    width=15, height=2,
                                    relief=tk.RAISED, bd=2)
        # Don't pack initially
        
        # Right side - Pagination and close
        control_frame = tk.Frame(bottom_frame, bg='#2c3e50')
        control_frame.pack(side=tk.RIGHT)
        
        # Pagination frame
        self.pagination_frame = tk.Frame(control_frame, bg='#2c3e50')
        self.pagination_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Page info label
        self.page_info_label = tk.Label(self.pagination_frame, text="Page 1", 
                                       font=('Arial', 10), 
                                       fg='#ecf0f1', bg='#2c3e50')
        self.page_info_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Previous page button
        self.prev_button = tk.Button(self.pagination_frame, text="◀ Prev", 
                                    command=self.prev_page,
                                    font=('Arial', 9, 'bold'),
                                    bg='#3498db', fg='white',
                                    width=8, height=1,
                                    relief=tk.RAISED, bd=2)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Next page button
        self.next_button = tk.Button(self.pagination_frame, text="Next ▶", 
                                    command=self.next_page,
                                    font=('Arial', 9, 'bold'),
                                    bg='#3498db', fg='white',
                                    width=8, height=1,
                                    relief=tk.RAISED, bd=2)
        self.next_button.pack(side=tk.LEFT)
        
        # Close button
        close_btn = tk.Button(control_frame, text="Close", 
                             command=self.close_checkin,
                             font=('Arial', 10, 'bold'),
                             bg='#e74c3c', fg='white',
                             width=20, height=2,
                             relief=tk.RAISED, bd=2)
        close_btn.pack(side=tk.RIGHT)
    def close_checkin(self):
        # Clear the current frame and show main menu
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.show_menu()



    def load_checkin_dates(self):
        """Load check-in dates with pagination"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window,"Error", "Attendance database not initialized.")
            return
        try:
            from datetime import datetime, timedelta
            
            # Get all dates with check-ins
            records = self.attendance_db.get_attendance_report()
            checkin_dates = set()
            
            for record in records:
                if record.get('check_in_time'):
                    checkin_dates.add(record['date'])
            
            # Sort dates (newest first)
            sorted_dates = sorted(list(checkin_dates), reverse=True)
            
            # Paginate
            start_idx = self.current_page * self.dates_per_page
            end_idx = start_idx + self.dates_per_page
            page_dates = sorted_dates[start_idx:end_idx]
            
            # Clear and populate listbox
            self.checkin_listbox.delete(0, tk.END)
            self.checkin_dates_data = page_dates
            
            if not page_dates:
                self.checkin_listbox.insert(tk.END, "No check-ins found")
                return
            
            # Add dates to listbox
            for date in page_dates:
                # Get count of check-ins for this date
                date_records = [r for r in records if r['date'] == date and r.get('check_in_time')]
                count = len(date_records)
                
                # Format date display
                try:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    display_text = f"{formatted_date} ({count} check-ins)"
                except:
                    display_text = f"{date} ({count} check-ins)"
                
                self.checkin_listbox.insert(tk.END, display_text)
            
            # Update pagination controls
            self.update_pagination_controls(len(sorted_dates))
            
            # Set current view
            self.hide_back_button()
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to load check-in dates: {e}")
    def get_clean_name(self, name):
        """Convert user name to clean filename format"""
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')
        return clean_name
    
    def show_checkin_photo(self, record):
        """Show check-in photo for selected employee"""
        # Clear previous content
        for widget in self.photo_content.winfo_children():
            widget.destroy()
        
        try:
            # Get employee info
            name = record['name']
            check_in_time = record['check_in_time']
            date = record['date']
            
            # Format time for filename
            time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
            formatted_time = time_obj.strftime("%H-%M-%S")
            
            # Clean name for filename
            clean_name = self.get_clean_name(name)
            
            # Construct photo path
            photo_path = os.path.join("CheckinPhoto", date, f"{clean_name}_{formatted_time}.jpg")
            
            # Employee info
            info_frame = tk.Frame(self.photo_content, bg='#34495e')
            info_frame.pack(fill=tk.X, pady=(0, 15))
            
            name_label = tk.Label(info_frame, text=f"Employee: {name}", 
                                 font=('Arial', 12, 'bold'), 
                                 fg='#ecf0f1', bg='#34495e')
            name_label.pack(anchor=tk.W)
            
            time_label = tk.Label(info_frame, text=f"Check-in Time: {time_obj.strftime('%H:%M:%S')}", 
                                 font=('Arial', 10), 
                                 fg='#bdc3c7', bg='#34495e')
            time_label.pack(anchor=tk.W)
            
            date_label = tk.Label(info_frame, text=f"Date: {time_obj.strftime('%B %d, %Y')}", 
                                 font=('Arial', 10), 
                                 fg='#bdc3c7', bg='#34495e')
            date_label.pack(anchor=tk.W)
            
            # Photo frame
            photo_frame = tk.Frame(self.photo_content, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
            photo_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            # Try to load and display photo
            if os.path.exists(photo_path):
                try:
                    # Load image
                    import cv2
                    from PIL import Image, ImageTk
                    
                    # Read image
                    img = cv2.imread(photo_path)
                    if img is not None:
                        # Convert color
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        
                        # Resize image to fit display
                        pil_img = Image.fromarray(img_rgb)
                        
                        # Calculate size to fit in frame (max 400x400)
                        max_size = 400
                        img_width, img_height = pil_img.size
                        
                        if img_width > max_size or img_height > max_size:
                            # Calculate scaling factor
                            scale = min(max_size / img_width, max_size / img_height)
                            new_width = int(img_width * scale)
                            new_height = int(img_height * scale)
                            pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Convert to PhotoImage
                        photo = ImageTk.PhotoImage(pil_img)
                        
                        # Display image
                        img_label = tk.Label(photo_frame, image=photo, bg='#2c3e50')
                        # Store reference to prevent garbage collection
                        self.current_photo_ref = photo
                        img_label.pack(expand=True)
                        
                except Exception as e:
                    # Error loading image
                    error_label = tk.Label(photo_frame, text=f"Error loading image: {e}", 
                                         font=('Arial', 11), 
                                         fg='#e74c3c', bg='#2c3e50')
                    error_label.pack(expand=True)
            else:
                # No photo found
                no_photo_label = tk.Label(photo_frame, text="No check-in photo found", 
                                         font=('Arial', 11), 
                                         fg='#95a5a6', bg='#2c3e50')
                no_photo_label.pack(expand=True)
                
                # Show expected path for debugging
                path_label = tk.Label(photo_frame, text=f"Expected path: {photo_path}", 
                                     font=('Arial', 9), 
                                     fg='#7f8c8d', bg='#2c3e50')
                path_label.pack(pady=(10, 0))
                
        except Exception as e:
            error_label = tk.Label(self.photo_content, text=f"Error displaying photo: {e}", 
                                  font=('Arial', 11), 
                                  fg='#e74c3c', bg='#34495e')
            error_label.pack(expand=True)
    
    def show_no_photo_message(self):
        """Show message when no photo is selected"""
        for widget in self.photo_content.winfo_children():
            widget.destroy()
        
        message_label = tk.Label(self.photo_content, 
                                text="Select an employee from the list\nto view their check-in photo", 
                                font=('Arial', 12), 
                                fg='#95a5a6', bg='#34495e',
                                justify=tk.CENTER)
        message_label.pack(expand=True)
    
   
    def update_pagination_controls(self, total_items):
        """Update pagination controls"""
        total_pages = (total_items + self.dates_per_page - 1) // self.dates_per_page
        current_page_num = self.current_page + 1
        
        # Update page info
        self.page_info_label.config(text=f"Page {current_page_num} of {total_pages}")
        
        # Update button states
        self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
    
    def hide_pagination_controls(self):
        """Hide pagination controls"""
        self.pagination_frame.pack_forget()
    
    def show_pagination_controls(self):
        """Show pagination controls"""
        self.pagination_frame.pack(side=tk.LEFT, padx=(0, 20))
    
    def show_back_button(self):
        """Show back button"""
        self.back_button.pack(side=tk.LEFT, padx=(0, 10))
    
    def hide_back_button(self):
        """Hide back button"""
        self.back_button.pack_forget()
    
    def back_to_dates(self):
        """Go back to dates view"""
        self.selected_date = None
        self.show_no_photo_message()
        self.hide_back_button()
        self.show_pagination_controls()
        self.load_checkin_dates()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_checkin_dates()
    
    def next_page(self):
        """Go to next page"""
        self.current_page += 1
        self.load_checkin_dates()
    
    def export_attendance_report(self):
        """Export attendance report"""
        # This method will be implemented with dependency injection
        pass
    def show_attendance_settings(self, parent):
        """Show attendance settings dialog"""

        parent.destroy()
        config = self.load_attendance_config()
        self.time_var= tk.StringVar(value=config.get("auto_checkout_time", "21:00"));
        self.show_attendance_settings_dialog()
    
    def load_attendance_config(self):


        """Load attendance configuration from file"""
        import json
        import os
        
        config_file = "attendance_config.json"
        default_config = {
            "auto_checkout_enabled": False,
            "auto_checkout_time": "18:00",
            "auto_checkout_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Ensure all required keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return default_config
        except Exception as e:
            print(f"Error loading attendance config: {e}")
            return default_config
    
    def save_attendance_config(self, config):
        """Save attendance configuration to file"""
        import json
        
        config_file = "attendance_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving attendance config: {e}")
            return False
    
    def show_attendance_settings_dialog(self):
        
        
    

        
        try:
            current_hour, current_minute = map(int, self.time_var.get().split(':'))
        except:
            current_hour, current_minute = 21, 0
        self.minute_var = tk.IntVar(value=current_minute)
        self.hour_var = tk.IntVar(value=current_hour)
        config = self.load_attendance_config()
        
        # Main frame
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Attendance Settings", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Settings content
        content_frame = tk.Frame(settings_frame, bg='#34495e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Auto Checkout Section
        auto_checkout_section = tk.LabelFrame(content_frame, text="Automatic Check-out", 
                                            font=('Arial', 14, 'bold'),
                                            fg='#ecf0f1', bg='#34495e',
                                            relief=tk.RAISED, bd=1)
        auto_checkout_section.pack(fill=tk.X, pady=(0, 15))
        
        # Auto checkout enable/disable
        auto_frame = tk.Frame(auto_checkout_section, bg='#34495e')
        auto_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Toggle switch for auto checkout
        auto_checkout_var = tk.BooleanVar(value=config.get("auto_checkout_enabled", False))
        
        auto_label = tk.Label(auto_frame, text="Enable Automatic Check-out:", 
                             font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        auto_label.pack(side=tk.LEFT)
        
        # Custom toggle button
        def toggle_auto_checkout():
            current = auto_checkout_var.get()
            auto_checkout_var.set(not current)
            update_toggle_button()
            update_time_fields()
        
        def update_toggle_button():
            if auto_checkout_var.get():
                toggle_btn.config(text="ON", bg='#27ae60', fg='white')
            else:
                toggle_btn.config(text="OFF", bg='#e74c3c', fg='white')
        
        def update_time_fields():
            state = tk.NORMAL if auto_checkout_var.get() else tk.DISABLED
            time_button.config(state=state)
            for day_data in day_checkboxes.values():
                day_data['widget'].config(state=tk.NORMAL if auto_checkout_var.get() else tk.DISABLED)
        
        toggle_btn = tk.Button(auto_frame, text="OFF",
                              command=toggle_auto_checkout,
                              font=('Arial', 12, 'bold'),
                              width=8, height=1,
                              relief=tk.RAISED, bd=2,
                              cursor='hand2')
        toggle_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Time setting
        time_frame = tk.Frame(auto_checkout_section, bg='#34495e')
        time_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        time_label = tk.Label(time_frame, text="Auto Check-out Time (24-hour format):", 
                             font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        time_label.pack(side=tk.LEFT)
        
        self.time_var = tk.StringVar(value=config.get("auto_checkout_time", "21:00"))
        
        def select_time():
            
     
            
            # Parse current time
            current_time = self.time_var.get()
     
            
            # Create time picker frame in the main window
            self.time_picker_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=3)
            self.time_picker_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Title
            title_label = tk.Label(self.time_picker_frame, text="Select Auto Check-out Time", 
                                  font=('Arial', 16, 'bold'), 
                                  fg='#ecf0f1', bg='#34495e')
            title_label.pack(pady=(15, 10))
            
            # Main time picker layout frame
            time_main_frame = tk.Frame(self.time_picker_frame, bg='#34495e')
            time_main_frame.pack(pady=(0, 15))
            
            # Time display frame (left side)
            time_display_frame = tk.Frame(time_main_frame, bg='#34495e')
            time_display_frame.pack(side=tk.LEFT, padx=(20, 30))
            
            # Hour section
            hour_frame = tk.Frame(time_display_frame, bg='#2c3e50', relief=tk.RAISED, bd=3)
            hour_frame.pack(side=tk.LEFT, padx=(0, 10))
            
            # Hour label
            hour_title = tk.Label(hour_frame, text="Hour", 
                                 font=('Arial', 12, 'bold'), 
                                 fg='#ecf0f1', bg='#2c3e50')
            hour_title.pack(pady=(10, 5))
            
            # Hour up button
  
            hour_up_btn = tk.Button(hour_frame, text="▲", 
                                   font=('Arial', 16, 'bold'),
                                   bg='#3498db', fg='white',
                                   width=4, height=1,
                                   command=lambda: self.change_hour( 1))
            hour_up_btn.pack(pady=5)
            
            # Hour display (giant label)
            hour_display = tk.Label(hour_frame, textvariable=self.hour_var,
                                   font=('Arial', 48, 'bold'),
                                   fg='#27ae60', bg='#2c3e50',
                                   width=3, height=2)
            hour_display.pack(pady=10)
            
            # Hour down button
            hour_down_btn = tk.Button(hour_frame, text="▼", 
                                     font=('Arial', 16, 'bold'),
                                     bg='#e74c3c', fg='white',
                                     width=4, height=1,
                                     command=lambda: self.change_hour( -1))
            hour_down_btn.pack(pady=(5, 10))
            
            # Colon separator
            colon_label = tk.Label(time_display_frame, text=":", 
                                  font=('Arial', 48, 'bold'), 
                                  fg='#ecf0f1', bg='#34495e')
            colon_label.pack(side=tk.LEFT, padx=15)
            
            # Minute section
            minute_frame = tk.Frame(time_display_frame, bg='#2c3e50', relief=tk.RAISED, bd=3)
            minute_frame.pack(side=tk.LEFT, padx=(10, 0))
            
            # Minute label
            minute_title = tk.Label(minute_frame, text="Minute", 
                                   font=('Arial', 12, 'bold'), 
                                   fg='#ecf0f1', bg='#2c3e50')
            minute_title.pack(pady=(10, 5))
            
            # Minute up button
   
            minute_up_btn = tk.Button(minute_frame, text="▲", 
                                     font=('Arial', 16, 'bold'),
                                     bg='#3498db', fg='white',
                                     width=4, height=1,
                                     command=lambda: self.change_minute(30))
            minute_up_btn.pack(pady=5)
            
            # Minute display (giant label)
            minute_display = tk.Label(minute_frame, text=f"{current_minute:02d}",
                                     font=('Arial', 48, 'bold'),
                                     fg='#27ae60', bg='#2c3e50',
                                     width=3, height=2)
            minute_display.pack(pady=10)
            
            # Minute down button
            minute_down_btn = tk.Button(minute_frame, text="▼", 
                                       font=('Arial', 16, 'bold'),
                                       bg='#e74c3c', fg='white',
                                       width=4, height=1,
                                       command=lambda: self.change_minute(-30))
            minute_down_btn.pack(pady=(5, 10))
            
            # Update minute display when variable changes
            def update_minute_display(*args):
                minute_display.config(text=f"{self.minute_var.get():02d}")
            self.minute_var.trace('w', update_minute_display)
            
            # Control buttons frame (right side)
            picker_button_frame = tk.Frame(time_main_frame, bg='#34495e')
            picker_button_frame.pack(side=tk.RIGHT, padx=(30, 20))
            
            def confirm_time():
        
                selected_time = f"{self.hour_var.get():02d}:{self.minute_var.get():02d}"
                self.time_var.set(selected_time)
                on_save()
                self.time_picker_frame.destroy()
            
            def cancel_time():
                
                on_cancel()
                self.time_picker_frame.destroy()
                
            
            # Confirm button (stacked vertically)
            confirm_btn = tk.Button(picker_button_frame, text="✓ Confirm Time", 
                                   command=confirm_time,
                                   font=('Arial', 12, 'bold'),
                                   bg='#27ae60', fg='white',
                                   width=15, height=2,
                                   relief=tk.RAISED, bd=3)
            confirm_btn.pack(pady=(10, 5))
            
            # Cancel button
            cancel_btn = tk.Button(picker_button_frame, text="✗ Cancel", 
                                  command=cancel_time,
                                  font=('Arial', 12, 'bold'),
                                  bg='#e74c3c', fg='white',
                                  width=15, height=2,
                                  relief=tk.RAISED, bd=3)
            cancel_btn.pack(pady=(5, 10))
            
            # Update button appearance
  
        # Set default value if not valid
        if not self.time_var.get() or ':' not in self.time_var.get():
            self.time_var.set("1:00")
        
        time_button = tk.Label(time_frame, text=f"{self.time_var.get()}",
                               font=('Arial', 12, 'bold'),
                               bg='#3498db', fg='white',
                               width=12, height=1,
                               relief=tk.RAISED, bd=2
                               )
        time_button.pack(side=tk.RIGHT, padx=(10, 0))
        select_time()
        # Days selection
        days_frame = tk.Frame(auto_checkout_section, bg='#34495e')
        days_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        days_label = tk.Label(days_frame, text="Auto Check-out Days:", 
                             font=('Arial', 12, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        days_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Day checkboxes
        days_checkbox_frame = tk.Frame(days_frame, bg='#34495e')
        days_checkbox_frame.pack(fill=tk.X)
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_checkboxes = {}
        enabled_days = config.get("auto_checkout_days", [])
        
        for i, (day, label) in enumerate(zip(days, day_labels)):
            day_var = tk.BooleanVar(value=day in enabled_days)
            day_cb = tk.Checkbutton(days_checkbox_frame, text=label,
                                   variable=day_var,
                                   font=('Arial', 11),
                                   fg='#ecf0f1', bg='#34495e',
                                   selectcolor='#2c3e50',
                                   activebackground='#34495e',
                                   activeforeground='#ecf0f1')
            day_cb.pack(side=tk.LEFT, padx=(0, 15))
            day_checkboxes[day] = {'var': day_var, 'widget': day_cb}
        
        # Initialize toggle button and field states
        update_toggle_button()
        update_time_fields()
        
        # Information section
        info_section = tk.LabelFrame(content_frame, text="Information", 
                                   font=('Arial', 14, 'bold'),
                                   fg='#ecf0f1', bg='#34495e',
                                   relief=tk.RAISED, bd=1)
        info_section.pack(fill=tk.X, pady=(0, 15))
        

        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X)
        
        def on_save():
            """Handle save button click"""
            try:
                # Get selected time (no validation needed since it's from dropdown)
               
                time_value = self.time_var.get().strip()
                if auto_checkout_var.get() and not time_value:
                    CustomDialog.show_error(main_frame, "Invalid Time", "Please select a time for auto check-out")
                    return
                
                # Get selected days
                selected_days = []
                for day, day_data in day_checkboxes.items():
                    if day_data['var'].get():
                        selected_days.append(day)
                
                # Create new config
                new_config = {
                    "auto_checkout_enabled": auto_checkout_var.get(),
                    "auto_checkout_time": time_value,
                    "auto_checkout_days": selected_days
                }
                
                # Save configuration
                if self.save_attendance_config(new_config):
                   
                    self.cleanup_keyboards()
                    # Go back to main menu
                    for widget in self.menu_window.winfo_children():
                        widget.destroy()
                    self.show_menu()
                else:
                    CustomDialog.show_error(self.menu_window, "Save Error", "Failed to save attendance settings!")
                    
            except Exception as e:
                CustomDialog.show_error(self.menu_window, "Error", f"Failed to save settings: {e}")
        
        def on_cancel():
            """Handle cancel button click"""
            
            self.cleanup_keyboards()
            # Go back to main menu
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.show_menu()
        
        # Save button
    
        
        # Handle window close
        def on_window_close():
            self.cleanup_keyboards()
            on_cancel()
        self.menu_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Bind Enter and Escape keys
        def on_enter(event):
            on_save()
        
        def on_escape(event):
            on_cancel()
        
        self.menu_window.bind('<Return>', on_enter)
        self.menu_window.bind('<Escape>', on_escape)
        
        # Focus on the main frame
        main_frame.focus()
    
    def show_camera_settings(self):
        """Show camera settings"""
        # This method will be implemented with dependency injection
        pass
    def start_capture(self):
        # Call the main UI's start_capture with menu window context
        try:
            self._injected_start_capture(self.menu_window)
        except TypeError:
            # Fallback if function doesn't accept arguments (default lambda)
            self.show_add_employee()
    def show_recognition_settings(self):
        """Show recognition settings"""
        # This method will be implemented with dependency injection
        pass
    
    def show_database_settings(self):
        """Show database settings"""
        # This method will be implemented with dependency injection
        pass
    
    def reset_system(self):
        """Reset system"""
        # This method will be implemented with dependency injection
        pass
    
    def cleanup_and_exit(self):
        """Exit system"""
        # This method will be implemented with dependency injection
        pass