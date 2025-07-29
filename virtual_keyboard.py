import tkinter as tk

class VirtualKeyboard:
    """A reusable virtual keyboard component for text input"""
    
    def __init__(self, parent_frame, text_var, bg_color='#2c3e50'):
        self.parent_frame = parent_frame
        self.text_var = text_var
        self.bg_color = bg_color
        self.keyboard_frame = None
        self.entry_widget = None
        self.separator = None
        self.is_visible = False
        self.confirm_callback = None
        
    def set_entry_widget(self, entry_widget):
        """Set the entry widget that this keyboard will interact with"""
        self.entry_widget = entry_widget
    
    def setup_dynamic_keyboard(self, entry_widget, confirm_callback=None):
        """Set up dynamic keyboard that shows/hides on entry focus"""
        self.entry_widget = entry_widget
        self.confirm_callback = confirm_callback
        
        # Bind entry widget events
        def on_entry_focus_in(event):
            self.show_keyboard()
            self.update_cursor()
        
        def on_entry_focus_out(event):
            # Only hide if focus is not on keyboard
            if not self._is_focus_on_keyboard():
                self.hide_keyboard()
        
        def on_entry_click(event):
            self.show_keyboard()
            self.update_cursor()
            return "break"
        
        # Bind events
        entry_widget.bind('<FocusIn>', on_entry_focus_in)
        entry_widget.bind('<FocusOut>', on_entry_focus_out)
        entry_widget.bind('<Button-1>', on_entry_click)
        
        # Bind physical keyboard
        self.bind_physical_keyboard(entry_widget, confirm_callback)
    
    def _is_focus_on_keyboard(self):
        """Check if focus is currently on keyboard widget"""
        if not self.keyboard_frame:
            return False
        focus_widget = self.keyboard_frame.focus_get()
        return focus_widget and str(focus_widget).startswith(str(self.keyboard_frame))
    
    def update_cursor(self):
        """Ensure cursor stays at end"""
        if self.entry_widget:
            self.entry_widget.focus()
            self.entry_widget.icursor(tk.END)
    
    def press_key(self, key):
        """Optimized key press with auto-capitalization"""
        current_text = self.text_var.get()
        if key == ' ':
            self.text_var.set(current_text + ' ')
        else:
            # Smart capitalization
            if len(current_text) == 0 or current_text[-1] == ' ':
                self.text_var.set(current_text + key.upper())
            else:
                self.text_var.set(current_text + key.lower())
        self.update_cursor()
    
    def backspace(self):
        """Optimized backspace"""
        current_text = self.text_var.get()
        if current_text:
            self.text_var.set(current_text[:-1])
        self.update_cursor()
    
    def clear_text(self):
        """Optimized clear"""
        self.text_var.set("")
        self.update_cursor()
    
    def create_key_button(self, parent, text, command, style='normal', width=4):
        """Create optimized keyboard button"""
        colors = {
            'normal': {'bg': '#34495e', 'fg': 'white', 'active_bg': '#4a6741'},
            'special': {'bg': '#3498db', 'fg': 'white', 'active_bg': '#2980b9'},
            'action': {'bg': '#27ae60', 'fg': 'white', 'active_bg': '#229954'},
            'danger': {'bg': '#e74c3c', 'fg': 'white', 'active_bg': '#c0392b'}
        }
        
        color = colors.get(style, colors['normal'])
        
        btn = tk.Button(parent, text=text, width=width, height=3,
                       font=('Arial', 12, 'bold'),
                       bg=color['bg'], fg=color['fg'],
                       activebackground=color['active_bg'],
                       relief=tk.RAISED, bd=2,
                       command=command, cursor='hand2')
        
        # Enhanced hover effects
        def on_enter(e):
            btn.config(bg=color['active_bg'])
        
        def on_leave(e):
            btn.config(bg=color['bg'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def show_keyboard(self):
        """Show the virtual keyboard under the entry widget"""
        if self.is_visible or not self.entry_widget:
            return
        
        # Create separator
        self.separator = tk.Frame(self.parent_frame, height=2, bg='#7f8c8d')
        self.separator.pack(fill=tk.X, pady=10)
        
        # Create keyboard frame
        self.keyboard_frame = tk.Frame(self.parent_frame, bg=self.bg_color)
        self.keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_keyboard_layout()
        self.is_visible = True
    
    def hide_keyboard(self):
        """Hide the virtual keyboard"""
        if not self.is_visible:
            return
        
        if self.separator:
            self.separator.destroy()
            self.separator = None
        
        if self.keyboard_frame:
            self.keyboard_frame.destroy()
            self.keyboard_frame = None
        
        self.is_visible = False
    
    def create_keyboard(self, confirm_callback=None):
        """Create the virtual keyboard interface (always visible)"""
        self.confirm_callback = confirm_callback
        
        # Separator
        self.separator = tk.Frame(self.parent_frame, height=2, bg='#7f8c8d')
        self.separator.pack(fill=tk.X, pady=10)
        
        # Optimized keyboard layout
        self.keyboard_frame = tk.Frame(self.parent_frame, bg=self.bg_color)
        self.keyboard_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_keyboard_layout()
        self.is_visible = True
    
    def _create_keyboard_layout(self):
        """Create the keyboard layout elements"""
        # Define keyboard layout with better organization
        keyboard_layout = [
            {'keys': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'], 'style': 'normal'},
            {'keys': ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'], 'style': 'normal'},
            {'keys': ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'], 'style': 'normal'},
            {'keys': ['Z', 'X', 'C', 'V', 'B', 'N', 'M'], 'style': 'normal'}
        ]
        
        # Create number and letter rows
        for row_data in keyboard_layout:
            row_frame = tk.Frame(self.keyboard_frame, bg=self.bg_color)
            row_frame.pack(pady=2)
            
            for key in row_data['keys']:
                btn = self.create_key_button(row_frame, key, 
                                           lambda k=key.lower(): self.press_key(k),
                                           row_data['style'], 4)
                btn.pack(side=tk.LEFT)
        
        # Special keys row
        special_frame = tk.Frame(self.keyboard_frame, bg=self.bg_color)
        special_frame.pack(pady=5)
        
        # Space bar (wider)
        space_btn = tk.Button(special_frame, text="SPACE", width=20, height=3,
                             font=('Arial', 10, 'bold'), bg='#34495e', fg='white',
                             activebackground='#4a6741', relief=tk.RAISED, bd=2,
                             command=lambda: self.press_key(' '), cursor='hand2')
        space_btn.pack(side=tk.LEFT, padx=2)
        
        # Backspace
        back_btn = self.create_key_button(special_frame, "⌫", self.backspace, 'danger', 8)
        back_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear
        clear_btn = self.create_key_button(special_frame, "Clear", self.clear_text, 'special', 8)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Hide keyboard button
        hide_btn = self.create_key_button(special_frame, "Hide", self.hide_keyboard, 'special', 8)
        hide_btn.pack(side=tk.LEFT, padx=2)
        
        # Enter (only add if confirm_callback is provided)
        if self.confirm_callback:
            enter_btn = self.create_key_button(special_frame, "Enter", self.confirm_callback, 'action', 10)
            enter_btn.pack(side=tk.LEFT, padx=2)
    
    def bind_physical_keyboard(self, widget, confirm_callback=None, cancel_callback=None):
        """Bind physical keyboard events to the widget"""
        def on_key_press(event):
            """Handle physical keyboard input"""
            if event.keysym == 'Return' and confirm_callback:
                confirm_callback()
            elif event.keysym == 'Escape' and cancel_callback:
                cancel_callback()
            elif event.keysym == 'BackSpace':
                self.backspace()
                return "break"
            elif event.char.isprintable() and event.char != ' ':
                self.press_key(event.char)
                return "break"
            elif event.keysym == 'space':
                self.press_key(' ')
                return "break"
        
        widget.bind('<Key>', on_key_press)
        if confirm_callback:
            widget.bind('<Return>', lambda e: confirm_callback())
        if cancel_callback:
            widget.bind('<Escape>', lambda e: cancel_callback())
    
    def destroy(self):
        """Clean up keyboard widgets"""
        if self.separator:
            self.separator.destroy()
            self.separator = None
        if self.keyboard_frame:
            self.keyboard_frame.destroy()
            self.keyboard_frame = None
        self.is_visible = False 