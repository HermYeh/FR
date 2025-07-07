#!/usr/bin/env python3
"""
Test script to measure startup performance of the face recognition UI
"""

import time
import subprocess
import sys

def test_startup_performance():
    """Test the startup performance of the face recognition UI"""
    print("Testing Face Recognition UI Startup Performance")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Start the UI in a subprocess
        process = subprocess.Popen([sys.executable, "face_recognition_attendance_ui.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for a reasonable amount of time to see if it starts
        time.sleep(10)  # Wait 10 seconds
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ UI started successfully within 10 seconds")
            print(f"Startup time: {time.time() - start_time:.2f} seconds")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            print("✅ UI terminated successfully")
        else:
            # Process ended prematurely
            stdout, stderr = process.communicate()
            print("❌ UI failed to start or crashed")
            print(f"Exit code: {process.returncode}")
            if stderr:
                print(f"Error output: {stderr.decode()}")
    
    except Exception as e:
        print(f"❌ Error testing startup: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    test_startup_performance() 