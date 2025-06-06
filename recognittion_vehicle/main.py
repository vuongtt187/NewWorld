import cv2
import difflib
import time
import requests
from datetime import datetime
from detect_vehicle import VehicleDetector
from detect_plate import LicensePlateDetector
from ocr_base import PlateOCR_Base
from parking_detector import ParkingSlotDetector
from db_manager import ParkingDatabase

def find_similar_plate(new_plate, known_plates, threshold=0.75):
    for plate in known_plates:
        ratio = difflib.SequenceMatcher(None, new_plate, plate).ratio()
        if ratio >= threshold:
            return plate
    return new_plate

def send_slot_status_to_esp32(slot_states):
    try:
        parts = []
        for i in range(4):
            plate = slot_states.get(i, "").replace("-", "").replace(".", "").strip()
            if not plate or len(plate) != 8:
                parts.append("________")
            else:
                parts.append(plate)
        payload = "".join(parts)
        url = "http://192.168.52.208/plate" # ip dress
        headers = {"Content-Type": "text/plain"}
        requests.post(url, data=payload, headers=headers)
        print("[GỬI ESP32]", payload)
    except Exception as e:
        print("[LỖI gửi ESP32]", e)

def main():
    vehicle_detector = VehicleDetector(model_path=r"D:\Smart_parking_management_and_query\model_AI\DetectVehicleModel.pt")# model DVH
    plate_detector = LicensePlateDetector(model_path=r"D:\Smart_parking_management_and_query\model_AI\DetectLicensePlateModel.pt") # model DLP
    ocr_engine = PlateOCR_Base()
    db = ParkingDatabase()

    slot_boxes = [
        (102, 146, 178, 241),
        (225, 152, 303, 250),
        (347, 149, 439, 255),
        (462, 154, 582, 263),
    ]
    parking_detector = ParkingSlotDetector(slot_boxes, iou_threshold=0.25)

    last_logged_plate = {}
    slot_states = {}
    last_send_time = time.time()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = vehicle_detector.detect_vehicles(frame)
        frame = vehicle_detector.draw_boxes(frame, detections)

        car_boxes = []
        for _, row in detections.iterrows():
            x1, y1, x2, y2 = row['xmin'], row['ymin'], row['xmax'], row['ymax']
            car_boxes.append((x1, y1, x2, y2))
            vehicle_crop = frame[y1:y2, x1:x2]
            plate_crop = plate_detector.detect_plate(vehicle_crop)

            if plate_crop is not None:
                text, conf = ocr_engine.predict_image(plate_crop)
                if text and conf >= 0.5:
                    raw_plate = ocr_engine.correct_plate_format(text)
                    known_plates = db.get_all_plates()
                    clean_plate = find_similar_plate(raw_plate, known_plates)

                    best_slot = None
                    best_iou = 0
                    for idx, slot in enumerate(slot_boxes):
                        iou = parking_detector.compute_iou(slot, (x1, y1, x2, y2))
                        if iou > best_iou:
                            best_iou = iou
                            best_slot = idx

                    if best_slot is not None:
                        stable_plate = ocr_engine.update_vote(best_slot, clean_plate)
                        if stable_plate:
                            if not db.check_vehicle_exists(stable_plate):
                                db.add_vehicle(stable_plate)
                            if last_logged_plate.get(best_slot) != stable_plate:
                                db.log_parking_event(stable_plate, best_slot + 1)
                                last_logged_plate[best_slot] = stable_plate
                            slot_states[best_slot] = stable_plate
                            
        occupied = parking_detector.detect(car_boxes)
        for slot_idx in range(len(slot_boxes)):
            was_occupied = slot_idx in slot_states
            is_now_empty = slot_idx not in occupied
            if was_occupied and is_now_empty:
                db.update_time_out(slot_states[slot_idx], slot_idx + 1)
                del slot_states[slot_idx]

        if time.time() - last_send_time >= 5:
            send_slot_status_to_esp32(slot_states)
            last_send_time = time.time()

        height = frame.shape[0]
        start_y = height - 80
        line_height = 20
        for i in range(len(slot_boxes)):
            slot_index = i + 1
            color = (0, 0, 255) if i in occupied else (0, 255, 0)
            status_text = slot_states[i] if i in slot_states and i in occupied else "Empty"
            cv2.putText(frame, f"Slot {slot_index}: {status_text}", (10, start_y + i * line_height),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Vehicle + Plate + Parking Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    ocr_engine.release_ocr()
    db.close()

if __name__ == "__main__":
    main()
