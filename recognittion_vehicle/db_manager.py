import sqlite3
from datetime import datetime

class ParkingDatabase:
    def __init__(self, db_path="parking_log.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_initial_data()
        self.reset_logs()

    def _normalize_plate(self, plate_number):
        return ''.join(c for c in plate_number if c.isalnum()).upper()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            plate_number TEXT PRIMARY KEY,
            brand TEXT,
            color TEXT,
            owner_name TEXT
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            ip_address TEXT,
            status TEXT DEFAULT 'active'
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_slots (
            slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER,
            location_description TEXT,
            FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT,
            slot_id INTEGER,
            time_in TEXT NOT NULL,
            time_out TEXT,
            FOREIGN KEY (plate_number) REFERENCES vehicles(plate_number),
            FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)
        );
        """)
        self.conn.commit()

    def insert_initial_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM cameras WHERE location = 'Khu A';")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO cameras (location, ip_address, status) VALUES (?, ?, ?)",
                                ('Khu A', '192.168.1.10', 'active'))
            self.conn.commit()

        self.cursor.execute("SELECT camera_id FROM cameras WHERE location = 'Khu A';")
        camera_id = self.cursor.fetchone()[0]

        for i in range(1, 5):
            desc = f"Slot {i} - Khu A"
            self.cursor.execute("SELECT COUNT(*) FROM parking_slots WHERE location_description = ?", (desc,))
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO parking_slots (camera_id, location_description) VALUES (?, ?)",
                                    (camera_id, desc))
        self.conn.commit()

    def reset_logs(self):
    # Xóa toàn bộ dữ liệu bảng parking_logs
        self.cursor.execute("DELETE FROM parking_logs;")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'parking_logs';")

    # ✅ Xóa toàn bộ dữ liệu bảng vehicles
        self.cursor.execute("DELETE FROM vehicles;")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'vehicles';")

        self.conn.commit()
        print("[⚠] Đã xóa toàn bộ dữ liệu bảng parking_logs và vehicles.")

    def check_vehicle_exists(self, plate_number):
        plate_number = self._normalize_plate(plate_number)
        self.cursor.execute("SELECT 1 FROM vehicles WHERE plate_number = ?", (plate_number,))
        return self.cursor.fetchone() is not None

    def add_vehicle(self, plate_number, brand=None, color=None, owner=None):
        plate_number = self._normalize_plate(plate_number)
        self.cursor.execute(
            "INSERT INTO vehicles (plate_number, brand, color, owner_name) VALUES (?, ?, ?, ?)",
            (plate_number, brand, color, owner)
        )
        self.conn.commit()

    def log_parking_event(self, plate_number, slot_id):
        plate_number = self._normalize_plate(plate_number)
        time_in = datetime.now().isoformat(timespec='seconds')
        print(f"[🅿 LOG] Ghi nhận {plate_number} vào slot {slot_id} lúc {time_in}")
        self.cursor.execute(
            "INSERT INTO parking_logs (plate_number, slot_id, time_in) VALUES (?, ?, ?)",
            (plate_number, slot_id, time_in)
                    )
        self.conn.commit()

    def update_time_out(self, plate_number, slot_id):
        plate_number = self._normalize_plate(plate_number)
        now = datetime.now().isoformat(timespec='seconds')
        self.cursor.execute("""
        SELECT log_id FROM parking_logs
        WHERE plate_number = ? AND slot_id = ? AND time_out IS NULL
        ORDER BY time_in DESC
        LIMIT 1
        """, (plate_number, slot_id))
        result = self.cursor.fetchone()
        if result:
            log_id = result[0]
            print(f"[⛔] {plate_number} rời khỏi slot {slot_id} lúc {now}")
            self.cursor.execute("""
            UPDATE parking_logs
            SET time_out = ?
            WHERE log_id = ?
            """, (now, log_id))
            self.conn.commit()
    
    def get_all_plates(self):
        self.cursor.execute("SELECT plate_number FROM vehicles")
        return [row[0] for row in self.cursor.fetchall()]
    
    def close(self):
        self.conn.close()
    
    # def is_vehicle_in_parking(self, plate_number):
    #     plate_number = self._normalize_plate(plate_number)
    #     self.cursor.execute("""
    #         SELECT 1 FROM parking_logs
    #         WHERE plate_number = ? AND time_out IS NULL
    #     """, (plate_number,))
    #     return self.cursor.fetchone() is not None

    # def get_current_parking_slot(self, plate_number):
    #     plate_number = self._normalize_plate(plate_number)
    #     self.cursor.execute("""
    #         SELECT slot_id, time_in FROM parking_logs
    #         WHERE plate_number = ? AND time_out IS NULL
    #         ORDER BY time_in DESC LIMIT 1
    #     """, (plate_number,))
    #     return self.cursor.fetchone()

    # def get_parking_duration(self, plate_number):
    #     from datetime import datetime
    #     slot_info = self.get_current_parking_slot(plate_number)
    #     if slot_info:
    #         _, time_in = slot_info
    #         time_in_dt = datetime.fromisoformat(time_in)
    #         return datetime.now() - time_in_dt
    #     return None

    # def get_parking_history(self, plate_number):
    #     plate_number = self._normalize_plate(plate_number)
    #     self.cursor.execute("""
    #         SELECT slot_id, time_in, time_out
    #         FROM parking_logs
    #         WHERE plate_number = ?
    #         ORDER BY time_in DESC
    #     """, (plate_number,))
    #     return self.cursor.fetchall()