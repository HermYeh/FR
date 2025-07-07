#!/usr/bin/env python3
"""
Test script for integrated keyboard: single window with input and keyboard
"""

import tkinter as tk
from tkinter import messagebox
from integrated_keyboard import show_integrated_keyboard

def test_integrated_keyboard():
    """Test the integrated keyboard window"""
    root = tk.Tk()
    root.title("Integrated Keyboard Test")
    root.geometry("800x600")
    root.configure(bg='#2c3e50')
    
    # Instructions
    instruction = tk.Label(root, 
                          text="Integrated Keyboard Test:\n\n" +
                               "• Single window combines input and keyboard\n" +
                               "• Input area at top, keyboard at bottom\n" +
                               "• Confirm and Cancel buttons always visible\n" +
                               "• Press ESC to close window\n" +
                               "• Click 'Done' on keyboard or 'Confirm' to proceed\n\n" +
                               "Window Layout:\n" +
                               "┌─────────────────────────────────────┐\n" +
                               "│           Input Area                 │ ← Top section\n" +
                               "│  [Enter Name] [Confirm] [Cancel]    │\n" +
                               "└─────────────────────────────────────┘\n" +
                               "│                                     │\n" +
                               "│           Keyboard Area              │ ← Bottom section\n" +
                               "│  [Q][W][E][R][T][Y][U][I][O][P]   │\n" +
                               "│  [A][S][D][F][G][H][J][K][L]      │\n" +
                               "│  [Z][X][C][V][B][N][M]            │\n" +
                               "│  [Space][Backspace][Clear][Done]   │\n" +
                               "└─────────────────────────────────────┘",
                          font=('Arial', 10),
                          fg='white', bg='#2c3e50',
                          justify=tk.LEFT)
    instruction.pack(pady=20)
    
    def show_keyboard():
        result = show_integrated_keyboard(root)
        print(f"Integrated keyboard result: {result}")
        if result:
            messagebox.showinfo("Result", f"Name entered: {result}")
        else:
            messagebox.showinfo("Result", "No name entered or cancelled")
    
    # Test button
    btn = tk.Button(root, text="Show Integrated Keyboard", 
                   command=show_keyboard,
                   font=('Arial', 12, 'bold'),
                   bg='#27ae60', fg='white',
                   width=25, height=2)
    btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_integrated_keyboard() 