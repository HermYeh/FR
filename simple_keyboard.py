#!/usr/bin/env python3
"""
Simple On-Screen Keyboard for Face Recognition System
A custom Tkinter-based keyboard widget
"""

import tkinter as tk
from tkinter import ttk

class SimpleKeyboard:
    def __init__(self, parent, entry_widget, confirm_callback=None):
        self.parent = parent
        self.entry_widget = entry_widget
        self.confirm_callback = confirm_callback
        self.result = ""
        
        # Create keyboard window - positioned at bottom of screen
        self.keyboard_window = tk.Toplevel(parent)
        self.keyboard_window.title("On-Screen Keyboard")
        self.keyboard_window.geometry("800x250")
        self.keyboard_window.configure(bg='#2c3e50')
        
        # Make keyboard stay on top
        self.keyboard_window.transient(parent)
        self.keyboard_window.grab_set()
        self.keyboard_window.focus_set()
        
        # Position keyboard at bottom of screen
        self.keyboard_window.update_idletasks()
        screen_width = self.keyboard_window.winfo_screenwidth()
        screen_height = self.keyboard_window.winfo_screenheight()
        x = (screen_width // 2) - (800 // 2)
        y = screen_height - 250  # Position at bottom
        self.keyboard_window.geometry(f"800x250+{x}+{y}")
        
        # Bind escape key to close
        self.keyboard_window.bind('<Escape>', lambda e: self.close_keyboard())
        
        # Create keyboard layout
        self.create_keyboard_layout()
        
        # Focus on entry widget
        self.entry_widget.focus()
    
    def create_keyboard_layout(self):
        """Create the keyboard layout"""
        # Main frame
        main_frame = tk.Frame(self.keyboard_window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Keyboard rows
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
            ['Space', 'Backspace', 'Clear', 'Done']
        ]
        
        # Create buttons for each row
        for i, row in enumerate(rows):
            row_frame = tk.Frame(main_frame, bg='#2c3e50')
            row_frame.pack(fill=tk.X, pady=2)
            
            for j, key in enumerate(row):
                if key == 'Space':
                    # Space bar - make it wider
                    btn = tk.Button(row_frame, text=key, width=8, height=2,
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  relief=tk.RAISED, bd=2,
                                  command=lambda: self.press_key(' '))
                elif key == 'Backspace':
                    btn = tk.Button(row_frame, text=key, width=8, height=2,
                                  font=('Arial', 8, 'bold'),
                                  bg='#e74c3c', fg='white',
                                  relief=tk.RAISED, bd=2,
                                  command=self.backspace)
                elif key == 'Clear':
                    btn = tk.Button(row_frame, text=key, width=8, height=2,
                                  font=('Arial', 8, 'bold'),
                                  bg='#f39c12', fg='white',
                                  relief=tk.RAISED, bd=2,
                                  command=self.clear_text)
                elif key == 'Done':
                    btn = tk.Button(row_frame, text=key, width=8, height=2,
                                  font=('Arial', 8, 'bold'),
                                  bg='#27ae60', fg='white',
                                  relief=tk.RAISED, bd=2,
                                  command=self.done)
                else:
                    # Regular letter/number keys
                    btn = tk.Button(row_frame, text=key.upper(), width=4, height=2,
                                  font=('Arial', 10, 'bold'),
                                  bg='#34495e', fg='white',
                                  relief=tk.RAISED, bd=2,
                                  command=lambda k=key: self.press_key(k))
                
                btn.pack(side=tk.LEFT, padx=1)
                
                # Add hover effect
                btn.bind('<Enter>', lambda e, b=btn: self.on_hover_enter(b))
                btn.bind('<Leave>', lambda e, b=btn: self.on_hover_leave(b))
    
    def press_key(self, key):
        """Handle key press"""
        current_text = self.entry_widget.get()
        self.entry_widget.delete(0, tk.END)
        self.entry_widget.insert(0, current_text + key)
        
        # Keep focus on entry widget
        self.entry_widget.focus()
    
    def backspace(self):
        """Handle backspace"""
        current_text = self.entry_widget.get()
        if current_text:
            new_text = current_text[:-1]
            self.entry_widget.delete(0, tk.END)
            self.entry_widget.insert(0, new_text)
        
        # Keep focus on entry widget
        self.entry_widget.focus()
    
    def clear_text(self):
        """Clear the text"""
        self.entry_widget.delete(0, tk.END)
        self.entry_widget.focus()
    
    def done(self):
        """Close keyboard and return result"""
        self.result = self.entry_widget.get()
        if self.confirm_callback:
            self.confirm_callback(self.result)
        self.close_keyboard()
    
    def close_keyboard(self):
        """Close the keyboard window"""
        self.keyboard_window.destroy()
    
    def on_hover_enter(self, button):
        """Handle button hover enter"""
        button.configure(bg='#3498db')
    
    def on_hover_leave(self, button):
        """Handle button hover leave"""
        if button.cget('text') == 'Backspace':
            button.configure(bg='#e74c3c')
        elif button.cget('text') == 'Clear':
            button.configure(bg='#f39c12')
        elif button.cget('text') == 'Done':
            button.configure(bg='#27ae60')
        else:
            button.configure(bg='#34495e')
    
    def wait_for_result(self):
        """Wait for keyboard to close and return result"""
        self.keyboard_window.wait_window()
        return self.result

def show_simple_keyboard(parent, entry_widget, confirm_callback=None):
    """Show the simple keyboard and return the result"""
    keyboard = SimpleKeyboard(parent, entry_widget, confirm_callback)
    return keyboard.wait_for_result()

if __name__ == "__main__":
    # Test the keyboard
    root = tk.Tk()
    root.title("Keyboard Test")
    root.geometry("400x200")
    
    entry = tk.Entry(root, font=('Arial', 14))
    entry.pack(pady=20)
    
    def show_keyboard():
        result = show_simple_keyboard(root, entry)
        print(f"Keyboard result: {result}")