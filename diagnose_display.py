#!/usr/bin/env python3
"""
Display Diagnostic Script
Helps troubleshoot fullscreen and display issues
"""

import os
import tkinter as tk
import subprocess
import sys

def check_environment():
    """Check environment variables and system status"""
    print("=== Environment Check ===")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM', 'Not set')}")
    print(f"Python version: {sys.version}")
    
    # Check if X server is running
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ X server is running")
        else:
            print("✗ X server is not responding")
    except FileNotFoundError:
        print("✗ xset command not found")

def check_screen_info():
    """Check screen information"""
    print("\n=== Screen Information ===")
    try:
        result = subprocess.run(['xrandr'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if '*' in line:  # Current resolution
                    print(f"Current resolution: {line.strip()}")
                    break
        else:
            print("Could not get screen information")
    except FileNotFoundError:
        print("xrandr command not found")

def test_tkinter():
    """Test Tkinter functionality"""
    print("\n=== Tkinter Test ===")
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        print(f"Screen dimensions: {screen_width}x{screen_height}")
        
        # Test fullscreen attributes
        root.attributes('-fullscreen', True)
        print("✓ Fullscreen attribute set successfully")
        
        root.attributes('-topmost', True)
        print("✓ Topmost attribute set successfully")
        
        root.overrideredirect(True)
        print("✓ Window decorations removed successfully")
        
        root.destroy()
        print("✓ Tkinter test completed successfully")
        
    except Exception as e:
        print(f"✗ Tkinter test failed: {e}")

def test_fullscreen_window():
    """Test creating a fullscreen window"""
    print("\n=== Fullscreen Window Test ===")
    try:
        root = tk.Tk()
        
        # Set up fullscreen
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.overrideredirect(True)
        root.configure(bg='red')
        
        # Get dimensions
        width = root.winfo_width()
        height = root.winfo_height()
        
        print(f"Window dimensions: {width}x{height}")
        
        # Create a label
        label = tk.Label(root, text="FULLSCREEN TEST\nPress any key to exit", 
                        bg='red', fg='white', font=('Arial', 24, 'bold'))
        label.pack(expand=True)
        
        # Bind key to exit
        root.bind('<Key>', lambda e: root.destroy())
        
        print("Fullscreen test window should appear (red background)")
        print("Press any key to exit the test")
        
        root.mainloop()
        
    except Exception as e:
        print(f"✗ Fullscreen window test failed: {e}")

def main():
    """Run all diagnostics"""
    print("Face Recognition Display Diagnostic")
    print("=" * 40)
    
    check_environment()
    check_screen_info()
    test_tkinter()
    
    # Ask user if they want to test fullscreen
    response = input("\nDo you want to test fullscreen window? (y/n): ")
    if response.lower() == 'y':
        test_fullscreen_window()
    
    print("\n=== Diagnostic Complete ===")
    print("If all tests pass, your display should work with the face recognition UI")

if __name__ == "__main__":
    main() 