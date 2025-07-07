'''
Face Recognition UI Application
Full Screen Version: Video fills the window, UI overlays on top
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

# Fix Qt platform plugin issues
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_QPA_FONTDIR'] = '/usr/share/fonts'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

# Fix locale issues
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

# Set display backend to avoid Qt issues
os.environ['DISPLAY'] = ':0'
os.environ['QT_QPA_PLATFORM'] = 'xcb'

class FaceRecognitionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # Initialize variables
        self.camera = None
        self.is_capturing = False
        self.is_training = False
        self.recognizer = None
        self.face_cascade = None
        self.names = []
        self.current_user_id = 1
        self.current_user_name = ""
        self.capture_count = 0
        self.max_captures = 30
        
        # Create directories if they don't exist
        self.create_directories()
        
        # Initialize face recognition components
        self.initialize_face_recognition()
        
        # Load existing names from dataset
        self.update_names_list({})
        
        # Create UI
        self.create_ui()
        
        # Start camera
        self.start_camera()
        
        # Start video loop
        self.update_video()
    
    def create_directories(self):
        """Create necessary directories"""
        directories = ['dataset', 'trainer']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created {directory} directory")
    
    def initialize_face_recognition(self):
        """Initialize face recognition components"""
        try:
            # Load frontal face detector
            frontal_cascade_path = "haarcascade_frontalface_default.xml"
            self.frontal_cascade = cv2.CascadeClassifier(frontal_cascade_path)
            
            if self.frontal_cascade.empty():
                messagebox.showerror("Error", "Could not load frontal face detector cascade file.")
                return
            
            # Profile face detection disabled for better performance
            self.profile_cascade = None
            print("Profile face detection disabled")
            
            # Set the main cascade to frontal for backward compatibility
            self.face_cascade = self.frontal_cascade
            
            # Load recognizer if trainer exists
            if os.path.exists('trainer/trainer.yml'):
                try:
                    self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                    self.recognizer.read('trainer/trainer.yml')
                    print("Loaded existing trainer model")
                except AttributeError:
                    messagebox.showwarning("Warning", "OpenCV face recognition module not available. Install opencv-contrib-python")
                except Exception as e:
                    print(f"Error loading trainer: {e}")
            else:
                print("No trainer model found. Will create new one after training.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize face recognition: {e}")
    
    def create_ui(self):
        """Create the user interface"""
        # Get screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Canvas for video
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Overlay UI elements
        # Status
        self.status_label = tk.Label(self.root, text="Status: Ready", 
                                   font=('Arial', 12), fg='white', bg='#34495e', bd=2)
        self.status_label.place(relx=0.01, rely=0.01, anchor='nw')
        
        self.recognition_label = tk.Label(self.root, text="Recognition: No face detected", 
                                        font=('Arial', 10), fg='#ecf0f1', bg='#34495e', bd=2)
        self.recognition_label.place(relx=0.01, rely=0.07, anchor='nw')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, 
                                          variable=self.progress_var,
                                          maximum=30,
                                          length=200)
        self.progress_bar.place(relx=0.01, rely=0.19, anchor='nw')
        
        # Buttons (bottom right)
        self.capture_button = tk.Button(self.root, text="Start Training", 
                                      command=self.start_capture,
                                      font=('Arial', 12, 'bold'),
                                      bg='#27ae60', fg='white',
                                      width=15, height=2,
                                      relief=tk.RAISED, bd=3)
        self.capture_button.place(relx=0.99, rely=0.85, anchor='ne')
    
    def start_camera(self):
        """Start the camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.camera = cv2.VideoCapture(1)
                if not self.camera.isOpened():
                    messagebox.showerror("Error", "Could not open camera")
                    return
            
            self.camera.set(3, self.screen_width)
            self.camera.set(4, self.screen_height)
            print("Camera started successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def update_video(self):
        """Update video frame"""
        if self.camera is None:
            return
            
        minW = 0.1*self.camera.get(3)
        minH = 0.1*self.camera.get(4)
        try:
            ret, frame = self.camera.read()
            if ret:
                # Flip frame vertically
                frame = cv2.flip(frame, -1)
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect frontal faces
                frontal_faces = self.frontal_cascade.detectMultiScale(
                    gray,
                    scaleFactor = 1.2,  # More sensitive - smaller scale factor
                    minNeighbors = 4,    # More sensitive - fewer neighbors required
                    minSize = (int(minW ), int(minH )),  # Detect smaller faces (closer faces)
                    )
                
                # Profile face detection disabled for better performance
                # Only use frontal face detection
                faces = list(frontal_faces)
                
                # Process faces
                for (x, y, w, h) in faces:
                    # Draw rectangle around face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Face recognition
                    if self.recognizer is not None:
                        try:
                            face_roi = gray[y:y+h, x:x+w]
                            id, confidence = self.recognizer.predict(face_roi)
                            
                            if confidence < 100:
                                name = self.names[id] if id < len(self.names) else f"User_{id}"
                                confidence_text = f"{round(100 - confidence)}%"
                            else:
                                name = "Unknown"
                                confidence_text = f"{round(100 - confidence)}%"
                            
                            # Display name and confidence
                            cv2.putText(frame, name, (x+5, y-5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                            cv2.putText(frame, confidence_text, (x+5, y+h-5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 1)
                            
                            # Update recognition label
                            self.recognition_label.config(text=f"Recognition: {name} ({confidence_text})")
                            
                        except Exception as e:
                            print(f"Recognition error: {e}")
                    
                    # Capture face for training
                    if self.is_capturing and self.capture_count < self.max_captures:
                        self.capture_face(gray[y:y+h, x:x+w])
                
                # Dynamically resize to fit window while maintaining aspect ratio
                win_w = self.root.winfo_width()
                win_h = self.root.winfo_height()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                
                # Calculate aspect ratios
                frame_aspect = frame_pil.width / frame_pil.height
                window_aspect = win_w / win_h
                
                # Resize maintaining aspect ratio
                if frame_aspect > window_aspect:
                    # Frame is wider than window - fit to width
                    new_width = win_w
                    new_height = int(win_w / frame_aspect)
                else:
                    # Frame is taller than window - fit to height
                    new_height = win_h
                    new_width = int(win_h * frame_aspect)
                
                frame_pil = frame_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                
                # Center the image on the canvas
                x_offset = (win_w - new_width) // 2
                y_offset = (win_h - new_height) // 2
                
                self.canvas.create_image(x_offset, y_offset, anchor='nw', image=frame_tk)
                self.canvas.image = frame_tk
                
                # Update status
                if len(faces) > 0:
                    self.status_label.config(text=f"Status: {len(faces)} face(s) detected")
                else:
                    self.status_label.config(text="Status: No faces detected")
                    self.recognition_label.config(text="Recognition: No face detected")
            
        except Exception as e:
            print(f"Video update error: {e}")
        
        # Schedule next update
        self.root.after(10, self.update_video)
    
    def capture_face(self, face_img):
        """Capture a face image for training"""
        try:
            # Count existing images for this user to get the next number
            existing_count = 0
            if os.path.exists('dataset'):
                for filename in os.listdir('dataset'):
                    if filename.startswith(f'User.{self.current_user_id}.') and filename.endswith('.jpg'):
                        existing_count += 1
            
            # Save face image with next available number
            next_number = existing_count + self.capture_count + 1
            filename = f"dataset/User.{self.current_user_id}.{next_number}.jpg"
            cv2.imwrite(filename, face_img)
            
            self.capture_count += 1
            self.progress_var.set(self.capture_count)
     
            print(f"Captured face {self.capture_count}/{self.max_captures} for User.{self.current_user_id}.{next_number}")
            
            # Check if capture is complete
            if self.capture_count >= self.max_captures:
                self.stop_capture()
                
        except Exception as e:
            print(f"Capture error: {e}")
    
    def start_capture(self):
        """Start face capture process"""
        if self.is_capturing:
            return
        
        # Show integrated keyboard window
        try:
            from integrated_keyboard import show_integrated_keyboard
            user_name = show_integrated_keyboard(self.root)
        except ImportError:
            # Fallback to simple dialog if integrated keyboard not available
            dialog = tk.Toplevel(self.root)
            dialog.title("Enter User Name")
            dialog.geometry("500x150")
            dialog.configure(bg='#2c3e50')
            
            # Make dialog stay on top
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.focus_set()
            
            # Position dialog at very top of screen
            dialog.update_idletasks()
            screen_width = dialog.winfo_screenwidth()
            x = (screen_width // 2) - (500 // 2)
            y = 10  # Position at very top with minimal margin
            dialog.geometry(f"500x150+{x}+{y}")
            
            # Create dialog content
            title_label = tk.Label(dialog, text="Enter User Name", 
                                  font=('Arial', 16, 'bold'), 
                                  fg='white', bg='#2c3e50')
            title_label.pack(pady=20)
            
            instruction_label = tk.Label(dialog, text="Please enter the name for the new user:", 
                                       font=('Arial', 12), 
                                       fg='#ecf0f1', bg='#2c3e50')
            instruction_label.pack(pady=10)
            
            # Entry field
            name_var = tk.StringVar()
            name_entry = tk.Entry(dialog, textvariable=name_var, 
                                font=('Arial', 14), 
                                width=30, 
                                relief=tk.RAISED, bd=3)
            name_entry.pack(pady=10)
            name_entry.focus()
            
            # Result variable
            result = {'name': None}
            
            def on_confirm():
                name = name_var.get().strip()
                if name:
                    result['name'] = name
                    dialog.destroy()
                else:
                    messagebox.showwarning("Warning", "Please enter a name", parent=dialog)
            
            def on_cancel():
                dialog.destroy()
            
            # Button frame with confirm and cancel buttons
            button_frame = tk.Frame(dialog, bg='#2c3e50')
            button_frame.pack(pady=10)
            
            # Confirm button (always present)
            confirm_button = tk.Button(button_frame, text="Confirm", command=on_confirm,
                                     font=('Arial', 12, 'bold'),
                                     bg='#27ae60', fg='white',
                                     width=10, height=2,
                                     relief=tk.RAISED, bd=3)
            confirm_button.pack(side=tk.LEFT, padx=10)
            
            # Cancel button
            cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel,
                                    font=('Arial', 12, 'bold'),
                                    bg='#e74c3c', fg='white',
                                    width=10, height=2,
                                    relief=tk.RAISED, bd=3)
            cancel_button.pack(side=tk.LEFT, padx=10)
            
            # Bind Enter key to Confirm
            name_entry.bind('<Return>', lambda e: on_confirm())
            
            # Wait for dialog to close
            dialog.wait_window()
            
            # Get result
            user_name = result['name']
        if user_name is None or user_name.strip() == "":
            return
        user_name = user_name.strip()
        
        # Check if user name already exists in dataset
        existing_user_id = None
        existing_ids = set()
        if os.path.exists('dataset'):
            for filename in os.listdir('dataset'):
                if filename.startswith('User.') and filename.endswith('.jpg'):
                    try:
                        user_id = int(filename.split('.')[1])
                        existing_ids.add(user_id)
                        
                        # Check if this user ID has the same name
                        name_file = f"dataset/name_{user_id}.txt"
                        if os.path.exists(name_file):
                            with open(name_file, 'r') as f:
                                existing_name = f.read().strip()
                            if existing_name.lower() == user_name.lower():
                                existing_user_id = user_id
                                break
                    except:
                        continue
        
        if existing_user_id is not None:
            # User with same name exists, extend their dataset
            self.current_user_id = existing_user_id
            self.current_user_name = user_name
            
            # Count existing images for this user
            existing_count = 0
            for filename in os.listdir('dataset'):
                if filename.startswith(f'User.{existing_user_id}.') and filename.endswith('.jpg'):
                    existing_count += 1
            
            print(f"Found existing user '{user_name}' with ID {existing_user_id} and {existing_count} existing images")
            
        else:
            # New user, find next available ID
            next_id = 1
            while next_id in existing_ids:
                next_id += 1
            
            self.current_user_id = next_id
            self.current_user_name = user_name
            
            # Save user name to file for later retrieval
            name_file = f"dataset/name_{next_id}.txt"
            try:
                with open(name_file, 'w') as f:
                    f.write(user_name)
                print(f"Saved user name '{user_name}' to {name_file}")
            except Exception as e:
                print(f"Error saving user name: {e}")
        
        # Add name to names list if not already present
        if user_name not in self.names:
            self.names.append(user_name)
        
        self.capture_count = 0
        self.is_capturing = True
        
        # Show capture instructions
        self.show_capture_instructions()
        
        # Update UI
        self.capture_button.config(text="Capturing...", bg='#e74c3c', state=tk.DISABLED)
        self.status_label.config(text=f"Status: Capturing faces for {user_name}...")
        self.progress_var.set(0)
        
        print(f"Started capturing faces for {user_name} (ID: {self.current_user_id})")
    
    def show_capture_instructions(self):
        """Show instructions for face capture"""
        instructions = (
            "Face Capture Instructions:\n\n"
            "1. Look directly at the camera (frontal view)\n"
            "2. Turn your head to the LEFT and hold for a few seconds\n"
            "3. Turn your head to the RIGHT and hold for a few seconds\n"
            "4. Tilt your head UP slightly\n"
            "5. Tilt your head DOWN slightly\n"
            "6. Make small movements to capture different angles\n\n"
            "The system will automatically capture 30 images.\n"
            "Stay in frame and follow the instructions!"
        )
        messagebox.showinfo("Capture Instructions", instructions)
    
    def stop_capture(self):
        """Stop face capture process"""
        self.is_capturing = False
        self.capture_button.config(text="Start Training", bg='#27ae60', state=tk.NORMAL)
        self.status_label.config(text="Status: Capture complete. Starting automatic training...")
        
        # Automatically start training
        self.auto_train_after_capture()
    
    def auto_train_after_capture(self):
        """Automatically train and refresh model after capture"""
        if self.is_training:
            return
        
        self.is_training = True
        self.status_label.config(text="Status: Training model...")
        
        # Run training in separate thread
        training_thread = threading.Thread(target=self.auto_train_thread)
        training_thread.daemon = True
        training_thread.start()
    
    def auto_train_thread(self):
        """Automatic training thread after capture"""
        try:
            # Get images and labels
            path = 'dataset'
            image_paths = [os.path.join(path, f) for f in os.listdir(path)]
            face_samples = []
            ids = []
            user_names = {}  # Dictionary to map IDs to names
            
            print(f"Found {len(image_paths)} images for training")
            
            for image_path in image_paths:
                try:
                    # Load image
                    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        continue
                    
                    # Get user ID from filename
                    filename = os.path.basename(image_path)
                    user_id = int(filename.split('.')[1])
                    
                    face_samples.append(img)
                    ids.append(user_id)
                    
                    # Store user ID for later name mapping
                    if user_id not in user_names:
                        user_names[user_id] = f"User_{user_id}"
                    
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    continue
            
            if len(face_samples) == 0:
                self.root.after(0, lambda: messagebox.showerror("Training Error", "No valid face images found for training"))
                self.root.after(0, self.auto_training_failed)
                return
            
            # Create and train recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(face_samples, np.array(ids))
            
            # Save model
            recognizer.write('trainer/trainer.yml')
            
            # Update main thread with user names
            self.root.after(0, self.auto_training_complete, len(face_samples), len(set(ids)), user_names)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Training Error", f"Failed to train model: {e}"))
            self.root.after(0, self.auto_training_failed)
    
    def auto_training_complete(self, num_faces, num_users, user_names):
        """Called when automatic training is complete"""
        self.is_training = False
        self.status_label.config(text=f"Status: Auto-training complete. {num_faces} faces from {num_users} users")
        
        # Update names list dynamically
        self.update_names_list(user_names)
        
        # Refresh recognizer
        self.refresh_model()
    
    def auto_training_failed(self):
        """Called when automatic training fails"""
        self.is_training = False
        self.status_label.config(text="Status: Auto-training failed")
    
    def update_names_list(self, user_names):
        """Update the names list with user names from training"""
        try:
            # Build names list from dataset
            names_dict = {}
            if os.path.exists('dataset'):
                for filename in os.listdir('dataset'):
                    if filename.startswith('User.') and filename.endswith('.jpg'):
                        try:
                            user_id = int(filename.split('.')[1])
                            # Try to find a name file or use default
                            name_file = f"dataset/name_{user_id}.txt"
                            if os.path.exists(name_file):
                                with open(name_file, 'r') as f:
                                    name = f.read().strip()
                            else:
                                name = f"User_{user_id}"
                            names_dict[user_id] = name
                        except:
                            continue
            
            # Update self.names list
            max_id = max(names_dict.keys()) if names_dict else 0
            self.names = ['None'] + [names_dict.get(i, f"User_{i}") for i in range(1, max_id + 1)]
            
            print(f"Updated names list: {self.names}")
            
        except Exception as e:
            print(f"Error updating names list: {e}")
    
    def refresh_model(self):
        """Refresh the face recognition model"""
        try:
            if os.path.exists('trainer/trainer.yml'):
                self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                self.recognizer.read('trainer/trainer.yml')
                
                # Update names list when refreshing model
                self.update_names_list({})
                
                self.status_label.config(text="Status: Model refreshed")
                print("Model refreshed successfully")
            else:
                self.status_label.config(text="Status: No model to refresh")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh model: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.camera is not None:
            self.camera.release()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FaceRecognitionUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 