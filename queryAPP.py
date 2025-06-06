import sqlite3
from tkinter import Tk, Label, Entry, Button, Text, messagebox
from datetime import datetime

DB_PATH = "parking_log.db"

class ParkingQueryApp:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.window = Tk()
        self.window.title("TRA CỨU BÃI ĐỖ XE")
        self.window.geometry("1080x680")
        self.create_widgets()
        self.window.mainloop()

    def create_widgets(self):
        Label(self.window, text="Biển số xe cần tìm:", font=("Arial", 12)).pack(pady=10)
        self.entry = Entry(self.window, font=("Arial", 12))
        self.entry.pack()
        Button(self.window, text="Tra cứu", font=("Arial", 12), command=self.query).pack(pady=10)
        self.result_text = Text(self.window, font=("Courier New", 10), width=130, height=28)
        self.result_text.pack(pady=5)

    def normalize_plate(self, plate):
        return ''.join(c for c in plate if c.isalnum()).upper()

    def format_datetime(self, dt_str):
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%H:%M:%S %d-%m-%Y")

    def query(self):
        plate = self.normalize_plate(self.entry.get().strip())
        if not plate:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập biển số xe!")
            return

        # Tra cứu hiện tại
        self.cursor.execute("""
            SELECT slot_id, time_in FROM parking_logs
            WHERE plate_number = ? AND time_out IS NULL
            ORDER BY time_in DESC LIMIT 1
        """, (plate,))
        current = self.cursor.fetchone()

        # Tra cứu lịch sử đầy đủ (bao gồm camera và vị trí)
        self.cursor.execute("""
            SELECT pl.slot_id, pl.time_in, pl.time_out, c.camera_id, c.location
            FROM parking_logs pl
            JOIN parking_slots ps ON pl.slot_id = ps.slot_id
            JOIN cameras c ON ps.camera_id = c.camera_id
            WHERE pl.plate_number = ?
            ORDER BY pl.time_in DESC
        """, (plate,))
        history = self.cursor.fetchall()

        self.result_text.delete(1.0, "end")
        self.result_text.insert("end", f"> Biển số: {plate}\n")
        if current:
            slot_id, time_in = current
            time_in_dt = datetime.fromisoformat(time_in)
            duration = datetime.now() - time_in_dt

            self.cursor.execute("""
                SELECT c.camera_id, c.location
                FROM parking_slots ps
                JOIN cameras c ON ps.camera_id = c.camera_id
                WHERE ps.slot_id = ?
            """, (slot_id,))
            cam_info = self.cursor.fetchone()
            if cam_info:
                camera_id, cam_location = cam_info
                self.result_text.insert("end", f"• Xe ĐANG đỗ tại Vị trí số {slot_id} ở {cam_location}\n")
                self.result_text.insert("end", f"• Vào lúc: {self.format_datetime(time_in)}\n")
                self.result_text.insert("end", f"• Thời gian đỗ: {str(duration).split('.')[0]}\n")
                self.result_text.insert("end", f"• Camera: {camera_id}\n")
        else:
            self.result_text.insert("end", "• Xe hiện KHÔNG có trong bãi.\n")

        self.result_text.insert("end", "\n🕓 Lịch sử:\n")
        for idx, (slot, time_in, time_out, cam_id, cam_loc) in enumerate(history, 1):
            time_in_fmt = self.format_datetime(time_in)
            time_out_fmt = self.format_datetime(time_out) if time_out else 'chưa rời bãi'
            self.result_text.insert("end", f"{idx:02}. Xe từng đỗ ở vị trí số {slot} khu {cam_loc} | Thời gian vào: {time_in_fmt} | Thời gian ra: {time_out_fmt} | Camera số {cam_id}\n")

if __name__ == "__main__":
    ParkingQueryApp()
