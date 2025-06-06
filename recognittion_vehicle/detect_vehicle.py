import cv2
from ultralytics import YOLO
import pandas as pd

class VehicleDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_vehicles_from_image(self, image_path, conf_threshold=0.3):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        return self.detect_vehicles(img, conf_threshold)

    def detect_vehicles(self, img, conf_threshold=0.3):
        results = self.model(img)[0]
        detections = []
        vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id]
            conf = float(box.conf[0])
            if cls_name in vehicle_classes and conf >= conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    'name': cls_name,
                    'confidence': conf,
                    'xmin': x1,
                    'ymin': y1,
                    'xmax': x2,
                    'ymax': y2
                })
        return pd.DataFrame(detections)

    def draw_boxes(self, img, detections):
        for _, row in detections.iterrows():
            x1, y1, x2, y2 = row['xmin'], row['ymin'], row['xmax'], row['ymax']
            label = f"{row['name']} {row['confidence']:.2f}"
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img

    def detect_from_camera(self, cam_index=0, conf_threshold=0.3):
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detect_vehicles(frame, conf_threshold)
            frame_with_boxes = self.draw_boxes(frame, detections)

            cv2.imshow("Vehicle Detection", frame_with_boxes)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# if __name__ == "__main__":
#     detector = VehicleDetector()
#     detector.detect_from_camera()
