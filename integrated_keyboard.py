#!/usr/bin/env python3
"""
Integrated Keyboard Window
Combines name input and on-screen keyboard into a single window
"""

import tkinter as tk
from tkinter import ttk

class IntegratedKeyboard:
    def __init__(self, parent):
        self.parent = parent
        self.result = ""
        
        # Create integrated window
        self.window = tk.Toplevel(parent)
        self.window.title("Enter User Name")
        self.window.geometry("800x500")
        self.window.configure(bg='#2c3e50')
        
        # Make window stay on top
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()
        
        # Position window at top of screen
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        x = (screen_width // 2) - (800 // 2)
        y = 50  # Position at top
        self.window.geometry(f"800x500+{x}+{y}")
        
        # Bind escape key to close
        self.window.bind('<Escape>', lambda e: self.close_window())
        
        # Create integrated layout
        self.create_integrated_layout()
        
        # Focus on entry widget
        self.entry_widget.focus()
    
    def create_integrated_layout(self):
        """Create the integrated layout with input at top and keyboard at bottom"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Input area
        top_frame = tk.Frame(main_frame, bg='#2c3e50', height=150)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        top_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(top_frame, text="Enter User Name", 
                              font=('Arial', 16, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=(10, 5))
        
        # Instruction
        instruction_label = tk.Label(top_frame, text="Please enter the name for the new user:", 
                                   font=('Arial', 12), 
                                   fg='#ecf0f1', bg='#2c3e50')
        instruction_label.pack(pady=5)
        
        # Entry field
        self.entry_widget = tk.Entry(top_frame, 
                                    font=('Arial', 14), 
                                    width=40, 
                                    relief=tk.RAISED, bd=3)
        self.entry_widget.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(top_frame, bg='#2c3e50')
        button_frame.pack(pady=10)
        
        # Confirm button
        self.confirm_button = tk.Button(button_frame, text="Confirm", 
                                       command=self.confirm,
                                       font=('Arial', 12, 'bold'),
                                       bg='#27ae60', fg='white',
                                       width=10, height=2,
                                       relief=tk.RAISED, bd=3)
        self.confirm_button.pack(side=tk.LEFT, padx=10)
        
        # Cancel button
        self.cancel_button = tk.Button(button_frame, text="Cancel", 
                                      command=self.cancel,
                                      font=('Arial', 12, 'bold'),
                                      bg='#e74c3c', fg='white',
                                      width=10, height=2,
                                      relief=tk.RAISED, bd=3)
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Bottom section - Keyboard
        keyboard_frame = tk.Frame(main_frame, bg='#2c3e50')
        keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create keyboard layout
        self.create_keyboard_layout(keyboard_frame)
        
        # Bind Enter key to confirm
        self.entry_widget.bind('<Return>', lambda e: self.confirm())
    
    def create_keyboard_layout(self, parent_frame):
        """Create the keyboard layout"""
        # Keyboard rows
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', 'Space', 'Backspace', 'Clear']
            ]
        
        # Create buttons for each row
        for i, row in enumerate(rows):
            row_frame = tk.Frame(parent_frame, bg='#2c3e50')
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
        """Close window and return result"""
        self.result = self.entry_widget.get()
        self.close_window()
    
    def confirm(self):
        """Confirm the input"""
        self.result = self.entry_widget.get()
        self.close_window()
    
    def cancel(self):
        """Cancel and close window"""
        self.result = ""
        self.close_window()
    
    def close_window(self):
        """Close the window"""
        self.window.destroy()
    
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
        """Wait for window to close and return result"""
        self.window.wait_window()
        return self.result

def show_integrated_keyboard(parent):
    """Show the integrated keyboard and return the result"""
    keyboard = IntegratedKeyboard(parent)
    return keyboard.wait_for_result()

if __name__ == "__main__":
    # Test the integrated keyboard
    root = tk.Tk()
    root.title("Integrated Keyboard Test")
    root.geometry("400x200")
    
    def show_keyboard():
        result = show_integrated_keyboard(root)
        print(f"Integrated keyboard result: {result}")
        if result:
            messagebox.showinfo("Result", f"Name entered: {result}")
    
    btn = tk.Button(root, text="Show Integrated Keyboard", command=show_keyboard)
    btn.pack(pady=20)
    
    root.mainloop() 