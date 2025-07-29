#!/usr/bin/env python3
"""
Test script to verify the employee table functionality
"""

import tkinter as tk
from tkinter import ttk

def test_table_ui():
    """Test the table UI components"""
    print("🧪 Testing Employee Table UI")
    
    root = tk.Tk()
    root.title("Test Employee Table")
    root.geometry("800x600")
    root.configure(bg='#2c3e50')
    
    # Create main frame
    main_frame = tk.Frame(root, bg='#2c3e50')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, text="Test Employee Table", 
                          font=('Arial', 18, 'bold'), 
                          fg='#ecf0f1', bg='#2c3e50')
    title_label.pack(pady=(0, 20))
    
    # Create table frame
    table_frame = tk.Frame(main_frame, bg='#2c3e50')
    table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    # Create Treeview for table display
    columns = ('name', 'check_in', 'check_out', 'status')
    employee_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    
    # Define column headings and widths
    employee_table.heading('name', text='Employee Name')
    employee_table.heading('check_in', text='Check-In Time')
    employee_table.heading('check_out', text='Check-Out Time')
    employee_table.heading('status', text='Status')
    
    # Configure column widths
    employee_table.column('name', width=200, minwidth=150)
    employee_table.column('check_in', width=120, minwidth=100)
    employee_table.column('check_out', width=120, minwidth=100)
    employee_table.column('status', width=150, minwidth=100)
    
    # Configure table styling
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Treeview', 
                   background='#34495e',
                   foreground='#ecf0f1',
                   fieldbackground='#34495e',
                   font=('Arial', 12))
    style.configure('Treeview.Heading',
                   background='#2c3e50',
                   foreground='#ecf0f1',
                   font=('Arial', 12, 'bold'))
    style.map('Treeview', 
             background=[('selected', '#4a6741')])
    
    # Scrollbar for table
    scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=employee_table.yview)
    employee_table.config(yscrollcommand=scrollbar.set)
     
    # Pack table and scrollbar
    employee_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Add sample data
    sample_data = [
        ("John Smith", "09:15:23", "Not Checked Out", "Checked In"),
        ("Jane Doe", "Not Checked In", "N/A", "Not Checked In"),
        ("Bob Johnson", "08:45:12", "17:30:45", "Checked Out"),
        ("Alice Brown", "09:22:15", "Not Checked Out", "Checked In"),
        ("Charlie Wilson", "Not Checked In", "N/A", "Not Checked In"),
        ("Diana Garcia", "08:30:10", "16:45:20", "Checked Out")
    ]
    
    for data in sample_data:
        employee_table.insert('', 'end', values=data)
    
    # Add test button
    def on_selection():
        selection = employee_table.selection()
        if selection:
            item = selection[0]
            values = employee_table.item(item, 'values')
            print(f"Selected: {values}")
            tk.messagebox.showinfo("Selection", f"Selected: {values[0]}")
    
    test_button = tk.Button(main_frame, text="Test Selection", 
                           command=on_selection,
                           font=('Arial', 12, 'bold'),
                           bg='#3498db', fg='white')
    test_button.pack(pady=10)
    
    print("✅ Table UI created successfully")
    print("📋 Sample data loaded:")
    for i, data in enumerate(sample_data, 1):
        print(f"   {i}. {data[0]} - {data[3]}")
    
    root.mainloop()

if __name__ == "__main__":
    try:
        import tkinter.messagebox
        test_table_ui()
    except Exception as e:
        print(f"❌ Error testing table UI: {e}")