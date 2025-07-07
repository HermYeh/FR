#!/usr/bin/env python3
"""
Test script for simple keyboard integration
"""

import tkinter as tk
from tkinter import messagebox
from simple_keyboard import show_simple_keyboard

def test_keyboard():
    """Test the simple keyboard"""
    root = tk.Tk()
    root.title("Keyboard Integration Test")
    root.geometry("500x300")
    root.configure(bg='#2c3e50')
    
    # Create test entry
    entry = tk.Entry(root, font=('Arial', 16), width=30)
    entry.pack(pady=30)
    
    # Test button
    def show_keyboard_test():
        result = show_simple_keyboard(root, entry)
        print(f"Keyboard result: {result}")
        messagebox.showinfo("Result", f"Entered text: {result}")
    
    btn = tk.Button(root, text="Show Simple Keyboard", 
                   command=show_keyboard_test,
                   font=('Arial', 12, 'bold'),
                   bg='#27ae60', fg='white',
                   width=20, height=2)
    btn.pack(pady=20)
    
    # Instructions
    instruction = tk.Label(root, 
                          text="Click the button to test the simple keyboard\nPress ESC to close the keyboard",
                          font=('Arial', 10),
                          fg='white', bg='#2c3e50')
    instruction.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_keyboard() 