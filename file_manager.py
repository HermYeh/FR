import os
import shutil
import tkinter as tk
from tkinter import ttk
from typing import Optional, TYPE_CHECKING, Any
from ui_dialogs import CustomDialog
from camera_config import camera_config

if TYPE_CHECKING:
    from face_recognition_attendance_ui import OptimizedFaceRecognitionAttendanceUI

class FileManager:
    """Handles file operations and data management"""
    
    def __init__(self):
        self.app_instance: Optional['OptimizedFaceRecognitionAttendanceUI'] = None

    
    def create_directories(self):
        """Create necessary directories"""
        for directory in ['dataset', 'trainer', 'CheckinPhoto', 'CheckoutPhoto']:
            os.makedirs(directory, exist_ok=True)
    
    def reset_system(self, root, face_processor, attendance_manager, training_manager):
        """Reset system settings"""
        result = CustomDialog.ask_yes_no(root, "Reset System", 
                                   "Are you sure you want to reset the system?\n\n"
                                   "This will:\n"
                                   "• Delete all face recognition data\n"
                                   "• Delete all training images\n"
                                   "• Delete all check-in photos\n"
                                   "• Delete all check-out photos\n"
                                   "• Delete all trainer files\n"
                                   "• Delete attendance database\n"
                                   "• Reload the system\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                # Delete contents of folders
                folders_to_clear = ['CheckinPhoto', 'CheckoutPhoto', 'dataset', 'trainer']
                deleted_items = []
                
                for folder in folders_to_clear:
                    if os.path.exists(folder):
                        # Get count of items before deletion
                        item_count = 0
                        for root_dir, dirs, files in os.walk(folder):
                            item_count += len(files)
                        
                        # Delete all contents
                        for item in os.listdir(folder):
                            item_path = os.path.join(folder, item)
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                            else:
                                os.remove(item_path)
                        
                        if item_count > 0:
                            deleted_items.append(f"{folder}: {item_count} items")
                        print(f"Cleared {folder} folder ({item_count} items)")
                
                # Delete attendance database
                if attendance_manager.attendance_db:
                    try:
                        # Close database connection first
                        attendance_manager.attendance_db.close()
                        attendance_manager.attendance_db = None
                        
                        # Delete database file
                        db_files = ["attendance.db", "attendance.db-journal", "attendance.db-wal", "attendance.db-shm"]
                        db_deleted = False
                        
                        for db_file in db_files:
                            if os.path.exists(db_file):
                                os.remove(db_file)
                                db_deleted = True
                                print(f"Deleted database file: {db_file}")
                        
                        if db_deleted:
                            deleted_items.append("Database: All attendance records")
                            
                    except Exception as db_error:
                        print(f"Error deleting database: {db_error}")
                        deleted_items.append("Database: Error deleting (may need manual cleanup)")
                
                # Clear face embeddings
                face_processor.face_embeddings = {}
                face_processor.save_face_embeddings()
                
                # Clear embedding cache
                face_processor.clear_embedding_cache()
                
                # Clear names list
                training_manager.names = []
                
                # Reload system components
                face_processor.load_face_embeddings()
                training_manager.update_names_list({})
                
                # Reinitialize attendance database
                attendance_manager.initialize_attendance_database()
                
                # Success message with details
                details = "\n".join(deleted_items) if deleted_items else "No items to delete"
                CustomDialog.show_info(root, "Reset Complete", 
                                  f"System has been reset successfully.\n\n"
                                  f"Deleted items:\n{details}\n\n"
                                  f"System has been reloaded.")
                
                print("System reset completed successfully")
                return True
                
            except Exception as e:
                CustomDialog.show_error(root, "Error", f"Failed to reset system: {e}")
                print(f"Error during system reset: {e}")
                return False
        return False
    
    def show_camera_settings(self, root):
        """Show dynamic camera settings dialog"""
        self.show_camera_settings_dialog(root)
    
    def show_camera_settings_dialog(self, root):
        """Show comprehensive camera settings dialog with editable fields"""
        # Create dialog window
        dialog = tk.Toplevel(root)
        dialog.grab_set()
        dialog.title("Camera Settings")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(True, True)
        dialog.transient(root)
        
        # Set dialog size
        dialog.update_idletasks()
        width = 800
        height = 700
        
        # Center dialog relative to parent
        if root:
            root.update_idletasks()
            parent_x = root.winfo_x()
            parent_y = root.winfo_y()
            parent_width = root.winfo_width()
            parent_height = root.winfo_height()
        else:
            parent_x = parent_y = parent_width = parent_height = 0
        
        # Calculate center position relative to parent
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(dialog, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Camera & Processing Settings", 
                              font=('Arial', 18, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 15))
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Style notebook
        style = ttk.Style()
        style.configure('TNotebook', background='#2c3e50')
        style.configure('TNotebook.Tab', background='#34495e', foreground='white', padding=[10, 5])
        
        # Storage for all settings
        self.settings_vars = {}
        
        # Camera Hardware Tab
        camera_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(camera_frame, text="Camera Hardware")
        self.create_camera_hardware_settings(camera_frame)
        
        # Video Processing Tab
        video_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(video_frame, text="Video Processing")
        self.create_video_processing_settings(video_frame)
        
        # Face Detection Tab
        detection_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(detection_frame, text="Face Detection")
        self.create_face_detection_settings(detection_frame)
        
        # Face Recognition Tab
        recognition_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(recognition_frame, text="Face Recognition")
        self.create_face_recognition_settings(recognition_frame)
        
        # Performance Tab
        performance_frame = tk.Frame(notebook, bg='#34495e')
        notebook.add(performance_frame, text="Performance")
        self.create_performance_settings(performance_frame)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create buttons
        def on_save():
            """Save all settings"""
            if self.save_all_settings():
                CustomDialog.show_info(dialog, "Settings Saved", 
                                     "Camera settings have been saved successfully.\n\n"
                                     "Changes will take effect after restarting the camera.")
                dialog.destroy()
            else:
                CustomDialog.show_error(dialog, "Save Error", 
                                      "Failed to save camera settings.\n\n"
                                      "Please check your input values and try again.")
        
        def on_reset():
            """Reset to default settings"""
            result = CustomDialog.ask_yes_no(dialog, "Reset Settings", 
                                           "Reset all camera settings to default values?\n\n"
                                           "This action cannot be undone.")
            if result:
                camera_config.reset_to_defaults()
                self.load_settings_into_ui()
                CustomDialog.show_info(dialog, "Settings Reset", 
                                     "Camera settings have been reset to default values.")
        
        def on_apply():
            """Apply settings without closing dialog"""
            if self.save_all_settings():
                CustomDialog.show_info(dialog, "Settings Applied", 
                                     "Camera settings have been applied.\n\n"
                                     "Changes will take effect after restarting the camera.")
            else:
                CustomDialog.show_error(dialog, "Apply Error", 
                                      "Failed to apply camera settings.\n\n"
                                      "Please check your input values and try again.")
        
        def on_cancel():
            """Close dialog without saving"""
            dialog.destroy()
        
        # Reset button
        reset_btn = tk.Button(button_frame, text="Reset to Defaults", 
                             command=on_reset,
                             font=('Arial', 12, 'bold'),
                             bg='#e67e22', fg='white',
                             width=15, height=2,
                             relief=tk.RAISED, bd=3,
                             cursor='hand2')
        reset_btn.pack(side=tk.LEFT)
        
        # Apply button
        apply_btn = tk.Button(button_frame, text="Apply", 
                             command=on_apply,
                             font=('Arial', 12, 'bold'),
                             bg='#f39c12', fg='white',
                             width=12, height=2,
                             relief=tk.RAISED, bd=3,
                             cursor='hand2')
        apply_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save button
        save_btn = tk.Button(button_frame, text="Save & Close", 
                            command=on_save,
                            font=('Arial', 12, 'bold'),
                            bg='#27ae60', fg='white',
                            width=15, height=2,
                            relief=tk.RAISED, bd=3,
                            cursor='hand2')
        save_btn.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=on_cancel,
                              font=('Arial', 12, 'bold'),
                              bg='#e74c3c', fg='white',
                              width=12, height=2,
                              relief=tk.RAISED, bd=3,
                              cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        
        # Load current settings into UI
        self.load_settings_into_ui()
        
        # Focus and wait
        dialog.focus()
        dialog.wait_window()
    
    def create_camera_hardware_settings(self, parent):
        """Create camera hardware settings section"""
        self.create_settings_section(parent, "Camera Hardware", [
            ("camera_index", "Camera Index", "int", (0, 5)),
            ("frame_width", "Frame Width", "int", (160, 1920)),
            ("frame_height", "Frame Height", "int", (120, 1080)),
            ("target_fps", "Target FPS", "int", (1, 60)),
            ("buffer_size", "Buffer Size", "int", (1, 10)),
            ("auto_exposure", "Auto Exposure", "float", (0.0, 1.0)),
            ("brightness", "Brightness", "int", (-100, 100)),
            ("contrast", "Contrast", "int", (-100, 100)),
            ("saturation", "Saturation", "int", (-100, 100)),
            ("gain", "Gain", "int", (0, 100)),
        ])
    
    def create_video_processing_settings(self, parent):
        """Create video processing settings section"""
        self.create_settings_section(parent, "Video Processing", [
            ("face_detection_interval", "Face Detection Interval", "int", (1, 30)),
            ("face_cache_size", "Face Cache Size", "int", (1, 50)),
            ("frame_rotation", "Frame Rotation", "choice", ["90_ccw", "90_cw", "180", "none"]),
            ("flip_horizontal", "Flip Horizontal (Mirror)", "bool", None),
            ("flip_vertical", "Flip Vertical", "bool", None),
            ("memory_cleanup_interval", "Memory Cleanup Interval", "int", (5, 100)),
        ])
    
    def create_face_detection_settings(self, parent):
        """Create face detection settings section"""
        self.create_settings_section(parent, "Face Detection", [
            ("min_face_size", "Min Face Size", "int", (10, 200)),
            ("detection_scale_factor", "Detection Scale Factor", "float", (0.1, 1.0)),
            ("mtcnn_threshold_1", "MTCNN Threshold 1", "float", (0.1, 1.0)),
            ("mtcnn_threshold_2", "MTCNN Threshold 2", "float", (0.1, 1.0)),
            ("mtcnn_threshold_3", "MTCNN Threshold 3", "float", (0.1, 1.0)),
            ("detection_confidence_threshold", "Detection Confidence", "float", (0.1, 1.0)),
            ("min_face_region_size", "Min Face Region Size", "int", (10, 100)),
        ])
    
    def create_face_recognition_settings(self, parent):
        """Create face recognition settings section"""
        self.create_settings_section(parent, "Face Recognition", [
            ("recognition_threshold", "Recognition Threshold", "float", (0.1, 1.0)),
            ("recognition_interval", "Recognition Interval", "int", (1, 10)),
            ("embedding_cache_size", "Embedding Cache Size", "int", (10, 500)),
            ("confidence_boost_factor", "Confidence Boost Factor", "float", (0.01, 0.5)),
            ("confidence_decay_factor", "Confidence Decay Factor", "float", (0.01, 0.5)),
        ])
    
    def create_performance_settings(self, parent):
        """Create performance settings section"""
        self.create_settings_section(parent, "Performance", [
            ("enable_gpu", "Enable GPU", "bool", None),
            ("image_quality", "Image Quality", "choice", ["low", "medium", "high"]),
            ("tracking_enabled", "Face Tracking", "bool", None),
            ("max_track_distance", "Max Track Distance", "int", (10, 200)),
            ("track_timeout", "Track Timeout", "int", (5, 100)),
        ])
    
    def create_settings_section(self, parent, title, settings):
        """Create a settings section with input fields"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='#34495e')
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(scrollable_frame, text=f"{title} Settings", 
                              font=('Arial', 14, 'bold'), 
                              fg='#ecf0f1', bg='#34495e')
        title_label.pack(pady=(5, 15), anchor='w')
        
        # Create input fields
        for setting_key, label_text, input_type, constraints in settings:
            self.create_setting_field(scrollable_frame, setting_key, label_text, input_type, constraints)
    
    def create_setting_field(self, parent, key, label_text, input_type, constraints):
        """Create a single setting input field"""
        frame = tk.Frame(parent, bg='#34495e')
        frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(frame, text=f"{label_text}:", 
                        font=('Arial', 10), 
                        fg='#bdc3c7', bg='#34495e',
                        width=25, anchor='w')
        label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Input field based on type
        if input_type == "int":
            var = tk.IntVar()
            entry = tk.Spinbox(frame, textvariable=var, 
                              from_=constraints[0], to=constraints[1],
                              font=('Arial', 10), width=10,
                              bg='#ecf0f1', relief=tk.SUNKEN, bd=2)
        elif input_type == "float":
            var = tk.DoubleVar()
            entry = tk.Entry(frame, textvariable=var,
                            font=('Arial', 10), width=10,
                            bg='#ecf0f1', relief=tk.SUNKEN, bd=2)
        elif input_type == "bool":
            var = tk.BooleanVar()
            entry = tk.Checkbutton(frame, variable=var,
                                  bg='#34495e', fg='#ecf0f1',
                                  selectcolor='#2c3e50')
        elif input_type == "choice":
            var = tk.StringVar()
            entry = ttk.Combobox(frame, textvariable=var,
                               values=constraints, state="readonly",
                               font=('Arial', 10), width=12)
        else:
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var,
                            font=('Arial', 10), width=15,
                            bg='#ecf0f1', relief=tk.SUNKEN, bd=2)
        
        entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Description
        desc_text = camera_config.get_config_description(key)
        desc_label = tk.Label(frame, text=desc_text,
                             font=('Arial', 8), 
                             fg='#95a5a6', bg='#34495e',
                             wraplength=300, justify=tk.LEFT)
        desc_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # Store the variable for later access
        self.settings_vars[key] = var
    
    def load_settings_into_ui(self):
        """Load current configuration values into UI elements"""
        for key, var in self.settings_vars.items():
            try:
                value = camera_config.get(key)
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(value))
                elif isinstance(var, tk.IntVar):
                    var.set(int(value))
                elif isinstance(var, tk.DoubleVar):
                    var.set(float(value))
                else:
                    var.set(str(value))
            except Exception as e:
                print(f"Error loading setting {key}: {e}")
    
    def save_all_settings(self) -> bool:
        """Save all settings from UI to configuration"""
        try:
            new_config = {}
            for key, var in self.settings_vars.items():
                try:
                    if isinstance(var, tk.BooleanVar):
                        new_config[key] = var.get()
                    elif isinstance(var, tk.IntVar):
                        new_config[key] = var.get()
                    elif isinstance(var, tk.DoubleVar):
                        new_config[key] = var.get()
                    else:
                        new_config[key] = var.get()
                except Exception as e:
                    print(f"Error getting value for {key}: {e}")
                    return False
            
            # Validate configuration
            if not self.validate_settings(new_config):
                return False
            
            # Update and save configuration
            camera_config.update_config(new_config)
            success = camera_config.save_config()
            
            if success:
                # Apply changes to running components
                self.apply_runtime_changes()
            
            return success
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def apply_runtime_changes(self):
        """Apply configuration changes to running components"""
        try:
            if self.app_instance is not None:
                # Apply camera configuration changes
                if hasattr(self.app_instance, 'camera_handler'):
                    self.app_instance.camera_handler.apply_config_changes()
                
                # Apply face processor configuration changes  
                if hasattr(self.app_instance, 'face_processor'):
                    self.app_instance.face_processor.apply_config_changes()
                
                print("✅ Runtime configuration changes applied")
            else:
                print("ℹ️  Configuration saved. Changes will take effect on next restart.")
                
        except Exception as e:
            print(f"⚠️  Configuration saved but runtime update failed: {e}")
            print("Changes will take effect on next restart.")
    
    def validate_settings(self, config) -> bool:
        """Validate configuration values"""
        validators = {
            "frame_width": lambda x: 160 <= x <= 1920,
            "frame_height": lambda x: 120 <= x <= 1080,
            "target_fps": lambda x: 1 <= x <= 60,
            "buffer_size": lambda x: 1 <= x <= 10,
            "auto_exposure": lambda x: 0.0 <= x <= 1.0,
            "face_detection_interval": lambda x: 1 <= x <= 30,
            "min_face_size": lambda x: 10 <= x <= 200,
            "recognition_threshold": lambda x: 0.1 <= x <= 1.0,
            "detection_confidence_threshold": lambda x: 0.1 <= x <= 1.0,
            "detection_scale_factor": lambda x: 0.1 <= x <= 1.0,
        }
        
        for key, validator in validators.items():
            if key in config and not validator(config[key]):
                CustomDialog.show_error(None, "Invalid Value", 
                                      f"Invalid value for {key}: {config[key]}\n\n"
                                      f"Please check the allowed range.")
                return False
        
        return True
    
    def show_recognition_settings(self, root):
        """Show face recognition settings dialog"""
        settings_text = """Face Recognition Settings:

• Model: FaceNet (MTCNN + InceptionResnetV1)
• Detection Threshold: 0.8
• Recognition Threshold: 0.7
• Face Detection Interval: Every 5th frame
• Recognition Cooldown: 1 second

To modify recognition settings, edit the relevant methods."""
        
        CustomDialog.show_info(root, "Recognition Settings", settings_text)
    
    def show_database_settings(self, root, attendance_manager):
        """Show database settings dialog"""
        if not attendance_manager.attendance_db:
            CustomDialog.show_warning(root, "Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            # Get database info
            employees = attendance_manager.attendance_db.get_employees()
            employee_count = len(employees)
            
            today = datetime.now().strftime("%Y-%m-%d")
            records = attendance_manager.attendance_db.get_attendance_report(today, today)
            today_checkins = len([r for r in records if r.get('check_in_time')])
            
            settings_text = f"""Database Settings:

• Database Type: SQLite
• Total Employees: {employee_count}
• Today's Check-ins: {today_checkins}
• Database File: attendance.db

Database location and connection details can be found in attendance_database.py"""
            
            CustomDialog.show_info(root, "Database Settings", settings_text)
            
        except Exception as e:
            CustomDialog.show_error(root, "Error", f"Failed to get database info: {e}") 