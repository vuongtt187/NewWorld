# 🅿️ Smart Parking Management and Query System (Python)

This application is a real-time smart parking management system built with Python, using computer vision and OCR to automatically detect vehicles and license plates, manage parking slot status, and log parking events to a local database. It also communicates with an ESP32 device to display live slot status on-site.

## 🚀 Features

### ✅ Real-Time Video Processing
- Detects vehicles using YOLOv8.
- Detects license plates from cropped vehicles using a second YOLO model.
- Recognizes plate text using PaddleOCR.
- Maps detected vehicles to predefined parking slots based on IoU.

### ✅ Intelligent Parking Slot Assignment
- Identifies which vehicle occupies which slot.
- Uses a voting mechanism to stabilize OCR results.
- Logs time-in and time-out of vehicles into an SQLite database.

### ✅ ESP32 Integration
- Sends the current parking status (license plates or empty) to an ESP32 device via HTTP POST every 5 seconds.
- Data format: 4 license plate fields (or placeholders) in a 32-character string.

### ✅ Local SQLite Database
- `vehicles`: stores license plate, brand, color, and owner.
- `parking_slots`: slot locations and associated cameras.
- `parking_logs`: entry/exit timestamps per vehicle.
- `cameras`: basic info for camera zones (e.g., “Khu A”).

## 🧪 Environment

The application is developed in a **Python 3.10.11** environment, utilizing:

- **Torch 2.1.0** with **CUDA 11.8**
- **PaddlePaddle-GPU 2.6.2**
- **Ultralytics 8.3.150**
- **PaddleOCR 2.6.1.3**

These tools enable advanced real-time image recognition and intelligent processing across multiple modules.

## 🖥️ Main Modules

| Module | Description |
|--------|-------------|
| `main.py` | Main entrypoint for video capture, detection, OCR, database logging, and ESP32 sync. |
| `detect_vehicle.py` | YOLO-based vehicle detector (car, bus, motorcycle, truck). |
| `detect_plate.py` | YOLO-based license plate detector. |
| `ocr_base.py` | PaddleOCR wrapper with preprocessing and voting. |
| `parking_detector.py` | IOU-based slot assignment logic. |
| `db_manager.py` | SQLite database manager for logs, vehicles, and slots. |

## 📷 Sample Hardware Setup
- Camera pointing at 4 parking slots.
- ESP32 connected to sensors and OLED screen for live display.
- Python app runs on edge device (PC, Jetson, etc.) and sends updates to ESP32.

## 🔧 How to Use

To start the real-time detection system:
```bash
python main.py
If you want to look up parked vehicles or query vehicle history, run:
python queryApp.py
 
### 👤 Author
vuong.tt1807