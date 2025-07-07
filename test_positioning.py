#!/usr/bin/env python3
"""
Test script for exact positioning: input dialog at very top, keyboard at very bottom
"""

import tkinter as tk
from tkinter import messagebox
from simple_keyboard import show_simple_keyboard

def test_exact_positioning():
    """Test the exact positioning with input at very top and keyboard at very bottom"""
    root = tk.Tk()
    root.title("Exact Positioning Test")
    root.geometry("800x600")
    root.configure(bg='#2c3e50')
    
    # Create a dialog at the very top
    dialog = tk.Toplevel(root)
    dialog.title("Enter Name")
    dialog.geometry("400x150")
    dialog.configure(bg='#2c3e50')
    
    # Position dialog at very top
    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    x = (screen_width // 2) - (400 // 2)
    y = 10  # Position at very top with minimal margin
    dialog.geometry(f"400x150+{x}+{y}")
    
    # Make dialog stay on top
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    
    # Create dialog content
    instruction_label = tk.Label(dialog, text="Please enter the name for the new user:", 
                               font=('Arial', 12), 
                               fg='#ecf0f1', bg='#2c3e50')
    instruction_label.pack(pady=5)
    
    # Entry field
    name_var = tk.StringVar()
    name_entry = tk.Entry(dialog, textvariable=name_var, 
                        font=('Arial', 14), 
                        width=25, 
                        relief=tk.RAISED, bd=3)
    name_entry.pack(pady=10)
    name_entry.focus()
    
    def on_confirm():
        name = name_var.get().strip()
        if name:
            messagebox.showinfo("Success", f"Name entered: {name}")
            dialog.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter a name")
    
    def on_cancel():
        dialog.destroy()
    
    # Button frame
    button_frame = tk.Frame(dialog, bg='#2c3e50')
    button_frame.pack(pady=10)
    
    # Confirm button
    confirm_button = tk.Button(button_frame, text="Confirm", command=on_confirm,
                             font=('Arial', 12, 'bold'),
                             bg='#27ae60', fg='white',
                             width=8, height=3,
                             relief=tk.RAISED, bd=3)
    confirm_button.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel,
                            font=('Arial', 12, 'bold'),
                            bg='#e74c3c', fg='white',
                            width=8, height=3,
                            relief=tk.RAISED, bd=3)
    cancel_button.pack(side=tk.LEFT, padx=10)
    
    # Bind Enter key
    name_entry.bind('<Return>', lambda e: on_confirm())
    
    # Show keyboard after delay
    def show_keyboard():
        def keyboard_confirm(text):
            name_var.set(text)
            on_confirm()
        
        show_simple_keyboard(dialog, name_entry, keyboard_confirm)
    
    dialog.after(500, show_keyboard)
    
    # Instructions
    instruction = tk.Label(root, 
                          text="Exact Positioning Test:\n\n" +
                               "• Input window positioned at VERY TOP (y=10)\n" +
                               "• Keyboard positioned at VERY BOTTOM\n" +
                               "• Minimal margins for maximum screen usage\n" +
                               "• Confirm button always present\n" +
                               "• Press ESC to close keyboard\n" +
                               "• Click 'Done' on keyboard or 'Confirm' to proceed\n\n" +
                               "Screen Layout:\n" +
                               "┌─────────────────────────────────────┐\n" +
                               "│           Input Window              │ ← y=10\n" +
                               "└─────────────────────────────────────┘\n" +
                               "│                                     │\n" +
                               "│           Video Area                 │\n" +
                               "│                                     │\n" +
                               "└─────────────────────────────────────┘\n" +
                               "┌─────────────────────────────────────┐\n" +
                               "│           On-Screen Keyboard        │ ← y=screen_height-250\n" +
                               "└─────────────────────────────────────┘",
                          font=('Arial', 10),
                          fg='white', bg='#2c3e50',
                          justify=tk.LEFT)
    instruction.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_exact_positioning() 