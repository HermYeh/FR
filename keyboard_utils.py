#!/usr/bin/env python3
"""
Keyboard Utilities for Face Recognition System
Handles onboard keyboard positioning and always-on-top functionality
"""

import subprocess
import time
import os

def install_wmctrl():
    """Install wmctrl if not available"""
    try:
        # Check if wmctrl is installed
        subprocess.run(['wmctrl', '-v'], capture_output=True, check=True)
        print("wmctrl is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("wmctrl not found, attempting to install...")
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wmctrl'], check=True)
            print("wmctrl installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install wmctrl: {e}")
            return False

def launch_onboard_always_on_top():
    """Launch onboard keyboard with always-on-top functionality"""
    try:
        # First, kill any existing onboard processes
        subprocess.run(['pkill', 'onboard'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        
        # Launch onboard with always-on-top
        subprocess.Popen(['onboard', '--always-on-top'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Onboard launched with always-on-top")
        
        # Give it time to start
        time.sleep(1)
        
        # Use wmctrl to ensure it stays on top
        try:
            subprocess.run(['wmctrl', '-r', 'onboard', '-b', 'add,above'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Onboard set to always on top via wmctrl")
        except Exception as e:
            print(f"Could not set onboard to always on top: {e}")
        
        return True
        
    except Exception as e:
        print(f"Failed to launch onboard: {e}")
        return False

def ensure_onboard_position():
    """Ensure onboard is positioned correctly and always on top"""
    try:
        # Try multiple methods to ensure onboard stays on top
        
        # Method 1: Use wmctrl to set always on top
        subprocess.run(['wmctrl', '-r', 'onboard', '-b', 'add,above'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Method 2: Use wmctrl to set window type to dock (stays on top)
        subprocess.run(['wmctrl', '-r', 'onboard', '-b', 'add,dock'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Method 3: Use xprop to set window type
        subprocess.run(['xprop', '-id', '$(xdotool search --name onboard)', 
                       '-f', '_NET_WM_WINDOW_TYPE', '32a', 
                       '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DOCK'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("Onboard positioning ensured")
        return True
        
    except Exception as e:
        print(f"Could not ensure onboard position: {e}")
        return False

def get_alternative_keyboards():
    """Get list of available alternative keyboards"""
    alternatives = []
    
    # Check for florence
    try:
        subprocess.run(['florence', '--version'], capture_output=True, check=True)
        alternatives.append('florence')
    except:
        pass
    
    # Check for xvkbd
    try:
        subprocess.run(['xvkbd', '-version'], capture_output=True, check=True)
        alternatives.append('xvkbd')
    except:
        pass
    
    # Check for matchbox-keyboard
    try:
        subprocess.run(['matchbox-keyboard', '--version'], capture_output=True, check=True)
        alternatives.append('matchbox-keyboard')
    except:
        pass
    
    return alternatives

def launch_alternative_keyboard(keyboard_name):
    """Launch an alternative keyboard with always-on-top"""
    try:
        if keyboard_name == 'florence':
            subprocess.Popen(['florence', '--always-on-top'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif keyboard_name == 'xvkbd':
            subprocess.Popen(['xvkbd'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif keyboard_name == 'matchbox-keyboard':
            subprocess.Popen(['matchbox-keyboard'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"{keyboard_name} launched successfully")
        return True
        
    except Exception as e:
        print(f"Failed to launch {keyboard_name}: {e}")
        return False

if __name__ == "__main__":
    # Test the keyboard utilities
    print("Testing keyboard utilities...")
    
    # Install wmctrl if needed
    if install_wmctrl():
        print("wmctrl is available")
    else:
        print("wmctrl not available, some features may not work")
    
    # Check for alternative keyboards
    alternatives = get_alternative_keyboards()
    print(f"Available alternative keyboards: {alternatives}")
    
    # Test onboard launch
    if launch_onboard_always_on_top():
        print("Onboard launched successfully")
        time.sleep(2)
        ensure_onboard_position()
    else:
        print("Failed to launch onboard") 