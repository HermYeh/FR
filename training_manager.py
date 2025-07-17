import cv2
import os
import threading
import time
from datetime import datetime
from ui_dialogs import CustomDialog
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
        
    def get_user_name_input(self, root, screen_width, screen_height):
        dialog = tk.Toplevel(root)
        dialog.grab_set()
        dialog.transient(root)
        dialog.title("Face Recognition Training - Name Input")
        dialog.configure(bg='#2c3e50')
        
        # Center on screen with optimized size
        dialog_width, dialog_height = 700, 600
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
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
        def create_key_button(parent, text, command, style='normal',width=4):
            """Create optimized keyboard button"""
            colors = {
                'normal': {'bg': '#34495e', 'fg': 'white', 'active_bg': '#4a6741'},
                'special': {'bg': '#3498db', 'fg': 'white', 'active_bg': '#2980b9'},
                'action': {'bg': '#27ae60', 'fg': 'white', 'active_bg': '#229954'},
                'danger': {'bg': '#e74c3c', 'fg': 'white', 'active_bg': '#c0392b'}
            }
            
            color = colors.get(style, colors['normal'])
            
            btn = tk.Button(parent, text=text, width=width, height=3,
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
        
        confirm_btn = tk.Button(control_frame, text="Confirm", command=confirm,
                               font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                               width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        confirm_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        cancel_btn = tk.Button(control_frame, text="Cancel", command=cancel,
                              font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                              width=12, height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        cancel_btn.pack(side=tk.RIGHT)
        cancel_btn.focus_set()
        
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
                                       row_data['style'],4)
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
        back_btn = create_key_button(special_frame, "⌫", backspace, 'danger',8)
        back_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear
        clear_btn = create_key_button(special_frame, "Clear", clear_text, 'special',8)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Enter
        enter_btn = create_key_button(special_frame, "Enter", confirm, 'action',10)
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
        """Save a photo of the current video feed when employee checks in"""
        try:
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