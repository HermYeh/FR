#!/usr/bin/env python3
"""
Simple test script to verify fullscreen functionality
"""

import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

def test_fullscreen():
    root = tk.Tk()
    
    # Fullscreen setup
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.configure(bg='black')
    
    # Force window to front
    root.lift()
    root.focus_force()
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    print(f"Screen dimensions: {screen_width}x{screen_height}")
    
    # Create canvas
    canvas = tk.Canvas(root, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.configure(width=screen_width, height=screen_height)
    
    # Create a test image (red rectangle)
    test_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    test_image[:, :] = [0, 0, 255]  # Red background
    
    # Convert to PIL and display
    test_pil = Image.fromarray(test_image)
    test_tk = ImageTk.PhotoImage(test_pil)
    
    canvas.create_image(0, 0, anchor='nw', image=test_tk)
    canvas.image = test_tk
    
    # Add text
    text = canvas.create_text(screen_width//2, screen_height//2, 
                             text="FULLSCREEN TEST\nPress ESC to exit", 
                             fill='white', font=('Arial', 24, 'bold'))
    
    # Bind escape key
    root.bind('<Escape>', lambda e: root.destroy())
    
    print("Fullscreen test window should be visible")
    print("Press ESC to exit")
    
    root.mainloop()

if __name__ == "__main__":
    test_fullscreen() 