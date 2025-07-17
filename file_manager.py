import os
import shutil
from ui_dialogs import CustomDialog

class FileManager:
    """Handles file operations and data management"""
    
    def __init__(self):
        pass
    
    def create_directories(self):
        """Create necessary directories"""
        for directory in ['dataset', 'trainer']:
            os.makedirs(directory, exist_ok=True)
    
    def reset_system(self, root, face_processor, attendance_manager, training_manager):
        """Reset system settings"""
        result = CustomDialog.ask_yes_no(root, "Reset System", 
                                   "Are you sure you want to reset the system?\n\n"
                                   "This will:\n"
                                   "• Delete all face recognition data\n"
                                   "• Delete all training images\n"
                                   "• Delete all check-in photos\n"
                                   "• Delete all trainer files\n"
                                   "• Delete attendance database\n"
                                   "• Reload the system\n\n"
                                   "This action cannot be undone.")
        
        if result:
            try:
                # Delete contents of folders
                folders_to_clear = ['CheckinPhoto', 'dataset', 'trainer']
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
        """Show camera settings dialog"""
        settings_text = """Camera Settings:

• Resolution: 640x480 (optimized for performance)
• Frame Rate: 10 FPS
• Auto Exposure: Enabled
• Buffer Size: 1

To modify camera settings, edit the start_camera_optimized() method."""
        
        CustomDialog.show_info(root, "Camera Settings", settings_text)
    
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