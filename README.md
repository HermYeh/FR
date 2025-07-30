# Face Recognition Attendance System

A comprehensive face recognition-based attendance tracking system with desktop GUI, web interface, and touch screen support.

## Features

- **Real-time Face Recognition**: Uses FaceNet (MTCNN + InceptionResnetV1) for accurate face detection and recognition
- **Multiple Interfaces**: Desktop GUI, web interface, and command-line tools
- **Touch Screen Support**: Virtual keyboard and touch-friendly interface
- **Attendance Management**: Check-in/check-out tracking with photo capture
- **Employee Management**: Add, edit, delete employees with detailed information
- **Reporting**: Export attendance reports to CSV
- **Configurable Settings**: Camera, recognition, and processing parameters
- **Database**: SQLite-based storage with backup/restore functionality

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Desktop Application**:
   ```bash
   python face_recognition_attendance_ui.py
   ```

3. **Or Run Web Interface**:
   ```bash
   python attendance_web_server.py
   ```

4. **Add Employees**: Use the "Add Employee" feature to register faces
5. **Start Attendance**: Point camera at faces for automatic check-in/out

## System Requirements

- Python 3.8+
- Webcam or USB camera
- 4GB+ RAM (8GB+ recommended)
- Optional: CUDA-compatible GPU for acceleration

## Documentation

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

## Project Structure

```
FR/
├── face_recognition_attendance_ui.py  # Main desktop application
├── attendance_web_server.py           # Web interface
├── attendance_cli.py                  # Command line tools
├── camera_handler.py                  # Camera processing
├── face_processing.py                 # Face recognition engine
├── attendance_database.py             # Database operations
├── menu_ui.py                         # GUI menu system
├── virtual_keyboard.py                # Touch screen keyboard
├── requirements.txt                   # Dependencies
└── templates/                         # Web interface templates
```

## License

This project is for educational and internal use. Please ensure compliance with privacy laws when using face recognition technology.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions, please check the troubleshooting section in [SETUP.md](SETUP.md).