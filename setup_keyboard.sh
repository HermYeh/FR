#!/bin/bash

echo "Setting up keyboard utilities for face recognition system..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install wmctrl for window management
echo "Installing wmctrl..."
sudo apt-get install -y wmctrl

# Install onboard keyboard if not already installed
echo "Installing onboard keyboard..."
sudo apt-get install -y onboard

# Install alternative keyboards
echo "Installing alternative keyboards..."
sudo apt-get install -y florence xvkbd

# Install xdotool for additional window management
echo "Installing xdotool..."
sudo apt-get install -y xdotool

# Test keyboard utilities
echo "Testing keyboard utilities..."
python3 keyboard_utils.py

echo "Keyboard setup complete!"
echo ""
echo "To test the keyboard functionality:"
echo "1. Run: python3 face_recognition_ui.py"
echo "2. Click 'Start Training'"
echo "3. The onboard keyboard should appear and stay on top" 