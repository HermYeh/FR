#!/usr/bin/env python3
"""
Camera Diagnostics Tool for Raspberry Pi
Helps identify and troubleshoot camera issues
"""

import cv2
import os
import subprocess
import sys
import time

def check_camera_devices():
    """Check available camera devices"""
    print("=== Camera Device Detection ===")
    
    # Check /dev/video* devices
    video_devices = []
    for i in range(10):  # Check video0 through video9
        device_path = f"/dev/video{i}"
        if os.path.exists(device_path):
            video_devices.append(i)
            print(f"✅ Found video device: {device_path}")
    
    if not video_devices:
        print("❌ No video devices found in /dev/")
        return []
    
    return video_devices

def test_opencv_camera(device_index):
    """Test OpenCV camera access"""
    print(f"\n=== Testing OpenCV Camera {device_index} ===")
    
    try:
        # Create camera object
        cap = cv2.VideoCapture(device_index)
        
        if not cap.isOpened():
            print(f"❌ Could not open camera {device_index}")
            return False
        
        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Get actual properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"📹 Camera {device_index} properties:")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        
        # Try to read a frame
        print("📸 Testing frame capture...")
        for i in range(5):  # Try 5 times
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Frame {i+1}/5: Success ({frame.shape})")
                break
            else:
                print(f"❌ Frame {i+1}/5: Failed")
                time.sleep(0.1)
        else:
            print("❌ All frame captures failed")
            cap.release()
            return False
        
        cap.release()
        print(f"✅ Camera {device_index} is working properly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing camera {device_index}: {e}")
        return False

def check_raspberry_pi_camera():
    """Check Raspberry Pi specific camera"""
    print("\n=== Raspberry Pi Camera Check ===")
    
    try:
        # Check if raspistill is available
        result = subprocess.run(['which', 'raspistill'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ raspistill not found - Pi camera tools not installed")
            return False
        
        # Try to take a test photo
        print("📸 Testing Pi camera with raspistill...")
        result = subprocess.run(['raspistill', '-t', '1', '-o', '/tmp/test_camera.jpg'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Pi camera is working")
            # Clean up test file
            if os.path.exists('/tmp/test_camera.jpg'):
                os.remove('/tmp/test_camera.jpg')
            return True
        else:
            print(f"❌ Pi camera failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Pi camera test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Pi camera: {e}")
        return False

def check_v4l2_info():
    """Check V4L2 device information"""
    print("\n=== V4L2 Device Information ===")
    
    try:
        # Check if v4l2-ctl is available
        result = subprocess.run(['which', 'v4l2-ctl'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ v4l2-ctl not found - install v4l-utils package")
            return
        
        # List V4L2 devices
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("📹 V4L2 devices:")
            print(result.stdout)
        else:
            print("❌ Could not list V4L2 devices")
            
    except Exception as e:
        print(f"❌ Error checking V4L2 info: {e}")

def suggest_fixes():
    """Suggest common fixes for camera issues"""
    print("\n=== Common Fixes ===")
    print("🔧 If you're having camera issues, try these:")
    print("1. Enable camera interface:")
    print("   sudo raspi-config → Interface Options → Camera → Enable")
    print()
    print("2. Add user to video group:")
    print("   sudo usermod -a -G video $USER")
    print("   (then logout and login again)")
    print()
    print("3. Install V4L2 utilities:")
    print("   sudo apt update")
    print("   sudo apt install v4l-utils")
    print()
    print("4. Check camera cable connection")
    print("5. Reboot the system:")
    print("   sudo reboot")
    print()
    print("6. If using USB camera, try different USB ports")
    print("7. Check power supply - insufficient power can cause camera issues")

def main():
    """Main diagnostics function"""
    print("🔍 Camera Diagnostics Tool")
    print("=" * 50)
    
    # Check OpenCV version
    print(f"OpenCV version: {cv2.__version__}")
    
    # Check available devices
    devices = check_camera_devices()
    
    # Test each device with OpenCV
    working_cameras = []
    for device in devices:
        if test_opencv_camera(device):
            working_cameras.append(device)
    
    # Check Pi camera
    pi_camera_works = check_raspberry_pi_camera()
    
    # Check V4L2 info
    check_v4l2_info()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if working_cameras:
        print(f"✅ Working cameras: {working_cameras}")
        print(f"💡 Use camera index {working_cameras[0]} in your application")
    else:
        print("❌ No working cameras found")
    
    if pi_camera_works:
        print("✅ Raspberry Pi camera is working")
    
    # Suggest fixes
    suggest_fixes()

if __name__ == "__main__":
    main() 