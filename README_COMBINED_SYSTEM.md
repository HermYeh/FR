# Combined Face Recognition & Attendance System

A complete automated attendance tracking system that combines face recognition with attendance database management.

## 🎯 **Key Features**

### ✅ **Automatic Face Recognition**
- Real-time face detection and recognition
- Automatic check-in when a face is recognized for the first time each day
- Prevents duplicate check-ins (subsequent scans of the same person are ignored)
- 5-second cooldown between recognitions to avoid spam

### ✅ **Attendance Database**
- SQLite database for reliable data storage
- Track check-in/check-out times
- Calculate total hours worked
- Daily attendance summaries and reports

### ✅ **Multiple Interfaces**
- **Full-screen Face Recognition UI**: Primary interface for face scanning
- **Web Interface**: Remote access for management and reporting
- **Command-line Interface**: For system administration

### ✅ **Real-time Monitoring**
- Live attendance tracking
- Instant notifications when someone is checked in
- Daily attendance summaries
- Employee management

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
pip install flask pandas opencv-contrib-python pillow
```

### 2. **Start the Combined System**
```bash
python start_combined_system.py
```

This will start both:
- **Face Recognition UI** (Full screen)
- **Web Server** (Port 5000)

### 3. **Access the System**
- **Face Recognition**: Full-screen interface for face scanning
- **Web Interface**: http://localhost:5000
- **Network Access**: http://[YOUR_IP]:5000

## 📁 **System Components**

### Core Files
- `face_recognition_attendance_ui.py` - Main face recognition interface
- `attendance_web_server.py` - Web server for remote access
- `attendance_database.py` - Database management
- `start_combined_system.py` - Startup script for both systems

### Database Files
- `attendance.db` - SQLite database (auto-created)
- `dataset/` - Face training images
- `trainer/` - Trained face recognition model

## 🎮 **How It Works**

### **Face Recognition Process**
1. **Camera Detection**: Continuously scans for faces
2. **Face Recognition**: Identifies known faces using trained model
3. **Attendance Check**: Checks if person already checked in today
4. **Automatic Check-in**: Records attendance for first-time recognition
5. **Notification**: Shows success message and updates status

### **Daily Tracking Logic**
- Each person can only be checked in **once per day**
- Subsequent face scans of the same person are **ignored**
- System resets daily at midnight
- Tracks check-in time automatically

### **Web Interface Features**
- **Dashboard**: Real-time attendance summary
- **Manual Check-in/Check-out**: For manual operations
- **Employee Management**: Add/edit employees
- **Reports**: Generate attendance reports
- **System Status**: Monitor system health

## 🖥️ **Face Recognition UI**

### **Full-Screen Interface**
- Real-time video feed
- Face detection rectangles
- Recognition confidence display
- Status indicators

### **Training Mode**
- Capture 30 face images per person
- Automatic model training
- Multiple angles for better recognition

### **Attendance Tracking**
- Automatic check-in notifications
- Daily attendance status
- Manual check-in option
- Attendance summary display

## 🌐 **Web Interface**

### **Available Pages**
- **Dashboard**: Overview with daily summary
- **Check In/Out**: Manual attendance operations
- **Employees**: Manage employee list
- **Reports**: Generate filtered reports
- **Status**: System health monitoring

### **API Endpoints**
- `POST /api/check_in` - Check in employee
- `POST /api/check_out` - Check out employee
- `GET /api/summary` - Daily summary
- `GET /api/attendance` - Attendance data
- `GET /api/employees` - Employee list

## 📊 **Database Schema**

### **Attendance Table**
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    check_in_time TEXT,
    check_out_time TEXT,
    total_hours REAL,
    status TEXT DEFAULT 'present',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Employees Table**
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    position TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 **Configuration**

### **Face Recognition Settings**
- **Recognition Threshold**: 100 (lower = more strict)
- **Detection Sensitivity**: 1.15 scale factor
- **Minimum Neighbors**: 4 (more sensitive)
- **Cooldown Period**: 5 seconds between recognitions

### **Database Settings**
- **Auto-import**: Existing CSV data
- **Daily Reset**: Midnight automatic reset
- **Backup**: Automatic database backup

## 📱 **Usage Examples**

### **Starting the System**
```bash
# Start both systems
python start_combined_system.py

# Or start individually
python face_recognition_attendance_ui.py  # Face recognition only
python attendance_web_server.py           # Web server only
```

### **Training New Faces**
1. Run the face recognition UI
2. Click "Start Training"
3. Enter employee name
4. Follow capture instructions
5. System automatically trains model

### **Web Interface Access**
```bash
# Local access
http://localhost:5000

# Network access (replace with your IP)
http://192.168.1.100:5000
```

## 🔍 **Monitoring & Reports**

### **Real-time Monitoring**
- Live attendance status
- Recognition confidence levels
- System health indicators
- Error logging

### **Daily Reports**
- Attendance rate calculation
- Present/absent employee count
- Average hours worked
- Individual employee history

### **Export Options**
- CSV export for external analysis
- Filtered reports by date/employee
- Historical data access

## 🛡️ **Security Features**

### **Data Protection**
- SQLite database with proper indexing
- Input validation and sanitization
- Error handling and logging
- Graceful failure recovery

### **Access Control**
- Local network access only
- No external authentication (add as needed)
- Secure database connections

## 🔄 **Integration Options**

### **Existing Systems**
- Import from CSV files
- Export to external systems
- API endpoints for integration
- Database backup/restore

### **Future Enhancements**
- Email notifications
- Mobile app integration
- Advanced reporting with charts
- Multi-location support

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Camera Not Found**
   ```bash
   # Check camera permissions
   ls /dev/video*
   # Install camera drivers if needed
   ```

2. **Face Recognition Not Working**
   ```bash
   # Reinstall OpenCV with contrib
   pip uninstall opencv-python
   pip install opencv-contrib-python
   ```

3. **Web Server Not Starting**
   ```bash
   # Check if port 5000 is available
   netstat -tulpn | grep 5000
   # Kill process if needed
   sudo kill -9 [PID]
   ```

4. **Database Errors**
   ```bash
   # Check database file
   ls -la attendance.db
   # Recreate if corrupted
   rm attendance.db
   python attendance_database.py
   ```

### **Debug Mode**
```bash
# Enable debug logging
export FLASK_DEBUG=1
python attendance_web_server.py
```

## 📈 **Performance**

### **System Requirements**
- **CPU**: Multi-core recommended
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB for database and images
- **Camera**: USB webcam or built-in camera

### **Optimization Tips**
- Use SSD for faster database access
- Adequate lighting for better face recognition
- Regular database maintenance
- Monitor system resources

## 🎯 **Success Metrics**

- ✅ **100% Automated**: No manual intervention needed
- ✅ **Real-time Tracking**: Instant attendance recording
- ✅ **Duplicate Prevention**: Smart daily tracking
- ✅ **Multi-interface**: Web + UI access
- ✅ **Scalable**: Handles multiple employees
- ✅ **Reliable**: Robust error handling

## 📞 **Support**

### **Getting Help**
1. Check the troubleshooting section
2. Review system logs
3. Test individual components
4. Verify all dependencies are installed

### **System Logs**
- Face recognition logs in console
- Web server logs in Flask debug mode
- Database logs in SQLite

The combined system provides a complete, automated attendance tracking solution that's both powerful and user-friendly! 