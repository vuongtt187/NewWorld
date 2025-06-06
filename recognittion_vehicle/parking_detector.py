import cv2
import numpy as np

class ParkingSlotDetector:
    def __init__(self, slot_boxes, iou_threshold=0.3):
        """
        slot_boxes: List các bounding box của ô đỗ xe, mỗi box là (x1, y1, x2, y2)
        iou_threshold: Ngưỡng IOU để xác định một xe có chiếm ô đỗ hay không
        """
        self.slot_boxes = slot_boxes
        self.iou_threshold = iou_threshold

    def compute_iou(self, boxA, boxB):
        """Tính IOU giữa 2 bounding box"""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou

    def detect(self, car_boxes):
        """
        Phát hiện các slot bị chiếm bởi xe.
        Trả về: danh sách chỉ số các slot bị chiếm
        """
        occupied_slots = set()
        for i, slot in enumerate(self.slot_boxes):
            for j, car_box in enumerate(car_boxes):
                iou = self.compute_iou(slot, car_box)
                # print(f"[DEBUG] Slot {i} vs Car {j} -> IOU = {iou:.3f}")
                if iou >= self.iou_threshold:
                    occupied_slots.add(i)
        return occupied_slots