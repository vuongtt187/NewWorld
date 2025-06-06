import cv2
import numpy as np
import os
import gc
import paddle
from paddleocr import PaddleOCR
from collections import deque, Counter

class PlateOCR_Base:
    def __init__(self):
        self._init_ocr()
        self.history = {}  # slot_id → deque các biển số

    def _init_ocr(self):
        try:
            self.ocr = PaddleOCR(
                det=False,
                cls=True,
                use_angle_cls=True,
                lang='en',
                use_gpu=True,
                drop_score=0.5,
                precision='fp32',
                ir_optim=True,
                show_log=False,
                rec_algorithm='CRNN',
                rec_model_dir=r'D:\Smart_parking_management_and_query\model_AI\rec_lite_en'
            )
            print("[INFO] PaddleOCR đã sẵn sàng.")
        except Exception as e:
            print(f"[ERROR] Không thể khởi tạo PaddleOCR: {e}")
            self.ocr = None

    def release_ocr(self):
        if hasattr(self, 'ocr'):
            del self.ocr
            gc.collect()
            paddle.device.cuda.empty_cache()
            print("[INFO] Đã giải phóng OCR")

    def predict_image(self, img):
        if not hasattr(self, 'ocr') or self.ocr is None:
            return '', 0.0
        if img is None or img.size == 0:
            return '', 0.0

        img = self.ensure_3channel(img)
        img = self.preprocess_image(img)

        try:
            result = self.ocr.ocr(img)
        except Exception:
            return '', 0.0

        if not result or not isinstance(result, list) or not result[0]:
            return '', 0.0

        # Ưu tiên dòng có độ tin cậy cao nhất
        best_line = max(result[0], key=lambda x: x[1][1])
        text = best_line[1][0]
        conf = best_line[1][1]
        text = self.correct_plate_format(text)
        return text, conf

    def correct_plate_format(self, text):
        if not text or len(text) < 3:
            return text
        char_to_num = {'B': '8', 'S': '5', 'Z': '2', 'I': '1', 'D': '0', 'A': '4', 'G': '6'}
        num_to_char = {'0': 'D', '1': 'I', '2': 'Z', '4': 'A', '5': 'S', '6': 'G', '8': 'B'}
        raw = ''.join(c for c in text if c.isalnum()).upper()
        fixed = list(raw)
        for i in range(min(2, len(fixed))):
            if fixed[i] in char_to_num:
                fixed[i] = char_to_num[fixed[i]]
        if len(fixed) > 2 and fixed[2].isdigit():
            fixed[2] = num_to_char.get(fixed[2], fixed[2])
        return ''.join(fixed)

    def update_vote(self, slot_id, plate_text, max_len=10):
        if slot_id not in self.history:
            self.history[slot_id] = deque(maxlen=max_len)
        self.history[slot_id].append(plate_text)
        most_common, _ = Counter(self.history[slot_id]).most_common(1)[0]
        return most_common

    def ensure_3channel(self, img):
        if len(img.shape) == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def preprocess_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (160, 48))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(enhanced, -1, sharpen_kernel)
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
