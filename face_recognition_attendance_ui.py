'''
Optimized Face Recognition Attendance System
Enhanced performance with better memory management and streamlined processing
Uses FaceNet (MTCNN + InceptionResnetV1) for face detection and recognition
'''

import cv2
import numpy as np
import os
import threading
import time
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from datetime import datetime
from attendance_database import AttendanceDatabase
import pickle
from collections import deque
import gc

# FaceNet imports
FACENET_AVAILABLE = False
try:
    from facenet_pytorch import MTCNN, InceptionResnetV1
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    FACENET_AVAILABLE = True
    print("FaceNet modules loaded successfully")
except ImportError:
    FACENET_AVAILABLE = False
    print("FaceNet not available. Install with: pip install facenet-pytorch torch scikit-learn")

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
        
        # Core variables
        self.camera = None
        self.is_capturing = False
        self.is_training = False
        self.names = []
        self.current_user_name = ""
        self.capture_count = 0
        self.max_captures = 8
        self.is_new_user = False  # Track if current user is new or existing
        
        # FaceNet components
        self.mtcnn = None
        self.facenet_model = None
        self.face_embeddings = {}
        
        # Performance optimization
        self.frame_skip_count = 0
        self.face_detection_interval = 5# Process every 5th frame
        self.face_cache = deque(maxlen=10)  # Cache recent face detections
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.target_fps = 10 # Reduced from 30 for better performance
        self.frame_interval = 1000 // self.target_fps
        
        # UI optimization
        self.ui_update_interval =1 # Update UI every 3rd frame
        self.current_frame_tk = None
        self.canvas_size = None
        
        # Attendance tracking
        self.attendance_db = None
        self.last_recognition_time = {}
        self.recognition_cooldown = 1 # Reduced from 5 seconds
        
        # Threading optimization
        self.processing_lock = threading.Lock()
        self.embedding_cache = {}  # Cache embeddings for faster recognition
        
        # Video control
        self.video_paused = False  # Flag to pause video during training
        
        # Face tracking for persistent recognition
        self.tracked_faces = {}  # Track faces across frames
        self.face_track_id = 0  # Unique ID counter for faces
        self.max_track_distance = 50  # Maximum distance to consider same face
        self.track_timeout = 30  # Frames before removing lost track
        self.current_frame_faces = []  # Store current frame face data
        
        # Initialize system
        self.initialize_system()
        
        # Start main processes
        self.start_camera_optimized()
        self.start_video_loop()
        # Removed start_attendance_monitoring as we now use database-based checking
    
    def setup_window(self):
        """Optimized window setup"""
        self.root.title("Optimized Face Recognition Attendance System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        self.root.bind('<Escape>', lambda e: self.cleanup_and_exit())
        
        # Cache screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
    
    def initialize_system(self):
        """Initialize all system components"""
        self.create_directories()
        self.initialize_face_recognition_optimized()
        self.initialize_attendance_database()
        self.update_names_list({})
        self.create_optimized_ui()
        self.sync_dataset_with_database() # Sync dataset users with database on startup
    
    def create_directories(self):
        """Create necessary directories"""
        for directory in ['dataset', 'trainer']:
            os.makedirs(directory, exist_ok=True)
    
    def initialize_face_recognition_optimized(self):
        """Optimized FaceNet initialization"""
        if not FACENET_AVAILABLE:
            messagebox.showerror("Error", "FaceNet required. Install: pip install facenet-pytorch torch scikit-learn")
            self.root.quit()
            return
        
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {device}")
            
            # Optimized MTCNN settings
            self.mtcnn = MTCNN(
                image_size=160,
                margin=0,
                min_face_size=30,  # Increased for better performance
                thresholds=[0.7, 0.8, 0.8],  # Higher thresholds for better accuracy
                factor=0.709,
                post_process=True,
                device=device,
                keep_all=False  # Keep only best face for better performance
            )
            
            # Initialize FaceNet model
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            
            self.load_face_embeddings()
            print("Optimized FaceNet initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize FaceNet: {e}")
            self.root.quit()
    
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
                        print(f"✅ Synced '{user_name}' to database")
                except Exception as e:
                    print(f"❌ Failed to sync '{user_name}': {e}")
            
            if added_count > 0:
                print(f"🔄 Synced {added_count} users from dataset to database")
            elif len(dataset_users) > 0:
                print(f"✅ All {len(dataset_users)} dataset users are already in database")
            else:
                print("📁 No users found in dataset to sync")
                
        except Exception as e:
            print(f"❌ Error syncing dataset with database: {e}")
    
    def initialize_attendance_database(self):
        """Initialize attendance database"""
        try:
            self.attendance_db = AttendanceDatabase()
            print("Attendance database initialized")
        except Exception as e:
            print(f"Error initializing attendance database: {e}")
            # Ensure attendance_db is not None even if initialization fails
            self.attendance_db = None
    
    def create_optimized_ui(self):
        """Create optimized UI with better layout"""
        # Main container frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Time label positioned in the top black area
 

        # Video canvas frame (takes most of the space)
        self.video_frame = tk.Frame(main_frame, bg='#2c3e50', relief=tk.RAISED, bd=2)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(3, 5))
        
        # Create main menu window button in upper right corner
        self.create_menu_button()
   
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
        self.progress_var = tk.DoubleVar()
        
        # Create a frame for the progress bar with background
        self.progress_frame = tk.Frame(self.root, bg='#34495e', bd=2, relief=tk.RAISED)
        self.progress_frame.place(relx=0.5, rely=0.85, anchor='center')
        
        # Progress bar with label
        progress_label = tk.Label(self.progress_frame, text="Training Progress:", 
                                 font=('Arial', 10, 'bold'), fg='white', bg='#34495e')
        progress_label.pack(pady=(5, 2))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                          maximum=self.max_captures, length=400)
        self.progress_bar.pack(pady=(0, 5), padx=10)
        
        self.progress_frame.place_forget()  # Hide initially
        
        # Initialize check-in tracking
        self.last_checkin_name = ""
        self.last_checkin_time = ""
        
        # Start time update timer
        self.update_time_display()
        
        # Create buttons in the bottom panel
        self.create_ui_buttons()
        
        # Load today's existing check-ins from database
        self.load_existing_checkins()
    
    def create_ui_buttons(self):
        """Create UI buttons in the bottom panel"""
        # Button configurations
        main_button_config = {'font': ('Arial', 12, 'bold'), 'height': 5, 'relief': tk.RAISED, 'bd': 3}
        small_button_config = {'font': ('Arial', 10, 'bold'), 'height': 1, 'relief': tk.RAISED, 'bd': 3}
        
        # Left side - Main action button
        left_frame = tk.Frame(self.button_frame, bg='#34495e')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.capture_button = tk.Button(left_frame, text="Start Training", command=self.start_capture,
                                      bg='#27ae60', fg='white', width=18, **main_button_config)
        self.capture_button.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Control buttons
        right_frame = tk.Frame(self.button_frame, bg='#34495e')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=5)
        
        self.attendance_button = tk.Button(right_frame, text="Attendance Summary", 
                                         command=self.show_attendance_summary,
                                         bg='#3498db', fg='white', width=18, **main_button_config)
        self.attendance_button.pack(pady=2)
        
        #self.manual_checkin_button = tk.Button(right_frame, text="Manual Check-in", 
        #                                     command=self.manual_check_in,
        #                                     bg='#e67e22', fg='white', width=18, **small_button_config)
        #self.manual_checkin_button.pack(pady=2)
        
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
        
        # Track if we've had any check-ins today
        self.has_checkins_today = False
    
    def create_menu_button(self):
        """Create main menu button in the upper right corner"""
        # Create menu bar frame positioned in upper right
        menu_frame = tk.Frame(self.root, bg='#2c3e50')
        menu_frame.place(relx=0.98, rely=0.02, anchor='ne')
        
        # Create main menu button
        self.menu_button = tk.Button(menu_frame, text="☰ Menu", 
                                    font=('Arial', 10, 'bold'),
                                    bg='#34495e', fg='white',
                                    relief=tk.RAISED, bd=2,
                                    cursor='hand2',
                                    command=self.show_main_menu_window)
        self.menu_button.pack()
    
    def show_main_menu_window(self):
        """Show the main menu window with all functionality"""
        # Pause video processing
        self.video_paused = True
        print("Video processing paused for menu")
        
        # Create main menu window
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.title("Face Recognition Attendance System - Main Menu")
        self.menu_window.geometry("800x600")
        self.menu_window.configure(bg='#2c3e50')
        
        # Center the window
        self.menu_window.transient(self.root)
        
        # Make window modal
        self.menu_window.focus()
        
        # Bind window close event to resume video
        self.menu_window.protocol("WM_DELETE_WINDOW", self.close_menu_window)
        
        # Main container
        main_frame = tk.Frame(self.menu_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Main Menu", 
                              font=('Arial', 20, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 30))
        
        # Create sections
        self.create_employee_section(main_frame)
        self.create_edit_section(main_frame)
        self.create_settings_section(main_frame)
        self.create_system_section(main_frame)
    
    def create_employee_section(self, parent):
        """Create Employee Check-in Details section"""
        # Section frame
        section_frame = tk.LabelFrame(parent, text="Employee Management", 
                                    font=('Arial', 12, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations
        button_config = {'font': ('Arial', 10, 'bold'), 'width': 30, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Single Employee Check-in Details button
        employee_detail_btn = tk.Button(buttons_frame, text="👥 Employee Details", 
                                       command=self.show_employee_detail_window,
                                       bg='#3498db', fg='white', **button_config)
        employee_detail_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Additional utility buttons
        photos_btn = tk.Button(buttons_frame, text="📸 Check-in Details", 
                              command=self.show_checkin_photos,
                              bg='#e67e22', fg='white', **button_config)
        photos_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export Report button
        export_btn = tk.Button(buttons_frame, text="📤 Export Report", 
                              command=self.export_attendance_report,
                              bg='#27ae60', fg='white', **button_config)
        export_btn.pack(side=tk.LEFT)
    
    def create_edit_section(self, parent):
        """Create Edit section"""
        # Section frame
        section_frame = tk.LabelFrame(parent, text="Edit & Manage", 
                                    font=('Arial', 12, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations
        button_config = {'font': ('Arial', 10, 'bold'), 'width': 25, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Edit Today's Check-ins button
        edit_btn = tk.Button(buttons_frame, text="✏️ Edit Today's Check-ins", 
                            command=self.edit_todays_checkins,
                            bg='#e74c3c', fg='white', **button_config)
        edit_btn.pack(side=tk.LEFT)
    
    def create_settings_section(self, parent):
        """Create Settings section"""
        # Section frame
        section_frame = tk.LabelFrame(parent, text="System Settings", 
                                    font=('Arial', 12, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations
        button_config = {'font': ('Arial', 10, 'bold'), 'width': 25, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Camera Settings button
        camera_btn = tk.Button(buttons_frame, text="📹 Camera Settings", 
                              command=self.show_camera_settings,
                              bg='#34495e', fg='white', **button_config)
        camera_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Recognition Settings button
        recognition_btn = tk.Button(buttons_frame, text="🤖 Recognition Settings", 
                                  command=self.show_recognition_settings,
                                  bg='#34495e', fg='white', **button_config)
        recognition_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Database Settings button
        db_btn = tk.Button(buttons_frame, text="🗄️ Database Settings", 
                          command=self.show_database_settings,
                          bg='#34495e', fg='white', **button_config)
        db_btn.pack(side=tk.LEFT)
    
    def create_system_section(self, parent):
        """Create System section"""
        # Section frame
        section_frame = tk.LabelFrame(parent, text="System Control", 
                                    font=('Arial', 12, 'bold'),
                                    fg='#ecf0f1', bg='#2c3e50',
                                    relief=tk.RAISED, bd=2)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button configurations
        button_config = {'font': ('Arial', 10, 'bold'), 'width': 25, 'height': 2,
                        'relief': tk.RAISED, 'bd': 2, 'cursor': 'hand2'}
        
        # Buttons frame
        buttons_frame = tk.Frame(section_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Reset System button
        reset_btn = tk.Button(buttons_frame, text="🔄 Reset System", 
                             command=self.reset_system,
                             bg='#f39c12', fg='white', **button_config)
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button
        exit_btn = tk.Button(buttons_frame, text="🚪 Exit System", 
                            command=self.cleanup_and_exit,
                            bg='#e74c3c', fg='white', **button_config)
        exit_btn.pack(side=tk.LEFT)
        
        # Close Menu button
        close_btn = tk.Button(buttons_frame, text="❌ Close Menu", 
                             command=self.close_menu_window,
                             bg='#95a5a6', fg='white', **button_config)
        close_btn.pack(side=tk.RIGHT)
    
    def close_menu_window(self):
        """Close the main menu window and resume video"""
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
            delattr(self, 'menu_window')
        
        # Resume video processing
        self.video_paused = False
        print("Video processing resumed")
    
    def show_employee_detail_window(self):
        """Show comprehensive employee detail window"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        # Create employee detail window
        self.employee_detail_window = tk.Toplevel(self.root)
        self.employee_detail_window.title("Employee Check-in Details")
        self.employee_detail_window.geometry("1000x700")
        self.employee_detail_window.configure(bg='#2c3e50')
        
        # Center the window
        self.employee_detail_window.transient(self.root)
        self.employee_detail_window.focus()
        
        # Bind window close event
        self.employee_detail_window.protocol("WM_DELETE_WINDOW", self.close_employee_detail_window)
        
        # Main container
        main_frame = tk.Frame(self.employee_detail_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Employee Check-in Details", 
                              font=('Arial', 18, 'bold'), 
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
        
        # Employee list label
        list_label = tk.Label(left_frame, text="Employee List", 
                             font=('Arial', 14, 'bold'), 
                             fg='#ecf0f1', bg='#2c3e50')
        list_label.pack(pady=(0, 10))
        
        # List frame with scrollbar
        list_container = tk.Frame(left_frame, bg='#2c3e50')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Employee listbox
        self.employee_listbox = tk.Listbox(list_container, 
                                          font=('Arial', 11),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#3498db',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2)
        
        # Scrollbar for employee list
        employee_scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                         command=self.employee_listbox.yview)
        self.employee_listbox.config(yscrollcommand=employee_scrollbar.set)
        
        # Pack employee list components
        self.employee_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        employee_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.employee_listbox.bind('<<ListboxSelect>>', self.on_employee_select)
    
    def create_employee_details_section(self, parent):
        """Create employee details section on the right"""
        # Right frame
        right_frame = tk.Frame(parent, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Employee details label
        details_label = tk.Label(right_frame, text="Employee Details", 
                                font=('Arial', 14, 'bold'), 
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
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Today's Check-ins button
        today_btn = tk.Button(button_frame, text="📊 Today's Check-ins", 
                             command=self.show_todays_checkins,
                             font=('Arial', 10, 'bold'),
                             bg='#3498db', fg='white',
                             width=20, height=2,
                             relief=tk.RAISED, bd=2)
        today_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(button_frame, text="🔄 Refresh", 
                               command=self.refresh_employee_data,
                               font=('Arial', 10, 'bold'),
                               bg='#27ae60', fg='white',
                               width=15, height=2,
                               relief=tk.RAISED, bd=2)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(button_frame, text="❌ Close", 
                             command=self.close_employee_detail_window,
                             font=('Arial', 10, 'bold'),
                             bg='#95a5a6', fg='white',
                             width=15, height=2,
                             relief=tk.RAISED, bd=2)
        close_btn.pack(side=tk.RIGHT)
    
    def load_employee_data(self):
        """Load employee data into the listbox"""
        if not self.attendance_db:
            messagebox.showerror("Error", "Attendance database not initialized.")
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
            messagebox.showerror("Error", f"Failed to load employee data: {e}")
    
    def on_employee_select(self, event):
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
        
        # Employee name
        name_label = tk.Label(self.details_content, text=f"Name: {employee['name']}", 
                             font=('Arial', 14, 'bold'), 
                             fg='#ecf0f1', bg='#34495e')
        name_label.pack(anchor=tk.W, pady=(0, 10))
        
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
        messagebox.showinfo("Refresh", "Employee data refreshed successfully")
    
    def close_employee_detail_window(self):
        """Close the employee detail window"""
        if hasattr(self, 'employee_detail_window'):
            self.employee_detail_window.destroy()
            delattr(self, 'employee_detail_window')
    
    def show_todays_checkins(self):
        """Show detailed view of today's check-ins"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            
            if not checkins:
                messagebox.showinfo("Today's Check-ins", "No check-ins recorded for today.")
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
            
            messagebox.showinfo("Today's Check-ins", report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get today's check-ins: {e}")
    
    def show_employee_list(self):
        """Show list of all registered employees"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        try:
            employees = self.attendance_db.get_employees()
            
            if not employees:
                messagebox.showinfo("Employee List", "No employees registered in the system.")
                return
            
            report = f"Registered Employees ({len(employees)} total)\n\n"
            
            for i, employee in enumerate(employees, 1):
                name = employee['name']
                dept = employee.get('department', 'N/A')
                position = employee.get('position', 'N/A')
                report += f"{i}. {name}\n   Department: {dept}\n   Position: {position}\n\n"
            
            messagebox.showinfo("Employee List", report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get employee list: {e}")
    
    def show_checkin_photos(self):
        """Show comprehensive check-in details window"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        # Create check-in details window
        self.checkin_details_window = tk.Toplevel(self.root)
        self.checkin_details_window.title("Check-in Details")
        self.checkin_details_window.geometry("1200x800")
        self.checkin_details_window.configure(bg='#2c3e50')
        
        # Center the window
        self.checkin_details_window.transient(self.root)
        self.checkin_details_window.focus()
        
        # Bind window close event
        self.checkin_details_window.protocol("WM_DELETE_WINDOW", self.close_checkin_details_window)
        
        # Initialize state variables
        self.current_page = 0
        self.dates_per_page = 30
        self.current_view = "dates"  # "dates" or "employees"
        self.selected_date = None
        
        # Main container
        main_frame = tk.Frame(self.checkin_details_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Check-in Details", 
                              font=('Arial', 18, 'bold'), 
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
        
        # Date header
        date_header = tk.Label(date_frame, text="Check-in Dates", 
                              font=('Arial', 14, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        date_header.pack(pady=(0, 10))
        
        # Date list container
        date_list_container = tk.Frame(date_frame, bg='#2c3e50')
        date_list_container.pack(fill=tk.BOTH, expand=True)
        
        # Date listbox
        self.checkin_listbox = tk.Listbox(date_list_container, 
                                         font=('Arial', 12, 'bold'),
                                         bg='#34495e', 
                                         fg='#ecf0f1',
                                         selectbackground='#3498db',
                                         selectforeground='white',
                                         relief=tk.SUNKEN,
                                         bd=2)
        
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
        
        # Employee header
        self.employee_header = tk.Label(employee_frame, text="Employees (Select a date)", 
                                       font=('Arial', 14, 'bold'), 
                                       fg='#ecf0f1', bg='#2c3e50')
        self.employee_header.pack(pady=(0, 10))
        
        # Employee list container
        employee_list_container = tk.Frame(employee_frame, bg='#2c3e50')
        employee_list_container.pack(fill=tk.BOTH, expand=True)
        
        # Employee listbox
        self.employee_listbox = tk.Listbox(employee_list_container, 
                                          font=('Arial', 12),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#27ae60',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2)
        
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
                messagebox.showwarning("Warning", "Attendance database not available")
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
            messagebox.showerror("Error", f"Failed to load employees for date: {e}")
    
    def create_checkin_right_section(self, parent):
        """Create right section for check-in photos"""
        # Right frame
        right_frame = tk.Frame(parent, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Photo section label
        photo_label = tk.Label(right_frame, text="Check-in Photo", 
                              font=('Arial', 14, 'bold'), 
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
        close_btn = tk.Button(control_frame, text="❌ Close", 
                             command=self.close_checkin_details_window,
                             font=('Arial', 10, 'bold'),
                             bg='#e74c3c', fg='white',
                             width=15, height=2,
                             relief=tk.RAISED, bd=2)
        close_btn.pack(side=tk.RIGHT)
    
    def load_checkin_dates(self):
        """Load check-in dates with pagination"""
        if not self.attendance_db:
            messagebox.showerror("Error", "Attendance database not initialized.")
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
            self.current_view = "dates"
            self.hide_back_button()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load check-in dates: {e}")
            messagebox.showerror("Error", f"Failed to load employees for date: {e}")
                selected_record = self.checkin_employees_data[index]
                self.show_checkin_photo(selected_record)
    
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
    
    def update_left_header(self, title, subtitle):
        """Update the left section header"""
        # Clear existing widgets
        for widget in self.left_header_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = tk.Label(self.left_header_frame, text=title, 
                              font=('Arial', 14, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = tk.Label(self.left_header_frame, text=subtitle, 
                                 font=('Arial', 10), 
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(anchor=tk.W)
    
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
        self.current_view = "dates"
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
    
    def close_checkin_details_window(self):
        """Close the check-in details window"""
        if hasattr(self, 'checkin_details_window'):
            self.checkin_details_window.destroy()
            delattr(self, 'checkin_details_window')
    
    def export_attendance_report(self):
        """Export attendance report to CSV"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            import csv
            
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get attendance records
            records = self.attendance_db.get_attendance_report(today, today)
            
            if not records:
                messagebox.showinfo("Export Report", "No attendance records found for today.")
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
            
            messagebox.showinfo("Export Complete", f"Attendance report exported to: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")
    
    def show_camera_settings(self):
        """Show camera settings dialog"""
        settings_text = """Camera Settings:

• Resolution: 640x480 (optimized for performance)
• Frame Rate: 10 FPS
• Auto Exposure: Enabled
• Buffer Size: 1

To modify camera settings, edit the start_camera_optimized() method."""
        
        messagebox.showinfo("Camera Settings", settings_text)
    
    def show_recognition_settings(self):
        """Show face recognition settings dialog"""
        settings_text = """Face Recognition Settings:

• Model: FaceNet (MTCNN + InceptionResnetV1)
• Detection Threshold: 0.8
• Recognition Threshold: 0.7
• Face Detection Interval: Every 5th frame
• Recognition Cooldown: 1 second

To modify recognition settings, edit the relevant methods."""
        
        messagebox.showinfo("Recognition Settings", settings_text)
    
    def show_database_settings(self):
        """Show database settings dialog"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        try:
            # Get database info
            employees = self.attendance_db.get_employees()
            employee_count = len(employees)
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            today_checkins = len([r for r in records if r.get('check_in_time')])
            
            settings_text = f"""Database Settings:

• Database Type: SQLite
• Total Employees: {employee_count}
• Today's Check-ins: {today_checkins}
• Database File: attendance.db

Database location and connection details can be found in attendance_database.py"""
            
            messagebox.showinfo("Database Settings", settings_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database info: {e}")
    
    def reset_system(self):
        """Reset system settings"""
        result = messagebox.askyesno("Reset System", 
                                   "Are you sure you want to reset the system?\n\n"
                                   "This will:\n"
                                   "• Clear all face recognition data\n"
                                   "• Reset camera settings\n"
                                   "• Clear attendance cache\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                # Clear face embeddings
                self.face_embeddings = {}
                self.save_face_embeddings()
                
                # Clear embedding cache
                self.embedding_cache.clear()
                
                # Reset tracking
                self.tracked_faces.clear()
                
                # Refresh model
                self.refresh_model()
                
                messagebox.showinfo("Reset Complete", "System has been reset successfully.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset system: {e}")
    
    def edit_todays_checkins(self):
        """Edit today's check-ins with video pause and deletion options"""
        if not self.attendance_db:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            
            if not checkins:
                messagebox.showinfo("Edit Check-ins", "No check-ins recorded for today.")
                return
            
            # Pause video processing
            self.video_paused = True
            
            # Create edit window
            self.create_edit_checkins_window(checkins)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load check-ins for editing: {e}")
            self.video_paused = False
    
    def create_edit_checkins_window(self, checkins):
        """Create window for editing check-ins"""
        # Create edit window
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Today's Check-ins")
        self.edit_window.geometry("600x500")
        self.edit_window.configure(bg='#2c3e50')
        
        # Center the window
        self.edit_window.transient(self.root)
        
        # Make window modal
        self.edit_window.focus()
        
        # Main container
        main_frame = tk.Frame(self.edit_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Edit Today's Check-ins", 
                              font=('Arial', 16, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instruction_label = tk.Label(main_frame, 
                                   text="Click on a check-in entry to delete it.\nVideo is paused during editing.",
                                   font=('Arial', 10), 
                                   fg='#bdc3c7', bg='#2c3e50')
        instruction_label.pack(pady=(0, 15))
        
        # Create frame for listbox and scrollbar
        list_frame = tk.Frame(main_frame, bg='#2c3e50')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Listbox for check-ins
        self.checkins_listbox = tk.Listbox(list_frame, 
                                          font=('Arial', 11),
                                          bg='#34495e', 
                                          fg='#ecf0f1',
                                          selectbackground='#4a6741',
                                          selectforeground='white',
                                          relief=tk.SUNKEN,
                                          bd=2,
                                          height=15)
        
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
        
        # Delete button
        delete_button = tk.Button(button_frame, text="Delete Selected", 
                                command=self.delete_selected_checkin,
                                font=('Arial', 12, 'bold'),
                                bg='#e74c3c', fg='white',
                                relief=tk.RAISED, bd=3,
                                cursor='hand2')
        delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_button = tk.Button(button_frame, text="Refresh List", 
                                 command=self.refresh_checkins_list,
                                 font=('Arial', 12, 'bold'),
                                 bg='#3498db', fg='white',
                                 relief=tk.RAISED, bd=3,
                                 cursor='hand2')
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_button = tk.Button(button_frame, text="Close", 
                               command=self.close_edit_window,
                               font=('Arial', 12, 'bold'),
                               bg='#95a5a6', fg='white',
                               relief=tk.RAISED, bd=3,
                               cursor='hand2')
        close_button.pack(side=tk.RIGHT)
        
        # Bind double-click event
        self.checkins_listbox.bind('<Double-Button-1>', self.on_checkin_double_click)
        
        # Store checkins data for reference
        self.edit_checkins_data = checkins
    
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
            messagebox.showerror("Error", "Attendance database not initialized.")
            return
        selection = self.checkins_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a check-in entry to delete.")
            return
        
        index = selection[0]
        if index >= len(self.edit_checkins_data):
            messagebox.showerror("Error", "Invalid selection.")
            return
        
        # Get the record to delete
        record_to_delete = self.edit_checkins_data[index]
        name = record_to_delete['name']
        check_in_time = record_to_delete['check_in_time']
        
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
        result = messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to delete this check-in?\n\n"
                                   f"Employee: {name}\n"
                                   f"Time: {formatted_time}\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                # Delete from database
                success = self.attendance_db.delete_checkin(name, check_in_time)
                
                if success:
                    # Remove from local data
                    del self.edit_checkins_data[index]
                    
                    # Refresh the listbox
                    self.populate_checkins_listbox(self.edit_checkins_data)
                    
                    # Update the main textbox
                    self.load_existing_checkins()
                    
                    messagebox.showinfo("Success", f"Check-in for {name} has been deleted.")
                    
                    # If no more check-ins, close the window
                    if not self.edit_checkins_data:
                        self.close_edit_window()
                else:
                    messagebox.showerror("Error", f"Failed to delete check-in for {name}.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete check-in: {e}")
    
    def refresh_checkins_list(self):
        """Refresh the check-ins list"""
        if not self.attendance_db:
            messagebox.showerror("Error", "Attendance database not initialized.")
            return
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            records = self.attendance_db.get_attendance_report(today, today)
            
            checkins = [record for record in records if record.get('check_in_time')]
            self.edit_checkins_data = checkins
            
            self.populate_checkins_listbox(checkins)
            
            if not checkins:
                messagebox.showinfo("Refresh Complete", "No check-ins found for today.")
                self.close_edit_window()
            else:
                messagebox.showinfo("Refresh Complete", f"List refreshed. {len(checkins)} check-ins found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh list: {e}")
    
    def close_edit_window(self):
        """Close the edit window and resume video"""
        if hasattr(self, 'edit_window'):
            self.edit_window.destroy()
            delattr(self, 'edit_window')
        
        # Resume video processing
        self.video_paused = False
        print("Video processing resumed")
    
    def load_existing_checkins(self):
        """Load today's existing check-ins from the database and display them in the textbox"""
        if not self.attendance_db:
            # If no database, just show the default message
            self.checkin_textbox.config(state=tk.NORMAL)
            self.checkin_textbox.delete(1.0, tk.END)
            self.checkin_textbox.insert(tk.END, "No check-ins today\n")
            self.checkin_textbox.config(state=tk.DISABLED)
            return
        
        try:
            # Get today's date
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get today's attendance records
            records = self.attendance_db.get_attendance_report(today, today)
            
            # Filter for records with check-in times
            checkins = [record for record in records if record.get('check_in_time')]
            
            # Update the textbox
            self.checkin_textbox.config(state=tk.NORMAL)
            self.checkin_textbox.delete(1.0, tk.END)
            
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
                    self.checkin_textbox.insert(tk.END, entry)
                
                # Auto-scroll to the bottom
                self.checkin_textbox.see(tk.END)
                print(f"Loaded {len(checkins)} existing check-ins for today")
            else:
                self.has_checkins_today = False
                self.checkin_textbox.insert(tk.END, "No check-ins today\n")
            
            self.checkin_textbox.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading existing check-ins: {e}")
            # Show default message on error
            self.checkin_textbox.config(state=tk.NORMAL)
            self.checkin_textbox.delete(1.0, tk.END)
            self.checkin_textbox.insert(tk.END, "No check-ins today\n")
            self.checkin_textbox.config(state=tk.DISABLED)
    
    def start_camera_optimized(self):
        """Start camera with optimized settings"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.camera = cv2.VideoCapture(1)
                if not self.camera.isOpened():
                    messagebox.showerror("Error", "Could not open camera")
                    return
            
            # Optimized camera settings for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Optimize exposure
            
            print("Camera started with optimized settings")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def start_video_loop(self):
        """Start optimized video processing loop"""
        self.update_video_optimized()
    
    def update_video_optimized(self):
        """Optimized video processing with better performance"""
        if not self.camera:
            return
        
        # Frame rate control
        current_time = time.time()
        if (current_time - self.last_frame_time) < (self.frame_interval / 1000.0):
            self.root.after(5, self.update_video_optimized)
            return
        
        self.last_frame_time = current_time
        self.frame_count += 1
        
        try:
            ret, frame = self.camera.read()
                       
            # Rotate frame
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if not ret or frame is None:
                self.root.after(self.frame_interval, self.update_video_optimized)
                return
            
            # Validate frame dimensions
            if frame.shape[0] <= 0 or frame.shape[1] <= 0:
                self.root.after(self.frame_interval, self.update_video_optimized)
                return
            
            # Check if video is paused (during training)
            if self.video_paused:
                # Display the last frame without processing new faces
                if hasattr(self, 'last_display_frame') and self.last_display_frame is not None:
                    paused_frame = self.last_display_frame.copy()
                    # Add pause indicator overlay
                   
                    cv2.putText(paused_frame, "Please wait...", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    self.display_frame_optimized(paused_frame)
                else:
                    # Add pause overlay to current frame
                    paused_frame = frame.copy()
        
                    cv2.putText(paused_frame, "Please wait...", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    self.display_frame_optimized(paused_frame)
                    
                # Update UI less frequently when paused
                if self.frame_count % (self.ui_update_interval * 3) == 0:
                    self.update_ui_labels(0)  # No new faces being detected
                    
                self.root.after(self.frame_interval, self.update_video_optimized)
                return
            
            # Store frame for pause display
            self.last_display_frame = frame.copy()
            
            # Optimized face detection with caching
            faces = self.get_cached_faces(frame)
            
            # Process faces efficiently
            if faces:
                self.process_faces_optimized(frame, faces)
            
            # Display frame
            self.display_frame_optimized(frame)
            
            # Update UI efficiently
            if self.frame_count % self.ui_update_interval == 0:
                self.update_ui_labels(len(faces))
            
        except Exception as e:
            print(f"Video update error: {e}")
        finally:
            # Memory cleanup and canvas size reset
            if self.frame_count % 10 == 0:  # Every 60 frames
                gc.collect()
                # Reset canvas size cache to handle window resizing
                self.canvas_size = None
        
        self.root.after(self.frame_interval, self.update_video_optimized)
    
    def get_cached_faces(self, frame):
        """Get faces with intelligent caching"""
        # Use cached faces if available and recent
        if len(self.face_cache) > 0 and self.frame_count % self.face_detection_interval != 0:
            return self.face_cache[-1] if self.face_cache else []
        
        # Detect new faces
        faces = self.detect_faces_optimized(frame)
        
        # Cache the result
        self.face_cache.append(faces)
        
        return faces
    
    def detect_faces_optimized(self, frame):
        """Optimized face detection with MTCNN"""
        try:
            if not self.mtcnn:
                return []
            
            # Resize frame for faster processing
            scale_factor = 0.5
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
            
            # Convert to PIL
            frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Detect faces
            with torch.no_grad():
                detection_result = self.mtcnn.detect(frame_pil)
            
            faces = []
            if detection_result and len(detection_result) >= 2:
                boxes, probs = detection_result[0], detection_result[1]
                if boxes is not None and probs is not None:
                    for box, prob in zip(boxes, probs):
                        if prob > 0.8:  # Higher threshold for better accuracy
                            # Scale back to original size
                            x, y, x2, y2 = (box / scale_factor).astype(int)
                            w, h = x2 - x, y2 - y
                            
                            # Validate coordinates
                            if self.is_valid_face_region(x, y, w, h, frame.shape):
                                faces.append((x, y, w, h))
            
            return faces
            
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
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
            
            if self.frame_count % 3 == 0:  # Every 3rd frame
                name, confidence = self.process_face_recognition_optimized(frame, x, y, w, h)
            else:
                # Use tracking information for non-recognition frames
                name, confidence = self.get_tracked_face_info((x, y, w, h))
            
            face_names.append(name)
            
            # Print recognition info for debugging (first face only)
            if i == 0:
                confidence_text = f"{round(confidence * 100)}%"
                print(f"Recognition: {name} ({confidence_text})")
            
            # Handle attendance for recognized faces
            if name != "Unknown" and confidence > 0.7:
                self.handle_attendance_optimized(name)
            
            # Capture for training
            if self.is_capturing and self.capture_count < self.max_captures:
                self.capture_face_optimized(frame[y:y+h, x:x+w])
        
        # Update face tracking first
        self.update_face_tracking(current_faces, face_names)
        
        # Draw faces with tracking information
        for i, (x, y, w, h) in enumerate(current_faces):
            name = face_names[i]
            confidence = 0.0
            track_id = None
            
            # Find corresponding track ID and get updated info
            for tid, track_data in self.tracked_faces.items():
                if self.calculate_rectangle_distance((x, y, w, h), track_data['rectangle']) < 10:
                    name = track_data['name']
                    confidence = track_data['confidence']
                    track_id = tid
                    break
            
            # Draw face with tracking info
            self.draw_face_with_tracking(frame, x, y, w, h, name, confidence, track_id)
        
        # Print debug information
        self.print_tracking_debug()
        
        self.current_frame_faces = current_faces
    
    def process_face_recognition_optimized(self, frame, x, y, w, h):
        """Optimized face recognition processing - returns (name, confidence)"""
        try:
            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size == 0:
                return "Unknown", 0.0
            
            # Generate cache key
            cache_key = hash(face_roi.tobytes())
            
            # Check embedding cache
            if cache_key in self.embedding_cache:
                face_embedding = self.embedding_cache[cache_key]
            else:
                face_embedding = self.get_face_embedding_optimized(face_roi)
                if face_embedding is not None:
                    self.embedding_cache[cache_key] = face_embedding
                    # Limit cache size
                    if len(self.embedding_cache) > 100:
                        self.embedding_cache.pop(next(iter(self.embedding_cache)))
            
            if face_embedding is not None:
                name, similarity = self.recognize_face_embedding_optimized(face_embedding)
                return name, similarity
            else:
                return "Unknown", 0.0
                    
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown", 0.0
    
    def get_face_embedding_optimized(self, face_image):
        """Optimized face embedding extraction"""
        try:
            if not self.facenet_model:
                return None
            
            # Resize and preprocess
            face_resized = cv2.resize(face_image, (160, 160))
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            
            # Get aligned face
            face_tensor = None
            if self.mtcnn is not None:
                face_tensor = self.mtcnn(face_pil)
            
            if face_tensor is not None:
                if face_tensor.dim() == 3:
                    face_tensor = face_tensor.unsqueeze(0)
                
                with torch.no_grad():
                    embedding = self.facenet_model(face_tensor).cpu().numpy()
                return embedding.flatten()
            
            return None
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def recognize_face_embedding_optimized(self, face_embedding, threshold=0.7):
        """Optimized face recognition with vectorized operations"""
        try:
            if face_embedding is None or not self.face_embeddings:
                return "Unknown", 0
            
            best_match = "Unknown"
            best_similarity = 0
            
            face_embedding_normalized = face_embedding / np.linalg.norm(face_embedding)
            
            for name, stored_embeddings in self.face_embeddings.items():
                if stored_embeddings:
                    # Vectorized similarity calculation
                    embeddings_array = np.array(stored_embeddings)
                    embeddings_normalized = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)
                    
                    similarities = np.dot(embeddings_normalized, face_embedding_normalized)
                    max_similarity = np.max(similarities)
                    
                    if max_similarity > best_similarity:
                        best_similarity = max_similarity
                        best_match = name
            
            return (best_match, best_similarity) if best_similarity > threshold else ("Unknown", best_similarity)
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown", 0
    
    def handle_attendance_optimized(self, name):
        """Optimized attendance handling with database-based checking"""
        if not self.attendance_db:
            return
        
        current_time = time.time()
        if name in self.last_recognition_time:
            if current_time - self.last_recognition_time[name] < self.recognition_cooldown:
                return
        
        self.last_recognition_time[name] = current_time
        
        try:
            # The database check_in method already handles checking if person checked in today
            if self.attendance_db.check_in(name):
                # Save check-in photo
                self.save_checkin_photo(name)
                
                self.update_last_checkin_display(name)
                print(f"✅ {name} checked in at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"ℹ️  {name} already checked in today at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error checking in {name}: {e}")
    
    def save_checkin_photo(self, name):
        """Save a photo of the current video feed when employee checks in"""
        try:
            # Get the current frame
            if not hasattr(self, 'last_display_frame') or self.last_display_frame is None:
                print("⚠️  No video frame available to save")
                return
            
            frame = self.last_display_frame.copy()
            
            # Get current date and time
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H-%M-%S")  # Use hyphens for filename compatibility
            
            # Create folder structure: CheckinPhoto/{current_date}/
            base_folder = "CheckinPhoto"
            date_folder = os.path.join(base_folder, current_date)
            
            # Create directories if they don't exist
            os.makedirs(date_folder, exist_ok=True)
            
            # Clean the employee name for filename (remove special characters)
            clean_name = self.get_clean_name(name)
            
            # Create filename: {employee_name}_{time}.jpg
            filename = f"{clean_name}_{current_time}.jpg"
            filepath = os.path.join(date_folder, filename)
            
            # Save the photo
            success = cv2.imwrite(filepath, frame)
            
            if success:
                print(f"📸 Check-in photo saved: {filepath}")
            else:
                print(f"❌ Failed to save check-in photo: {filepath}")
                
        except Exception as e:
            print(f"❌ Error saving check-in photo for {name}: {e}")
    
    def display_frame_optimized(self, frame):
        """Optimized frame display with better memory management"""
        try:
            # Validate frame
            if frame is None or frame.size == 0:
                return
            
            # Cache canvas size with validation
            if not self.canvas_size:
                win_w = self.root.winfo_width()
                win_h = self.root.winfo_height()
                
                # Ensure minimum window size
                if win_w <= 0 or win_h <= 0:
                    return  # Window not ready yet
                
                self.canvas_size = (win_w, win_h)
            
            win_w, win_h = self.canvas_size
            
            # Validate window dimensions
            if win_w <= 0 or win_h <= 0:
                return
            
            # Convert and resize efficiently
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Validate frame dimensions
            if frame_pil.width <= 0 or frame_pil.height <= 0:
                return
            
            # Calculate optimal size with validation
            frame_aspect = frame_pil.width / frame_pil.height
            window_aspect = win_w / win_h
            
            if frame_aspect > window_aspect:
                new_width = win_w
                new_height = int(win_w / frame_aspect)
            else:
                new_height = win_h
                new_width = int(win_h * frame_aspect)
            
            # Ensure minimum dimensions
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            # Validate final dimensions
            if new_width <= 0 or new_height <= 0:
                return
            
            # Resize with optimized method
            frame_pil = frame_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update canvas
            self.canvas.delete("all")
            x_offset = (win_w - new_width) // 2
            y_offset = (win_h - new_height) // 2
            self.canvas.create_image(x_offset, y_offset, anchor='nw', image=frame_tk)
            
            # Keep reference
            self.current_frame_tk = frame_tk
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def update_ui_labels(self, num_faces):
        """Print debug info instead of updating labels"""
        num_tracked = len(self.tracked_faces)
        
        if num_faces > 0:
            print(f"Status: {num_faces} face(s) detected, {num_tracked} tracked")
        else:
            if self.frame_count % 30 == 0:
                print(f"Status: No faces detected, {num_tracked} tracked")
    
    def is_valid_face_region(self, x, y, w, h, frame_shape):
        """Validate face region coordinates"""
        frame_height, frame_width = frame_shape[:2]
        return (0 <= x < frame_width and 0 <= y < frame_height and 
                x + w <= frame_width and y + h <= frame_height and 
                w > 20 and h > 20)
    
    def calculate_rectangle_distance(self, rect1, rect2):
        """Calculate distance between two rectangles (center-to-center)"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Calculate centers
        center1_x = x1 + w1 // 2
        center1_y = y1 + h1 // 2
        center2_x = x2 + w2 // 2
        center2_y = y2 + h2 // 2
        
        # Euclidean distance
        distance = ((center1_x - center2_x) ** 2 + (center1_y - center2_y) ** 2) ** 0.5
        return distance
    
    def match_faces_to_tracks(self, current_faces):
        """Match current face rectangles to existing tracks"""
        matched_pairs = []
        unmatched_faces = list(range(len(current_faces)))
        unmatched_tracks = list(self.tracked_faces.keys())
        
        # Find best matches based on distance
        for face_idx, face_rect in enumerate(current_faces):
            best_track_id = None
            best_distance = float('inf')
            
            for track_id in unmatched_tracks:
                track_data = self.tracked_faces[track_id]
                track_rect = track_data['rectangle']
                
                distance = self.calculate_rectangle_distance(face_rect, track_rect)
                
                if distance < self.max_track_distance and distance < best_distance:
                    best_distance = distance
                    best_track_id = track_id
            
            if best_track_id is not None:
                matched_pairs.append((face_idx, best_track_id))
                unmatched_faces.remove(face_idx)
                unmatched_tracks.remove(best_track_id)
        
        return matched_pairs, unmatched_faces, unmatched_tracks
    
    def update_face_tracking(self, current_faces, face_names):
        """Update face tracking data with current frame information"""
        # Match current faces to existing tracks
        matched_pairs, unmatched_faces, unmatched_tracks = self.match_faces_to_tracks(current_faces)
        
        # Update matched tracks
        for face_idx, track_id in matched_pairs:
            track_data = self.tracked_faces[track_id]
            track_data['rectangle'] = current_faces[face_idx]
            track_data['last_seen'] = self.frame_count
            
            # Update name if recognition was successful
            if face_idx < len(face_names) and face_names[face_idx] != "Unknown":
                track_data['name'] = face_names[face_idx]
                track_data['confidence'] = min(track_data['confidence'] + 0.1, 1.0)  # Increase confidence
            else:
                track_data['confidence'] = max(track_data['confidence'] - 0.05, 0.1)  # Decrease confidence
        
        # Create new tracks for unmatched faces
        for face_idx in unmatched_faces:
            self.face_track_id += 1
            track_id = self.face_track_id
            
            name = face_names[face_idx] if face_idx < len(face_names) else "Unknown"
            confidence = 0.8 if name != "Unknown" else 0.1
            
            self.tracked_faces[track_id] = {
                'rectangle': current_faces[face_idx],
                'name': name,
                'confidence': confidence,
                'last_seen': self.frame_count,
                'created_frame': self.frame_count
            }
        
        # Remove old tracks that haven't been seen
        tracks_to_remove = []
        for track_id in unmatched_tracks:
            track_data = self.tracked_faces[track_id]
            if self.frame_count - track_data['last_seen'] > self.track_timeout:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracked_faces[track_id]
    
    def get_tracked_face_info(self, face_rect):
        """Get tracking information for a face rectangle"""
        for track_id, track_data in self.tracked_faces.items():
            if self.calculate_rectangle_distance(face_rect, track_data['rectangle']) < 10:
                return track_data['name'], track_data['confidence']
        return "Unknown", 0.0
    
    def print_tracking_debug(self):
        """Print debugging information about face tracking"""
        if self.frame_count % 60 == 0:  # Print every 60 frames
            print(f"\n--- Frame {self.frame_count} Tracking Debug ---")
            print(f"Total tracked faces: {len(self.tracked_faces)}")
            for track_id, track_data in self.tracked_faces.items():
                print(f"Track {track_id}: {track_data['name']} (conf: {track_data['confidence']:.2f}, "
                      f"last_seen: {track_data['last_seen']}, rect: {track_data['rectangle']})")
            print("----------------------------------------\n")
    
    def draw_face_with_tracking(self, frame, x, y, w, h, name, confidence, track_id=None):
        """Draw face rectangle with tracking information"""
        # Choose color based on recognition confidence
        if name != "Unknown" and confidence > 0.7:
            color = (0, 255, 0)  # Green for high confidence
        elif name != "Unknown" and confidence > 0.3:
            color = (0, 255, 255)  # Yellow for medium confidence
        else:
            color = (255, 0, 0)  # Blue for unknown/low confidence
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Display name and confidence
        confidence_text = f"{round(confidence * 100)}%"
        cv2.putText(frame, name, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, confidence_text, (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        
        # Display track ID if available
        if track_id is not None:
            cv2.putText(frame, f"ID:{track_id}", (x+w-40, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
    
    def capture_face_optimized(self, face_img):
        """Optimized face capture"""
        try:
            if face_img is None or face_img.size == 0 or min(face_img.shape[:2]) < 20:
                return
            
            # Resize to standard size
            face_img = cv2.resize(face_img, (160, 160))
            
            # Generate filename using user name instead of user ID
            # Clean the user name for filename (remove special characters)
            clean_name = self.get_clean_name(self.current_user_name)
            
            # Create user directory if it doesn't exist
            user_dir = f"dataset/{clean_name}"
            os.makedirs(user_dir, exist_ok=True)
            
            # Count existing images for this user in their directory
            existing_count = len([f for f in os.listdir(user_dir) 
                                if f.startswith(f'{clean_name}_') and f.endswith('.jpg')])
            
            filename = f"{user_dir}/{clean_name}_{existing_count + self.capture_count + 1}.jpg"
            cv2.imwrite(filename, face_img)
            
            self.capture_count += 1
            time.sleep(0.5)
            self.progress_var.set(self.capture_count)
            
            if self.capture_count >= self.max_captures:
                self.video_paused = True
                self.stop_capture()
                
        except Exception as e:
            print(f"Capture error: {e}")

    def start_capture(self):
        """Optimized face capture process"""
        if self.is_capturing:
            return
        self.video_paused = True
        # Get user name input
        name = self.get_user_name_input()
        if not name:
            self.video_paused = False
            return
        self.show_capture_instructions()
        # Set up user information
        self.setup_user_for_capture(name)
        
        # Start capturing
        self.capture_count = 0
        self.is_capturing = True
        self.video_paused = False
        
        # Show capture instructions
 
        
        # Update UI
        self.capture_button.config(text="Capturing...", bg='#e74c3c', state=tk.DISABLED)
        self.progress_frame.place(relx=0.5, rely=0.85, anchor='center')  # Show progress bar
        self.progress_var.set(0)
        print(f"Status: Capturing faces for {name}...")
        
        # Pause video processing during training phase
 
        print("Video feed paused for training")
        
        print(f"Started capturing faces for {name}")
    
    def get_user_name_input(self):
        """Get user name input with optimized virtual keyboard"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Face Recognition Training - Name Input")
        dialog.configure(bg='#2c3e50')
        
        # Center dialog
        dialog.transient(self.root)
      
        dialog.focus()
        
        # Center on screen with optimized size
        dialog_width, dialog_height = 800, 650
        x = (self.screen_width - dialog_width) // 2
        y = (self.screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Main container with better padding
        main_frame = tk.Frame(dialog, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title section
        title_label = tk.Label(main_frame, text="Enter Name for Training", 
                              font=('Arial', 16, 'bold'), 
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 15))
        
        # Entry section with enhanced styling
        entry_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        entry_label = tk.Label(entry_frame, text="Name:", 
                              font=('Arial', 12, 'bold'), 
                              fg='#bdc3c7', bg='#34495e')
        entry_label.pack(side=tk.LEFT, padx=(10, 5), pady=5)
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(entry_frame, textvariable=name_var, 
                            font=('Arial', 16), width=35, 
                            relief=tk.SUNKEN, bd=2, bg='#ecf0f1')
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10), pady=5)
   
        name_entry.icursor(tk.END)
        
        # Result storage
        result = {'name': ''}
        
        # Optimized keyboard functions
        def update_cursor():
            """Ensure cursor stays at end"""
            name_entry.focus()
            name_entry.icursor(tk.END)
        
        def press_key(key):
            """Optimized key press with auto-capitalization"""
            current_text = name_var.get()
            if key == ' ':
                name_var.set(current_text + ' ')
            else:
                # Smart capitalization
                if len(current_text) == 0 or current_text[-1] == ' ':
                    name_var.set(current_text + key.upper())
                else:
                    name_var.set(current_text + key.lower())
            update_cursor()
        
        def backspace():
            """Optimized backspace"""
            current_text = name_var.get()
            if current_text:
                name_var.set(current_text[:-1])
            update_cursor()
        
        def clear_text():
            """Optimized clear"""
            name_var.set("")
            update_cursor()
        
        def confirm():
            """Validate and confirm input"""
            name = name_var.get().strip()
            if name:
                result['name'] = name
                dialog.destroy()
            else:
                # Flash entry field for error feedback
                original_bg = name_entry.cget('bg')
                name_entry.config(bg='#ffcccb')
                dialog.after(200, lambda: name_entry.config(bg=original_bg))
                update_cursor()
        
        def cancel():
            """Cancel input"""
            
            dialog.destroy()
        
        # Enhanced button creation with better styling
        def create_key_button(parent, text, command, style='normal'):
            """Create optimized keyboard button"""
            colors = {
                'normal': {'bg': '#34495e', 'fg': 'white', 'active_bg': '#4a6741'},
                'special': {'bg': '#3498db', 'fg': 'white', 'active_bg': '#2980b9'},
                'action': {'bg': '#27ae60', 'fg': 'white', 'active_bg': '#229954'},
                'danger': {'bg': '#e74c3c', 'fg': 'white', 'active_bg': '#c0392b'}
            }
            
            color = colors.get(style, colors['normal'])
            
            btn = tk.Button(parent, text=text, width=5, height=3,
                           font=('Arial', 12, 'bold'),
                           bg=color['bg'], fg=color['fg'],
                           activebackground=color['active_bg'],
                           relief=tk.RAISED, bd=2,
                           command=command, cursor='hand2')
            
            # Enhanced hover effects
            def on_enter(e):
                btn.config(bg=color['active_bg'])
            
            def on_leave(e):
                btn.config(bg=color['bg'])
            
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            return btn
        
        # Control buttons section
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        confirm_btn = tk.Button(control_frame, text="✓ Confirm", command=confirm,
                               font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                               width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        cancel_btn = tk.Button(control_frame, text="✕ Cancel", command=cancel,
                              font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                              width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg='#7f8c8d')
        separator.pack(fill=tk.X, pady=10)
        
        # Optimized keyboard layout
        keyboard_frame = tk.Frame(main_frame, bg='#2c3e50')
        keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define keyboard layout with better organization
        keyboard_layout = [
            {'keys': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], 'style': 'normal'},
            {'keys': ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'], 'style': 'normal'},
            {'keys': ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'], 'style': 'normal'},
            {'keys': ['Z', 'X', 'C', 'V', 'B', 'N', 'M'], 'style': 'normal'}
        ]
        
        # Create number and letter rows
        for row_data in keyboard_layout:
            row_frame = tk.Frame(keyboard_frame, bg='#2c3e50')
            row_frame.pack(pady=2)
            
            for key in row_data['keys']:
                btn = create_key_button(row_frame, key, 
                                       lambda k=key.lower(): press_key(k),
                                       row_data['style'])
                btn.pack(side=tk.LEFT)
        
        # Special keys row
        special_frame = tk.Frame(keyboard_frame, bg='#2c3e50')
        special_frame.pack(pady=5)
        
        # Space bar (wider)
        space_btn = tk.Button(special_frame, text="SPACE", width=20, height=3,
                             font=('Arial', 10, 'bold'), bg='#34495e', fg='white',
                             activebackground='#4a6741', relief=tk.RAISED, bd=2,
                             command=lambda: press_key(' '), cursor='hand2')
        space_btn.pack(side=tk.LEFT, padx=2)
        
        # Backspace
        back_btn = create_key_button(special_frame, "⌫", backspace, 'danger')
        back_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear
        clear_btn = create_key_button(special_frame, "Clear", clear_text, 'special')
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Enter
        enter_btn = create_key_button(special_frame, "Enter", confirm, 'action')
        enter_btn.pack(side=tk.LEFT, padx=2)
        
        # Enhanced event bindings
        def on_entry_click(event):
            update_cursor()
            return "break"
        
        def on_key_press(event):
            """Handle physical keyboard input"""
            if event.keysym == 'Return':
                confirm()
            elif event.keysym == 'Escape':
                cancel()
            elif event.keysym == 'BackSpace':
                backspace()
                return "break"
            elif event.char.isprintable() and event.char != ' ':
                press_key(event.char)
                return "break"
            elif event.keysym == 'space':
                press_key(' ')
                return "break"
        
        # Bind events
        name_entry.bind('<Button-1>', on_entry_click)
        name_entry.bind('<FocusIn>', lambda e: update_cursor())
        dialog.bind('<Key>', on_key_press)
        dialog.bind('<Return>', lambda e: confirm())
        dialog.bind('<Escape>', lambda e: cancel())
        
        # Focus management
        dialog.focus()
        name_entry.focus()
        
        # Wait for dialog completion
        dialog.wait_window()
        
        return result['name'] if result['name'] else None
    
    def setup_user_for_capture(self, user_name):
        """Set up user information for capture"""
        # Check if user already exists
        existing_user_clean_name = self.find_existing_user(user_name)
        
        if existing_user_clean_name is not None:
            # Clean the user name for filename (remove special characters)
            clean_name = self.get_clean_name(user_name)
            
            self.current_user_name = user_name
            self.is_new_user = False  # Track that this is an existing user
            print(f"Found existing user '{user_name}' with clean name '{clean_name}'")
        else:
            # New user
            self.current_user_name = user_name
            self.is_new_user = True  # Track that this is a new user
            self.save_user_name(0, user_name)  # user_id parameter is not used anymore
            print(f"Created new user '{user_name}'")
        
        # Add to names list if not present
        if user_name not in self.names:
            self.names.append(user_name)
    
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
    
    def get_clean_name(self, name):
        """Convert user name to clean filename format"""
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')
        return clean_name
    
    def find_existing_user(self, user_name):
        """Find existing user by name"""
        if not os.path.exists('dataset'):
            return None
        
        # Clean the user name for filename (remove special characters)
        clean_name = self.get_clean_name(user_name)
        
        # Check if user directory exists
        user_dir = f"dataset/{clean_name}"
        if os.path.exists(user_dir):
            # Check if name file exists in the user directory
            name_file = f"{user_dir}/{clean_name}.txt"
            if os.path.exists(name_file):
                try:
                    with open(name_file, 'r') as f:
                        existing_name = f.read().strip()
                        if existing_name.lower() == user_name.lower():
                            return clean_name  # Return clean name as identifier
                except:
                    pass
        
        return None
    
    def save_user_name(self, user_id, name):
        """Save user name to file"""
        try:
            # Clean the user name for filename (remove special characters)
            clean_name = self.get_clean_name(name)
            
            # Create user directory if it doesn't exist
            user_dir = f"dataset/{clean_name}"
            os.makedirs(user_dir, exist_ok=True)
            
            name_file = f"{user_dir}/{clean_name}.txt"
            with open(name_file, 'w') as f:
                f.write(name)
            print(f"Saved user name '{name}' to {name_file}")
        except Exception as e:
            print(f"Error saving user name: {e}")
    
    def show_capture_instructions(self):
        """Show optimized capture instructions"""
        instructions = (
            "Face Capture Instructions:\n\n"
            "1. Look directly at the camera\n"
            "2. Turn your head left and right\n"
            "3. Tilt your head up and down\n"
            "4. Make small movements for different angles\n\n"
            f"System will capture {self.max_captures} images automatically.\n"
            "Stay in frame and follow the instructions!"
        )
        messagebox.showinfo("Capture Instructions", instructions)
    
    def stop_capture(self):
        """Stop face capture and start training"""
        self.is_capturing = False
        self.capture_button.config(text="Start Training", bg='#27ae60', state=tk.NORMAL)
        print("Status: Capture complete. Starting training...")
        
        # Keep video paused during training phase
        # (will be resumed when training completes)
        
        # Start automatic training
        self.start_auto_training()
    
    def start_auto_training(self):
        """Start automatic training after capture"""
        if self.is_training:
            return
        
        self.is_training = True
        print("Status: Training model...")
        
        # Start training thread
        training_thread = threading.Thread(target=self.auto_train_thread, daemon=True)
        training_thread.start()
    
    def auto_train_thread(self):
        """Optimized training thread"""
        try:
            image_paths = self.get_training_images()
            if not image_paths:
                self.root.after(0, self.training_failed, "No training images found")
                self.video_paused = False
                return
            
            print(f"Training with {len(image_paths)} images")
            
            # Extract embeddings
            embeddings_extracted = 0
            for image_path in image_paths:
                try:
                    embedding_data = self.process_training_image(image_path)
                    if embedding_data:
                        user_name, embedding = embedding_data
                        if user_name not in self.face_embeddings:
                            self.face_embeddings[user_name] = []
                        self.face_embeddings[user_name].append(embedding)
                        embeddings_extracted += 1
                        
                        # Update progress
                        progress = (embeddings_extracted / len(image_paths)) * 100
                        self.root.after(0, self.update_training_progress, progress)
                        
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    continue
            
            if embeddings_extracted == 0:
                self.root.after(0, self.training_failed, "No valid embeddings extracted")
                self.video_paused = False
                return
            
            # Save embeddings
            self.save_face_embeddings()
            
            # Complete training
            self.root.after(0, self.training_complete, embeddings_extracted)
            
        except Exception as e:
            self.root.after(0, self.training_failed, f"Training error: {e}")


        self.video_paused = False
    def get_training_images(self):
        """Get list of training images"""
        image_paths = []
        if not os.path.exists('dataset'):
            return image_paths
        
        # Look for all user directories
        for dirname in os.listdir('dataset'):
            dir_path = os.path.join('dataset', dirname)
            if os.path.isdir(dir_path):
                # Get all .jpg files in the user directory
                for filename in os.listdir(dir_path):
                    if filename.endswith('.jpg'):
                        image_paths.append(os.path.join(dir_path, filename))
        
        return image_paths
    
    def process_training_image(self, image_path):
        """Process a single training image"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Get user info from path structure
            # Path format: dataset/clean_name/clean_name_number.jpg
            path_parts = image_path.split(os.sep)
            if len(path_parts) >= 3:
                user_dir = path_parts[-2]  # Get the user directory name
                
                # Try to find the corresponding .txt file with the actual name
                txt_file = os.path.join(os.path.dirname(image_path), f"{user_dir}.txt")
                if os.path.exists(txt_file):
                    with open(txt_file, 'r') as f:
                        user_name = f.read().strip()
                else:
                    # Fallback to directory name if no txt file found
                    user_name = user_dir.replace('_', ' ')
            else:
                # Fallback for unexpected path format
                filename = os.path.basename(image_path)
                user_name = filename[:-4].replace('_', ' ')
            
            # Extract embedding
            embedding = self.get_face_embedding_optimized(img)
            
            return (user_name, embedding) if embedding is not None else None
            
        except Exception as e:
            print(f"Error processing training image {image_path}: {e}")
            return None
    
    def update_training_progress(self, progress):
        """Update training progress"""
        print(f"Status: Training... {progress:.1f}%")
    
    def training_complete(self, num_embeddings):
        """Training completed successfully"""
        self.is_training = False
        self.progress_frame.place_forget()  # Hide progress bar
        print(f"Status: Training complete. {num_embeddings} embeddings")
        self.update_names_list({})
        self.refresh_model()
        
        # Resume video processing
        self.video_paused = False
        print("Video feed resumed")
        
        # Add new user to attendance database
        if hasattr(self, 'is_new_user') and self.is_new_user and self.attendance_db:
            try:
                # Check if employee already exists in database
                if self.is_employee_in_database(self.current_user_name):
                    print(f"⚠️  Employee '{self.current_user_name}' already exists in database")
                    messagebox.showinfo("Training Complete", 
                                      f"Successfully trained '{self.current_user_name}'!\n\n"
                                      f"Embeddings: {num_embeddings}\n"
                                      f"Note: Employee already exists in database")
                else:
                    # Add new employee to database
                    success = self.attendance_db.add_employee(
                        name=self.current_user_name,
                        employee_id=None,  # Auto-generated or can be customized
                        department="Face Recognition",  # Default department
                        position="Employee"  # Default position
                    )
                    
                    if success:
                        print(f"✅ Added '{self.current_user_name}' to attendance database")
                        messagebox.showinfo("Training Complete", 
                                          f"Successfully trained and registered '{self.current_user_name}' as a new employee!\n\n"
                                          f"Embeddings: {num_embeddings}")
                    else:
                        print(f"❌ Failed to add '{self.current_user_name}' to database")
                        messagebox.showinfo("Training Complete", 
                                          f"Successfully trained '{self.current_user_name}'!\n\n"
                                          f"Embeddings: {num_embeddings}\n"
                                          f"Note: Could not add to database")
                    
            except Exception as e:
                print(f"❌ Error adding user to database: {e}")
                messagebox.showinfo("Training Complete", 
                                  f"Successfully trained '{self.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}\n"
                                  f"Note: Could not add to database - {e}")
        else:
            # Existing user or no database
            if hasattr(self, 'is_new_user') and not self.is_new_user:
                print(f"🔄 Retrained existing user '{self.current_user_name}'")
                messagebox.showinfo("Training Complete", 
                                  f"Successfully retrained '{self.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}")
            else:
                messagebox.showinfo("Training Complete", 
                                  f"Successfully trained '{self.current_user_name}'!\n\n"
                                  f"Embeddings: {num_embeddings}")
        
        # Reset the new user flag
        self.is_new_user = False
    
    def training_failed(self, error_message):
        """Training failed"""
        self.is_training = False
        self.progress_frame.place_forget()  # Hide progress bar
        print("Status: Training failed")
        
        # Resume video processing
        self.video_paused = False
        print("Video feed resumed")
        
        # Reset the new user flag
        self.is_new_user = False
        
        messagebox.showerror("Training Error", error_message)
    
    def update_names_list(self, user_names):
        """Update names list efficiently"""
        try:
            names_set = set()
            if os.path.exists('dataset'):
                # Look for all user directories
                for dirname in os.listdir('dataset'):
                    dir_path = os.path.join('dataset', dirname)
                    if os.path.isdir(dir_path):
                        # Look for .txt file in each user directory
                        txt_file = os.path.join(dir_path, f"{dirname}.txt")
                        if os.path.exists(txt_file):
                            try:
                                with open(txt_file, 'r') as f:
                                    name = f.read().strip()
                                    if name:  # Only add non-empty names
                                        names_set.add(name)
                            except:
                                continue
            
            # Convert to sorted list
            if names_set:
                self.names = ['None'] + sorted(list(names_set))
            else:
                self.names = ['None']
            
            print(f"Updated names list: {len(self.names)} names")
            
        except Exception as e:
            print(f"Error updating names list: {e}")
    
    def refresh_model(self):
        """Refresh the face recognition model"""
        try:
            self.load_face_embeddings()
            self.update_names_list({})
            
            # Clear embedding cache to force fresh calculations
            self.embedding_cache.clear()
            
            print("Status: Optimized model refreshed")
            print("Face recognition model refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh model: {e}")
    
    def load_face_embeddings(self):
        """Load face embeddings efficiently"""
        try:
            embeddings_file = 'trainer/face_embeddings.pkl'
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'rb') as f:
                    self.face_embeddings = pickle.load(f)
                print(f"Loaded {len(self.face_embeddings)} face embeddings")
            else:
                self.face_embeddings = {}
                print("No face embeddings found")
        except Exception as e:
            print(f"Error loading face embeddings: {e}")
            self.face_embeddings = {}
    
    def save_face_embeddings(self):
        """Save face embeddings efficiently"""
        try:
            os.makedirs('trainer', exist_ok=True)
            with open('trainer/face_embeddings.pkl', 'wb') as f:
                pickle.dump(self.face_embeddings, f)
            print(f"Saved {len(self.face_embeddings)} face embeddings")
        except Exception as e:
            print(f"Error saving face embeddings: {e}")
    

    
    def show_attendance_summary(self):
        """Show attendance summary"""
        if self.attendance_db is None:
            messagebox.showwarning("Warning", "Attendance database not available")
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
            
            messagebox.showinfo("Attendance Summary", summary_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get attendance summary: {e}")
    
    def manual_check_in(self):
        """Manual check-in dialog"""
        if self.attendance_db is None:
            messagebox.showwarning("Warning", "Attendance database not available")
            return
        
        name = simpledialog.askstring("Manual Check-in", "Enter employee name:")
        if name and name.strip():
            name = name.strip()
            try:
                if self.attendance_db.check_in(name):
                    self.update_last_checkin_display(name)
                    messagebox.showinfo("Success", f"{name} checked in successfully!")
                else:
                    messagebox.showwarning("Warning", f"{name} already checked in today")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to check in {name}: {e}")
    
    def cleanup_and_exit(self):
        """Clean up resources and exit"""
        if self.camera is not None:
            self.camera.release()
        if self.attendance_db is not None:
            self.attendance_db.close()
        cv2.destroyAllWindows()
        self.root.destroy()
    
    def update_time_display(self):
        """Update the current time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.time_label.config(text=current_time)
        # Update every second
        self.root.after(1000, self.update_time_display)
    
    def update_last_checkin_display(self, name):
        """Update the check-in history in the textbox"""
        from datetime import datetime
        self.last_checkin_name = name
        self.last_checkin_time = datetime.now().strftime("%H:%M:%S")
        
        # Enable text editing
        self.checkin_textbox.config(state=tk.NORMAL)
        
        # Clear the initial message on first check-in
        if not self.has_checkins_today:
            self.checkin_textbox.delete(1.0, tk.END)
            self.has_checkins_today = True
        
        # Add new check-in entry with timestamp and name
        entry = f"✅ {name} - {self.last_checkin_time}\n"
        self.checkin_textbox.insert(tk.END, entry)
        
        # Auto-scroll to the bottom to show the latest entry
        self.checkin_textbox.see(tk.END)
        
        # Disable text editing to prevent user modification
        self.checkin_textbox.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = OptimizedFaceRecognitionAttendanceUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.cleanup_and_exit)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 