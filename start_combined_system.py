'''
Combined Face Recognition and Attendance System Startup
Runs both the face recognition UI and web server
'''

import subprocess
import threading
import time
import sys
import os
from datetime import datetime

def run_face_recognition_ui():
    """Run the face recognition UI"""
    print("Starting Face Recognition UI...")
    try:
        subprocess.run([sys.executable, "face_recognition_attendance_ui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Face Recognition UI error: {e}")
    except KeyboardInterrupt:
        print("Face Recognition UI stopped")

def run_web_server():
    """Run the web server"""
    print("Starting Web Server...")
    try:
        subprocess.run([sys.executable, "attendance_web_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Web Server error: {e}")
    except KeyboardInterrupt:
        print("Web Server stopped")

def main():
    """Main function to start both systems"""
    print("=" * 60)
    print("    FACE RECOGNITION ATTENDANCE SYSTEM")
    print("=" * 60)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This will start:")
    print("1. Face Recognition UI (Full screen)")
    print("2. Web Server (Port 5000)")
    print()
    print("Web interface will be available at:")
    print("- Local: http://localhost:5000")
    print("- Network: http://[YOUR_IP]:5000")
    print()
    print("Press Ctrl+C to stop both systems")
    print("=" * 60)
    print()
    
    # Check if required files exist
    required_files = [
        "face_recognition_attendance_ui.py",
        "attendance_web_server.py",
        "attendance_database.py",
        "haarcascade_frontalface_default.xml"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Error: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print()
        print("Please ensure all files are in the current directory.")
        return
    
    print("✅ All required files found")
    print()
    
    # Start both systems in separate threads
    ui_thread = threading.Thread(target=run_face_recognition_ui, daemon=True)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    
    try:
        # Start web server first (it takes a moment to start)
        print("🚀 Starting Web Server...")
        web_thread.start()
        
        # Give web server time to start
        time.sleep(3)
        
        # Start face recognition UI
        print("🚀 Starting Face Recognition UI...")
        ui_thread.start()
        
        print()
        print("✅ Both systems are now running!")
        print()
        print("Face Recognition UI: Full screen interface")
        print("Web Server: http://localhost:5000")
        print()
        print("Press Ctrl+C to stop both systems")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print()
        print("🛑 Stopping both systems...")
        print("Please wait for graceful shutdown...")
        
        # Give time for graceful shutdown
        time.sleep(2)
        
        print("✅ Systems stopped")
        print("Goodbye!")

if __name__ == "__main__":
    main() 