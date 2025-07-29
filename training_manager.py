import cv2
import os
import threading
import time
from datetime import datetime
import menu_ui
from ui_dialogs import CustomDialog
from menu_ui import MenuManager
from virtual_keyboard import VirtualKeyboard

import tkinter as tk

class TrainingManager:
    """Handles face capture, training, and user management"""
    
    def __init__(self):
        self.is_capturing = False
        self.is_training = False
        self.capture_count = 0
        self.max_captures = 8
        self.current_user_name = ""
        self.is_new_user = False
        self.names = []
        
    def get_user_name_input(self, parent_window, screen_width, screen_height, restore_callback=None):
        # Clear existing content from the parent window
        for widget in parent_window.winfo_children():
            widget.destroy()
        
        # Main container with better padding
        main_frame = tk.Frame(parent_window, bg='#2c3e50')
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
        
        def confirm():
            """Validate and confirm input"""
            name = name_var.get().strip()
            parent_window.destroy()
            if name:
                result['name'] = name
                main_frame.destroy()
            else:
                # Flash entry field for error feedback
                original_bg = name_entry.cget('bg')
                name_entry.config(bg='#ffcccb')
                main_frame.after(200, lambda: name_entry.config(bg=original_bg))
                virtual_keyboard.update_cursor()
        
        def cancel():
            """Cancel input"""
            main_frame.destroy()
            if restore_callback:
                restore_callback()
        
        # Control buttons section
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        confirm_btn = tk.Button(control_frame, text="Confirm", command=confirm,
                               font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                               width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        cancel_btn = tk.Button(control_frame, text="Cancel", command=cancel,
                              font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                              width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        cancel_btn.focus_set()
        
        # Create virtual keyboard with dynamic show/hide
        virtual_keyboard = VirtualKeyboard(main_frame, name_var)
        virtual_keyboard.setup_dynamic_keyboard(name_entry, confirm_callback=confirm)
        
        # Bind cancel to main frame
        main_frame.bind('<Escape>', lambda e: cancel())
        
        # Focus management
        main_frame.focus()
        name_entry.focus()
        
        # Wait for dialog completion
        main_frame.wait_window()
        
        return result['name'] if result['name'] else None
    
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
    
    def show_capture_instructions(self, root):
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
        CustomDialog.show_info(root, "Capture Instructions", instructions)
    
    def capture_face_optimized(self, frame, x, y, w, h):
        face_img = frame[y:y+h, x:x+w]
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
            self.capture_count += 1
            cv2.imwrite(filename, face_img)
            
            return self.capture_count >= self.max_captures
                
        except Exception as e:
            print(f"Capture error: {e}")
            return False
    
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
    
    def auto_train_thread(self, face_processor, callback_success, callback_failed):
        """Optimized training thread"""
        try:
            image_paths = self.get_training_images()
            if not image_paths:
                callback_failed("No training images found")
                return
            
            print(f"Training with {len(image_paths)} images")
            
            # Extract embeddings
            embeddings_extracted = 0
            for image_path in image_paths:
                try:
                    embedding_data = face_processor.process_training_image(image_path)
                    if embedding_data:
                        user_name, embedding = embedding_data
                        if user_name not in face_processor.face_embeddings:
                            face_processor.face_embeddings[user_name] = []
                        face_processor.face_embeddings[user_name].append(embedding)
                        embeddings_extracted += 1
                        
                        # Update progress
                        progress = (embeddings_extracted / len(image_paths)) * 100
                        
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                    continue
            
            if embeddings_extracted == 0:
                callback_failed("No valid embeddings extracted")
                return
            
            # Save embeddings
            face_processor.save_face_embeddings()
            
            # Complete training
            callback_success(embeddings_extracted)
            
        except Exception as e:
            callback_failed(f"Training error: {e}")
    
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
    
    def save_checkin_photo(self, name, frame):
        """Save a photo when employee checks in"""
        try:
            # Create checkout photos directory
            today = datetime.now().strftime("%Y-%m-%d")
            checkin_dir = f"CheckinPhoto/{today}"
            os.makedirs(checkin_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%H-%M-%S")
            clean_name = self.get_clean_name(name)
            filename = f"{checkin_dir}/{clean_name}_{timestamp}.jpg"
            
            # Save the photo
            cv2.imwrite(filename, frame)
            print(f"Saved check-in photo: {filename}")
            
        except Exception as e:
            print(f"Error saving check-in photo: {e}")
    
    def save_checkout_photo(self, name, frame):
        """Save a photo when employee checks out"""
        try:
            # Create checkout photos directory
            today = datetime.now().strftime("%Y-%m-%d")
            checkout_dir = f"CheckoutPhoto/{today}"
            os.makedirs(checkout_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%H-%M-%S")
            clean_name = self.get_clean_name(name)
            filename = f"{checkout_dir}/{clean_name}_{timestamp}.jpg"
            
            # Save the photo
            cv2.imwrite(filename, frame)
            print(f"Saved check-out photo: {filename}")
            
        except Exception as e:
            print(f"Error saving check-out photo: {e}") 