import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
from ui_dialogs import CustomDialog
from attendance_database import AttendanceDatabase


class MenuManager:
    """Handles menu windows and UI management"""
    
    def __init__(self):
        self.menu_window = None
        self.current_page = 0
        self.dates_per_page = 30
        self.selected_date = None
        self.attendance_db = AttendanceDatabase()
    def show_main_menu_window(self, root):
        self.menu_window = tk.Toplevel(root)
        self.menu_window.grab_set()  
        self.menu_window.transient(root)
        
        self.menu_window.title("Face Recognition Attendance System - Main Menu")
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
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 20, 'height': 2,
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
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 20, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Edit Today's Check-ins button with click protection
        edit_btn = tk.Button(buttons_frame, text="Edit Today's Check-ins", 
                            command=self.show_edit,
                            bg='#e74c3c', fg='white', **button_config)
        edit_btn.pack(side=tk.LEFT)

        edit_employee_btn = tk.Button(buttons_frame, text="Employee Management", 
                            command=self.show_edit,
                            bg='#e74c3c', fg='white', **button_config)
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
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 20, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Camera Settings button with click protection
        camera_btn = tk.Button(buttons_frame, text="Camera Settings", 
                              command=self.show_camera_settings,
                              bg='#34495e', fg='white', **button_config)
        camera_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Recognition Settings button with click protection
        recognition_btn = tk.Button(buttons_frame, text="Recognition Settings", 
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
        button_config = {'font': ('Arial', 14, 'bold'), 'width': 20, 'height': 2,
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
        
        # Today's Check-ins button (larger font) with click protection
        today_btn = tk.Button(button_frame, text="📊 Today's Check-ins", 
                             command=self.show_todays_checkins,
                             font=('Arial', 14, 'bold'),
                             bg='#3498db', fg='white',
                             width=15, height=2,
                             relief=tk.RAISED, bd=2)
        today_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button (larger font) with click protection
        refresh_btn = tk.Button(button_frame, text="🔄 Refresh", 
                               command=self.refresh_employee_data,
                               font=('Arial', 14, 'bold'),
                               bg='#27ae60', fg='white',
                               width=15, height=2,
                               relief=tk.RAISED, bd=2)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button (larger font) with click protection
        close_btn = tk.Button(button_frame, text="Close", 
                             command=self.close_employee_window,
                             font=('Arial', 14, 'bold'),
                             bg='#95a5a6', fg='white',
                             width=15, height=2,
                             relief=tk.RAISED, bd=2)
        close_btn.pack(side=tk.RIGHT)
        close_btn.focus_set()
    
    def close_employee_window(self):
        # Clear the current frame and show main menu
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.show_menu()
    
    def load_employee_data(self):
        """Load employee data into the listbox"""
        # This method will be implemented with dependency injection
        pass
    
    def on_employee_detail_select(self, event):
        """Handle employee selection"""
        # This method will be implemented with dependency injection
        pass
    
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
        # This method will be implemented with dependency injection
        pass
    
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
    
    def show_edit(self):
        # Clear the current frame and show edit interface
        if self.menu_window and self.menu_window.winfo_exists():
            for widget in self.menu_window.winfo_children():
                widget.destroy()
            self.edit_todays_checkins()
    
    def edit_todays_checkins(self):
        """Edit today's check-ins with video pause and deletion options"""
        if not self.attendance_db:
            CustomDialog.show_warning(self.menu_window, "Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            
            if not checkins:
                CustomDialog.show_info(self.menu_window,"Edit Check-ins", "No check-ins recorded for today.")
                return
            
        
            
            # Create edit window
            self.create_edit_checkins_window(checkins)
            
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to load check-ins for editing: {e}")
           
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
        title_label = tk.Label(main_frame, text="Edit Today's Check-ins", 
                              font=('Arial', 22, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Instructions (larger font)
        instruction_label = tk.Label(main_frame, 
                                   text="Click on a check-in entry to delete it.\nVideo is paused during editing.",
                                   font=('Arial', 14), 
                                   fg='#bdc3c7', bg='#2c3e50')
        instruction_label.pack(pady=(0, 15))
        
        # Create frame for listbox and scrollbar
        list_frame = tk.Frame(main_frame, bg='#2c3e50')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Listbox for check-ins (larger for easier selection)
        self.checkins_listbox = tk.Listbox(list_frame, 
                                          font=('Arial', 16, 'bold'),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#4a6741',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2,
                                          height=18)
        
         
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.checkins_listbox.yview)
        self.checkins_listbox.config(yscrollcommand=scrollbar.set)
         
        # Pack listbox and scrollbar
        self.checkins_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate listbox with check-ins
        self.populate_checkins_listbox(checkins)
        
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
        self.checkins_listbox.bind('<Double-Button-1>', self.on_checkin_double_click)
        
        # Store checkins data for reference
        self.edit_checkins_data = checkins
    def refresh_checkins_list(self):
        """Refresh the check-ins list"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window,"Error", "Attendance database not initialized.")
            return
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            self.edit_checkins_data = checkins
            
            self.populate_checkins_listbox(checkins)
            
     
            CustomDialog.show_info(self.menu_window,"Refresh Complete", f"List refreshed. {len(checkins)} check-ins found.")
                
        except Exception as e:
            CustomDialog.show_error(self.menu_window,"Error", f"Failed to refresh list: {e}")
    
 
    



    def populate_checkins_listbox(self, checkins):
        """Populate the listbox with check-in entries"""
        self.checkins_listbox.delete(0, tk.END)
        
        # Sort by check-in time
        checkins.sort(key=lambda x: x['check_in_time'])
        
        for i, record in enumerate(checkins, 1):
            name = record['name']
            check_in_time = record['check_in_time']
            
            # Format time
            if isinstance(check_in_time, str):
                try:
                    from datetime import datetime
                    time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                    formatted_time = time_obj.strftime("%H:%M:%S")
                except:
                    formatted_time = check_in_time
            else:
                formatted_time = str(check_in_time)
            
            # Create display entry
            entry_text = f"{i:2d}. {name:<20} - {formatted_time}"
            self.checkins_listbox.insert(tk.END, entry_text)
    
    def on_checkin_double_click(self, event):
        """Handle double-click on check-in entry"""
        selection = self.checkins_listbox.curselection()
        if selection:
            self.delete_selected_checkin()
    


    def delete_selected_checkin(self):
        """Delete the selected check-in entry"""
        if not self.attendance_db:
            CustomDialog.show_error(self.menu_window,"Error", "Attendance database not initialized.")
            return
            
        selection = self.checkins_listbox.curselection()
        print(f"Selection: {selection}")
        
        if not selection:
            CustomDialog.show_warning(self.menu_window, "Warning", "Please select a check-in entry to delete.")
            return
        
        index = selection[0]
        print(f"Selected index: {index}, Total data items: {len(self.edit_checkins_data)}")
        
        if index >= len(self.edit_checkins_data):
            CustomDialog.show_error(self.menu_window,"Error", "Invalid selection.")
            return
        
        # Get the record to delete
        record_to_delete = self.edit_checkins_data[index]
        name = record_to_delete['name']
        check_in_time = record_to_delete['check_in_time']
        
        print(f"Attempting to delete check-in for {name} at {check_in_time}")

        # Format time for display
        if isinstance(check_in_time, str):
            try:
                from datetime import datetime
                time_obj = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                formatted_time = time_obj.strftime("%H:%M:%S")
            except:
                formatted_time = check_in_time
        else:
            formatted_time = str(check_in_time)
        
        # Confirm deletion
        result = CustomDialog.ask_yes_no(self.menu_window, "Confirm Deletion", 
                                   f"Are you sure you want to delete this check-in?\n\n"
                                   f"Employee: {name}\n"
                                   f"Time: {formatted_time}\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                print(f"User confirmed deletion, calling database delete...")
                # Delete from database
                success = self.attendance_db.delete_checkin(name, check_in_time)
                print(f"Database delete result: {success}")
                    
                if success:
                    print("Database deletion successful, updating UI...")
                    
                    # Refresh the check-ins data from database to ensure consistency
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    records = self.attendance_db.get_attendance_report(today, today)
                    self.edit_checkins_data = [record for record in records if record.get('check_in_time')]
                    
                    print(f"Refreshed data from database, now have {len(self.edit_checkins_data)} items")
                    
                    # Clear listbox completely and repopulate
                    self.checkins_listbox.delete(0, tk.END)
                    
              
                    self.populate_checkins_listbox(self.edit_checkins_data)
                    print("Listbox repopulated with remaining data")
                   
                    
                    # Main textbox will be updated when returning to main UI
                    
         
                    # If no more check-ins, go back to main menu
                  
                else:
                    print("Database deletion failed")
                    CustomDialog.show_error(self.menu_window,"Error", f"Failed to delete check-in for {name}.")
                    
            except Exception as e:
                print(f"Exception during deletion: {e}")
                CustomDialog.show_error(self.menu_window,"Error", f"Failed to delete check-in: {e}")
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
    
    def show_camera_settings(self):
        """Show camera settings"""
        # This method will be implemented with dependency injection
        pass
    
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