'''
Optimized Face Recognition Attendance System - Main UI Module
Enhanced performance with better memory management and streamlined processing
Uses FaceNet (MTCNN + InceptionResnetV1) for face detection and recognition
'''

import cv2
import numpy as np
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
from typing import Optional
from datetime import datetime
import gc

# Import custom modules
from ui_dialogs import CustomDialog
from face_processing import FaceProcessor
from camera_handler import CameraHandler
from training_manager import TrainingManager
from attendance_manager import AttendanceManager
from file_manager import FileManager
from menu_ui import MenuManager
from camera_config import camera_config

# Optimized environment setup
os.environ.update({
    'QT_QPA_PLATFORM': 'xcb',
    'QT_QPA_FONTDIR': '/usr/share/fonts',
    'QT_LOGGING_RULES': 'qt.qpa.*=false',
    'LC_ALL': 'C',
    'LANG': 'C',
    'DISPLAY': ':0'
})

class OptimizedFaceRecognitionAttendanceUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Initialize modular components
        self.face_processor = FaceProcessor()
        self.camera_handler = CameraHandler()
        self.training_manager = TrainingManager()
        self.attendance_manager = AttendanceManager()
        self.file_manager = FileManager()
        self.menu_manager = MenuManager()
      
        # Core variables
        self.is_capturing = False
        self.is_training = False
        self.progress_var = tk.DoubleVar()
        
        # Initialize system
        self.initialize_system()
        
        # Start main processes
        self.start_camera_optimized()
        self.start_video_loop()
    
    def setup_window(self):
        """Optimized window setup"""
        self.root.title("Optimized Face Recognition Attendance System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        self.root.bind('<Escape>', lambda e: self.cleanup_and_exit())
        
        def record_touch(event):
            """Function to be called when a touch/click occurs."""
            self.root.x, self.root.y = event.x, event.y
            if self.root.x != event.x and self.root.y != event.y:
                self.root.event_generate('<Motion>', x=self.root.x, y=self.root.y, warp=True)
                self.root.event_generate('<Button-1>', x=self.root.x, y=self.root.y, warp=True)
            #else:
                #print(f"touch at {self.root.x}, {self.root.y}")
           #print(f"touch at {self.root.x}, {self.root.y}")
   
        def callback(e):
            x, y = e.x, e.y
            #print(f"Pointer is currently at {x}, {y}")   

        self.root.bind("<Button-1>", record_touch)
        self.root.bind('<Motion>', callback)
        
        # Cache screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
    
    def initialize_system(self):
        """Initialize all system components"""
        self.file_manager.create_directories()
        
        if not self.face_processor.initialize_face_recognition_optimized():
            CustomDialog.show_error(self.root, "Error", "FaceNet required. Install: pip install facenet-pytorch torch scikit-learn")
            self.root.quit()
            return
        
        self.attendance_manager.initialize_attendance_database()
        self.training_manager.update_names_list({})
        self.create_optimized_ui()
        self.attendance_manager.sync_dataset_with_database()
    
    def create_optimized_ui(self):
        """Create optimized UI with better layout"""
        # Main container frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video canvas frame (takes most of the space)
        self.video_frame = tk.Frame(main_frame, bg='#2c3e50', relief=tk.RAISED, bd=2)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(3, 5))
        
        # Main canvas for video
        self.canvas = tk.Canvas(self.video_frame, bg='black', highlightthickness=1, highlightcolor='#7f8c8d')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        self.time_label = tk.Label(main_frame, text="", 
                                  font=('Arial', 32, 'bold'), fg='white', bg='black', height=3)
        self.time_label.place(relx=0.5, rely=0.07, anchor='center')

        # Separator line
        separator = tk.Frame(main_frame, bg='#7f8c8d', height=2)
        separator.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Bottom button panel
        self.button_frame = tk.Frame(main_frame, bg='#34495e', height=80)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        self.button_frame.pack_propagate(False)  # Maintain fixed height
        
        # Progress bar overlay (hidden by default, shown during training)
        # Create a frame for the progress bar with background
        self.progress_frame = tk.Frame(self.root, bg='#34495e', bd=2, relief=tk.RAISED)
        self.progress_frame.place(relx=0.5, rely=0.85, anchor='center')
        
        # Progress bar with label
        progress_label = tk.Label(self.progress_frame, text="Training Progress:", 
                                 font=('Arial', 10, 'bold'), fg='white', bg='#34495e')
        progress_label.pack(pady=(5, 2))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                          maximum=self.training_manager.max_captures, length=400)
        self.progress_bar.pack(pady=(0, 5), padx=10)
        
        self.progress_frame.place_forget()  # Hide initially
        
        # Start time update timer
        self.update_time_display()
        
        # Create buttons in the bottom panel
        self.create_ui_buttons()
        
        # Load today's existing check-ins from database
        self.attendance_manager.load_existing_checkins(self.checkin_textbox)
    
    def create_ui_buttons(self):
        """Create UI buttons in the bottom panel"""
        # Button configurations
        main_button_config = {'font': ('Arial', 12, 'bold'), 'height': 5, 'relief': tk.RAISED, 'bd': 3}
        
        # Left side - Main action button
        left_frame = tk.Frame(self.button_frame, bg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.capture_button = tk.Button(left_frame, text="Check Out", command=self.check_out_last_face,
                                      bg='#e74c3c', fg='white', width=18, **main_button_config)
        self.capture_button.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Control buttons
        menu_frame = tk.Frame(self.button_frame, bg='#34495e')
        menu_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        self.menu_button = tk.Button(menu_frame, text="☰ Menu", 
                                    font=('Arial', 18, 'bold'),
                                    bg='#34495e', fg='white',
                                    relief=tk.RAISED, bd=3,
                                    cursor='hand2',
                                    width=12, height=2,
                                    command=self.show_main_menu_window)
        self.menu_button.pack(padx=5, pady=5)
        
        # Center info panel
        center_frame = tk.Frame(self.button_frame, bg='#34495e')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        # Create a frame for the textbox with title
        textbox_frame = tk.Frame(center_frame, bg='#34495e')
        textbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Title label for the textbox
        title_label = tk.Label(textbox_frame, text="Recent Check-ins", 
                              font=('Arial', 10, 'bold'), fg='#ecf0f1', bg='#34495e')
        title_label.pack(pady=(0, 2))
        
        # Create textbox with scrollbar
        text_frame = tk.Frame(textbox_frame, bg='#34495e')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget for check-in history
        self.checkin_textbox = tk.Text(text_frame, 
                                      font=('Arial', 9), 
                                      bg='#2c3e50', 
                                      fg='#ecf0f1',
                                      wrap=tk.WORD,
                                      height=3,
                                      state=tk.DISABLED,
                                      relief=tk.SUNKEN,
                                      bd=1)
        
        # Scrollbar for the textbox
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.checkin_textbox.yview)
        self.checkin_textbox.config(yscrollcommand=scrollbar.set)
        
        # Pack textbox and scrollbar
        self.checkin_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize with default message (will be updated after database check)
        self.checkin_textbox.config(state=tk.NORMAL)
        self.checkin_textbox.insert(tk.END, "Loading check-ins...\n")
        self.checkin_textbox.config(state=tk.DISABLED)
    
    def show_main_menu_window(self):
        # Pause video processing
        self.camera_handler.video_paused = True
        print("Video processing paused for menu")
    
        # Set callback functions for menu manager
        self.menu_manager.export_attendance_report = lambda: self.attendance_manager.export_attendance_report(self.root)
        self.menu_manager.show_camera_settings = lambda: self.file_manager.show_camera_settings(self.root)
        self.menu_manager.show_recognition_settings = lambda: self.file_manager.show_recognition_settings(self.root)
        self.menu_manager.show_database_settings = lambda: self.file_manager.show_database_settings(self.root, self.attendance_manager)
        self.menu_manager.reset_system = lambda: self.reset_system()
        self.menu_manager.cleanup_and_exit = self.cleanup_and_exit
        setattr(self.menu_manager, '_injected_start_capture', lambda menu_window: self.start_capture(menu_window))
        setattr(self.menu_manager, '_capture_injected', True)
  
        # Show menu and set close callback
        original_close = self.menu_manager.close_menu_window
        self.menu_manager.close_menu_window = lambda: self.close_menu_and_resume_video(original_close)
        
        self.menu_manager.show_main_menu_window(self.root)
    
    def close_menu_and_resume_video(self, original_close):
        original_close()
        self.camera_handler.video_paused = False
        print("Video processing resumed")
    
    def reset_system(self):
        """Reset system using file manager"""
        success = self.file_manager.reset_system(self.root, self.face_processor, self.attendance_manager, self.training_manager)
        if success:
            # Reload check-ins display
            self.attendance_manager.load_existing_checkins(self.checkin_textbox)
    
    def start_camera_optimized(self):
        """Start camera with optimized settings"""
        if not self.camera_handler.start_camera_optimized():
            CustomDialog.show_error(self.root, "Error", "Could not open camera")
    
    def start_video_loop(self):
        """Start optimized video processing loop"""
        self.update_video_optimized()
    
    def update_video_optimized(self):
        """Optimized video processing with better performance"""
        if not self.camera_handler.camera:
            return
        
        # Frame rate control
        if not self.camera_handler.is_time_for_next_frame():
            self.root.after(5, self.update_video_optimized)
            return
        
        try:
            ret, frame = self.camera_handler.get_frame()
            if not ret or frame is None:
                self.root.after(self.camera_handler.frame_interval, self.update_video_optimized)
                return
            
            # Check if video is paused (during training or menu)
            if self.camera_handler.video_paused:
                # Display the last frame without processing new faces
                if hasattr(self.camera_handler, 'last_display_frame') and self.camera_handler.last_display_frame is not None:
                    paused_frame = self.camera_handler.last_display_frame.copy()
                    cv2.putText(paused_frame, "Please wait...", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    self.camera_handler.display_frame_optimized(paused_frame, self.canvas, self.root)
                else:
                    paused_frame = frame.copy()
                    cv2.putText(paused_frame, "Please wait...", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    self.camera_handler.display_frame_optimized(paused_frame, self.canvas, self.root)
                    
                self.root.after(self.camera_handler.frame_interval, self.update_video_optimized)
                return
            
            # Store frame for pause display
     
            self.camera_handler.last_display_frame = frame.copy()
            
            # Optimized face detection with caching
            faces = self.camera_handler.get_cached_faces(frame, self.face_processor)
            
            # Process faces efficiently
            if faces:
                self.process_faces_optimized(frame, faces)
            
            # Display frame
            self.camera_handler.display_frame_optimized(frame, self.canvas, self.root)
            
        except Exception as e:
            print(f"Video update error: {e}")
        finally:
            # Memory cleanup
            self.camera_handler.cleanup_memory()
        
        self.root.after(self.camera_handler.frame_interval, self.update_video_optimized)
    
    def process_faces_optimized(self, frame, faces):
        """Optimized face processing with tracking"""
        current_faces = []
        face_names = []
        
        # Process each face
        for i, (x, y, w, h) in enumerate(faces):
            current_faces.append((x, y, w, h))
            
            # Face recognition (process less frequently)
            name = "Unknown"
            confidence = 0.0
            
            recognition_interval = camera_config.get("recognition_interval", 3)
            if self.camera_handler.frame_count % recognition_interval == 0:
                name, confidence = self.face_processor.process_face_recognition_optimized(frame, x, y, w, h)
            else:
                # Use tracking information for non-recognition frames
                name, confidence = self.camera_handler.get_tracked_face_info((x, y, w, h))
            
            face_names.append(name)
            
            # Handle attendance for recognized faces
            if name != "Unknown" and confidence > 0.7:
                if self.attendance_manager.handle_attendance_optimized(name):
                    # Save check-in photo
                    self.training_manager.save_checkin_photo(name, frame)
                    self.attendance_manager.update_last_checkin_display(name, self.checkin_textbox)
            
            # Capture for training
            if self.is_capturing and self.training_manager.capture_count < self.training_manager.max_captures:
                if self.training_manager.capture_face_optimized(frame, x, y, w, h):
                    self.progress_var.set(self.training_manager.capture_count)
                    self.stop_capture()
        
        # Update face tracking first
        self.camera_handler.update_face_tracking(current_faces, face_names)
        
        # Draw faces with tracking information
        for i, (x, y, w, h) in enumerate(current_faces):
            name = face_names[i]
            confidence = 0.0
            track_id = None
            
            # Find corresponding track ID and get updated info
            for tid, track_data in self.camera_handler.tracked_faces.items():
                if self.camera_handler.calculate_rectangle_distance((x, y, w, h), track_data['rectangle']) < 10:
                    name = track_data['name']
                    confidence = track_data['confidence']
                    track_id = tid
                    break
            
            # Draw face with tracking info
            self.camera_handler.draw_face_with_tracking(frame, x, y, w, h, name, confidence, track_id)
        
        self.camera_handler.current_frame_faces = current_faces
    
    def start_capture(self, menu_window=None):
        """Optimized face capture process"""
        if self.is_capturing:
            return
        
        self.camera_handler.video_paused = True
        
        # Get user name input - use menu window if provided, otherwise use root
        parent_window = menu_window if menu_window else self.root
        restore_callback = self.menu_manager.show_menu if menu_window else None
        name = self.training_manager.get_user_name_input(parent_window, self.screen_width, self.screen_height, restore_callback)
        if not name:
            return
            
        self.training_manager.show_capture_instructions(self.root)
        
        # Set up user information
        self.training_manager.setup_user_for_capture(name)
        
        # Start capturing
        self.training_manager.capture_count = 0
        self.is_capturing = True
        self.camera_handler.video_paused = False
        
        # Update UI
        self.capture_button.config(text="Capturing...", bg='#e74c3c', state=tk.DISABLED)
        self.progress_frame.place(relx=0.5, rely=0.85, anchor='center')  # Show progress bar
        self.progress_var.set(0)
        print(f"Status: Capturing faces for {name}...")
        print(f"Started capturing faces for {name}")
    
    def stop_capture(self):
        """Stop face capture and start training"""
        self.is_capturing = False
        self.capture_button.config(text="Start Training", bg='#27ae60', state=tk.NORMAL)
        print("Status: Capture complete. Starting training...")
        
        # Start automatic training
        self.start_auto_training()
    
    def start_auto_training(self):
        """Start automatic training after capture"""
        if self.is_training:
            return
        
        self.is_training = True
        print("Status: Training model...")
        
        # Start training thread
        training_thread = threading.Thread(
            target=self.training_manager.auto_train_thread, 
            args=(self.face_processor, self.training_complete, self.training_failed),
            daemon=True
        )
        training_thread.start()
    
    def training_complete(self, num_embeddings):
        """Training completed successfully"""
        self.is_training = False
        self.progress_frame.place_forget()  # Hide progress bar
        print(f"Status: Training complete. {num_embeddings} embeddings")
        self.training_manager.update_names_list({})
        
        # Resume video processing
        self.camera_handler.video_paused = False
        print("Video feed resumed")
        
        # Add new user to attendance database
        if hasattr(self.training_manager, 'is_new_user') and self.training_manager.is_new_user and self.attendance_manager.attendance_db:
            try:
                # Check if employee already exists in database
                if self.attendance_manager.is_employee_in_database(self.training_manager.current_user_name):
                    print(f"⚠️  Employee '{self.training_manager.current_user_name}' already exists in database")
                    CustomDialog.show_info(self.root, "Training Complete", 
                                      f"Successfully trained '{self.training_manager.current_user_name}'!\n\n"
                                      f"Embeddings: {num_embeddings}\n"
                                      f"Note: Employee already exists in database")
                else:
                    # Add new employee to database
                    success = self.attendance_manager.add_employee_to_database(self.training_manager.current_user_name)
                    
                    if success:
                        print(f"Added '{self.training_manager.current_user_name}' to attendance database")
                        CustomDialog.show_info(self.root, "Training Complete", 
                                      f"Successfully trained and registered '{self.training_manager.current_user_name}' as a new employee!\n\n"
                                      f"Embeddings: {num_embeddings}")
                    else:
                        print(f"Failed to add '{self.training_manager.current_user_name}' to database")
                        CustomDialog.show_info(self.root, "Training Complete", 
                                          f"Successfully trained '{self.training_manager.current_user_name}'!\n\n"
                                          f"Embeddings: {num_embeddings}\n"
                                          f"Note: Could not add to database")
                    
            except Exception as e:
                print(f"❌ Error adding user to database: {e}")
                CustomDialog.show_info(self.root, "Training Complete", 
                                  f"Successfully trained '{self.training_manager.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}\n"
                                  f"Note: Could not add to database - {e}")
        else:
            # Existing user or no database
            if hasattr(self.training_manager, 'is_new_user') and not self.training_manager.is_new_user:
                print(f"🔄 Retrained existing user '{self.training_manager.current_user_name}'")
                CustomDialog.show_info(self.root, "Training Complete", 
                                  f"Successfully retrained '{self.training_manager.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}")
            else:
                CustomDialog.show_info(self.root, "Training Complete", 
                                  f"Successfully trained '{self.training_manager.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}")
        
        # Reset the new user flag
        self.training_manager.is_new_user = False
    
    def training_failed(self, error_message):
        """Training failed"""
        self.is_training = False
        self.progress_frame.place_forget()  # Hide progress bar
        print("Status: Training failed")
        
        # Resume video processing
        self.camera_handler.video_paused = False
        print("Video feed resumed")
        
        # Reset the new user flag
        self.training_manager.is_new_user = False
        
        CustomDialog.show_error(self.root, "Training Error", error_message)
    
    def check_out_last_face(self):
        """Handle the 'Check Out' button click - checks out the last recognized employee."""
        # Check if we have a last recognized employee
        if not self.attendance_manager.last_recognized_employee:
            CustomDialog.show_info(self.root, "No Employee Detected", 
                                 "No employee has been recognized recently.\n\n"
                                 "Please ensure an employee is visible to the camera before checking out.")
            return
        
        last_employee = self.attendance_manager.last_recognized_employee
        
        # Confirm checkout
        result = CustomDialog.ask_yes_no(self.root, "Confirm Check Out", 
                                       f"Check out {last_employee}?\n\n"
                                       f"This will record their departure time.")
        
        if not result:
            return
        
        # Attempt to check out the last recognized employee
        if self.attendance_manager.handle_checkout_optimized(last_employee):
            # Save check-out photo if we have a current frame
            if hasattr(self.camera_handler, 'last_display_frame') and self.camera_handler.last_display_frame is not None:
                self.training_manager.save_checkout_photo(last_employee, self.camera_handler.last_display_frame)
            
            # Update the display to show checkout
            self.update_checkout_display(last_employee)
            
            CustomDialog.show_info(self.root, "Check Out Successful", 
                                 f"Successfully checked out {last_employee}.\n\n"
                                 f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print(f"✅ Successfully checked out {last_employee}")
        else:
            CustomDialog.show_info(self.root, "Check Out Failed", 
                                 f"Could not check out {last_employee}.\n\n"
                                 f"Possible reasons:\n"
                                 f"• Employee was not checked in today\n"
                                 f"• Employee already checked out\n"
                                 f"• Database error")
            print(f"❌ Failed to check out {last_employee}")
    
    def update_checkout_display(self, name):
        """Update the check-in history to show checkout"""
        checkout_time = datetime.now().strftime("%H:%M:%S")
        
        # Enable text editing
        self.checkin_textbox.config(state=tk.NORMAL)
        
        # Add checkout entry with timestamp and name
        entry = f"🔓 {name} - {checkout_time} (CHECKOUT)\n"
        self.checkin_textbox.insert(tk.END, entry)
        
        # Auto-scroll to the bottom to show the latest entry
        self.checkin_textbox.see(tk.END)
        
        # Disable text editing to prevent user modification
        self.checkin_textbox.config(state=tk.DISABLED)

    def cleanup_and_exit(self):
        """Clean up resources and exit"""
        self.camera_handler.cleanup_camera()
        self.attendance_manager.cleanup_database()
        self.root.destroy()
    
    def update_time_display(self):
        """Update the current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.time_label.config(text=current_time)
        # Update every second
        self.root.after(1000, self.update_time_display)

def main():
    root = tk.Tk()
    app = OptimizedFaceRecognitionAttendanceUI(root)
 
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.cleanup_and_exit)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 