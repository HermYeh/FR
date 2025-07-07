#!/usr/bin/env python3
"""
Test script for new layout: input window at top, keyboard at bottom
"""

import tkinter as tk
from tkinter import messagebox
from simple_keyboard import show_simple_keyboard

def test_new_layout():
    """Test the new layout with input at top and keyboard at bottom"""
    root = tk.Tk()
    root.title("New Layout Test")
    root.geometry("800x600")
    root.configure(bg='#2c3e50')
    
    # Create a dialog at the top
    dialog = tk.Toplevel(root)
    dialog.title("Enter Name")
    dialog.geometry("500x150")
    dialog.configure(bg='#2c3e50')
    
    # Position dialog at top
    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    x = (screen_width // 2) - (500 // 2)
    y = 50  # Position at top
    dialog.geometry(f"500x150+{x}+{y}")
    
    # Make dialog stay on top
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    
    # Create dialog content
    title_label = tk.Label(dialog, text="Enter User Name", 
                          font=('Arial', 16, 'bold'), 
                          fg='white', bg='#2c3e50')
    title_label.pack(pady=10)
    
    # Entry field
    name_var = tk.StringVar()
    name_entry = tk.Entry(dialog, textvariable=name_var, 
                        font=('Arial', 14), 
                        width=30, 
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
                             width=10, height=2,
                             relief=tk.RAISED, bd=3)
    confirm_button.pack(side=tk.LEFT, padx=10)
    
    # Cancel button
    cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel,
                            font=('Arial', 12, 'bold'),
                            bg='#e74c3c', fg='white',
                            width=10, height=2,
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
                          text="New Layout Test:\n\n" +
                               "• Input window positioned at top of screen\n" +
                               "• Keyboard positioned at bottom of screen\n" +
                               "• Confirm button always present\n" +
                               "• Press ESC to close keyboard\n" +
                               "• Click 'Done' on keyboard or 'Confirm' to proceed",
                          font=('Arial', 12),
                          fg='white', bg='#2c3e50',
                          justify=tk.LEFT)
    instruction.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test_new_layout() 