import tkinter as tk

class CustomDialog:
    """Custom dialog class to replace standard messageboxes with themed windows"""
    
    @staticmethod
    def show_info(parent, title, message):
        """Show info dialog"""
        return CustomDialog._show_dialog(parent, title, message, "info")
    
    @staticmethod
    def show_error(parent, title, message):
        """Show error dialog"""
        return CustomDialog._show_dialog(parent, title, message, "error")
    
    @staticmethod
    def show_warning(parent, title, message):
        """Show warning dialog"""
        return CustomDialog._show_dialog(parent, title, message, "warning")
    
    @staticmethod
    def ask_yes_no(parent, title, message):
        """Show yes/no dialog"""
        return CustomDialog._show_dialog(parent, title, message, "question")
    
    @staticmethod
    def _show_dialog(parent, title, message, dialog_type):
        """Internal method to create and show dialog"""
        dialog = tk.Toplevel(parent)
        dialog.grab_set()
        dialog.title(title)
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        dialog.transient(parent)
        
        # Center dialog
        dialog.update_idletasks()
        width = 500
        height = 400
        x = (parent.winfo_screenwidth() - width) // 3
        y = (parent.winfo_screenheight() - height) // 3
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame
        main_frame = tk.Frame(dialog, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and title frame
        header_frame = tk.Frame(main_frame, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icon based on dialog type
      
        
        # Title colors
        title_colors = {
            'info': '#3498db',
            'error': '#e74c3c',
            'warning': '#f39c12',
            'question': '#9b59b6'
        }
        
        icon_label = tk.Label(header_frame, text="", font=('Arial', 24), bg='#2c3e50')
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(header_frame, text=title, 
                              font=('Arial', 18, 'bold'), 
                              fg=title_colors.get(dialog_type, '#3498db'), 
                              bg='#2c3e50')
        title_label.pack(side=tk.LEFT)
        
        # Message frame
        message_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message text
        message_text = tk.Text(message_frame, 
                              font=('Arial', 18), 
                              bg='#34495e', 
                              fg='#ecf0f1',
                              wrap=tk.WORD,
                              relief=tk.FLAT,
                              state=tk.NORMAL,
                              height=6)
        message_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Insert message and make read-only
        message_text.insert(tk.END, message)
        message_text.config(state=tk.DISABLED)
        
        # Scrollbar if needed
        if len(message) > 200:
            scrollbar = tk.Scrollbar(message_frame, orient=tk.VERTICAL, command=message_text.yview)
            message_text.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill=tk.X)
        
        # Result storage
        result = None
        
        def on_button_click(value):
            nonlocal result
            result = value
            dialog.destroy()
        
        # Create buttons based on dialog type
        if dialog_type == "question":
            # Yes/No buttons
            yes_btn = tk.Button(button_frame, text="Yes", 
                               command=lambda: on_button_click(True),
                               font=('Arial', 14, 'bold'),
                               bg='#27ae60', fg='white',
                               width=10, height=2,
                               relief=tk.RAISED, bd=3,
                               cursor='hand2')
            yes_btn.pack(side=tk.RIGHT, padx=(10, 0))
            yes_btn.focus_set()
            
            no_btn = tk.Button(button_frame, text="No", 
                              command=lambda: on_button_click(False),
                              font=('Arial', 14, 'bold'),
                              bg='#e74c3c', fg='white',
                              width=10, height=2,
                              relief=tk.RAISED, bd=3,
                              cursor='hand2')
            no_btn.pack(side=tk.RIGHT)

        else:
            # OK button
            ok_btn = tk.Button(button_frame, text="OK", 
                              command=lambda: on_button_click(True),
                              font=('Arial', 14, 'bold'),
                              bg='#3498db', fg='white',
                              width=12, height=2,
                              relief=tk.RAISED, bd=3,
                              cursor='hand2')
            ok_btn.pack(side=tk.RIGHT)
            ok_btn.focus_set()
        
        # Handle window close
        def on_close():
            nonlocal result
            result = False if dialog_type == "question" else True
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # Bind Enter and Escape keys
        def on_enter(event):
            if dialog_type == "question":
                on_button_click(True)  # Yes for questions
            else:
                on_button_click(True)  # OK for others
        
        def on_escape(event):
            if dialog_type == "question":
                on_button_click(False)  # No for questions
            else:
                on_button_click(True)   # OK for others
        
        dialog.bind('<Return>', on_enter)
        dialog.bind('<Escape>', on_escape)
        
        # Focus and wait
        dialog.focus()
        dialog.wait_window()
        
        return result 