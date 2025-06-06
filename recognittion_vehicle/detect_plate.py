from ultralytics import YOLO
import cv2
import numpy as np

class LicensePlateDetector:
    def __init__(self, model_path, conf_threshold=0.5):
        """
        Khởi tạo detector với model YOLO.
        
        :param model_path: Đường dẫn đến file model YOLO đã huấn luyện để nhận diện biển số.
        :param conf_threshold: Ngưỡng confidence để lọc kết quả nhận diện.
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect_plate(self, image):
        """
        Phát hiện 1 biển số trong ảnh xe đã crop.
        :param image: Ảnh đầu vào dưới dạng NumPy array (BGR).
        :return: Ảnh cắt của biển số nếu tìm thấy, ngược lại trả về None.
        """
        results = self.model(image)[0]

        for box in results.boxes:
            conf = box.conf.item()
            if conf >= self.conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_crop = image[y1:y2, x1:x2]
                return plate_crop

        return None

    def detect_all(self, image):
        """
        Phát hiện tất cả biển số trong ảnh gốc (frame).
        :param image: Ảnh đầu vào (BGR).
        :return: Danh sách toạ độ bbox [(x1, y1, x2, y2)].
        """
        results = self.model(image)[0]
        plate_boxes = []

        for box in results.boxes:
            conf = box.conf.item()
            if conf >= self.conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_boxes.append((x1, y1, x2, y2))

        return plate_boxes
