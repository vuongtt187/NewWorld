import cv2

slot_boxes = []
drawing = False
start_point = ()

def draw_rectangle(event, x, y, flags, param):
    global drawing, start_point, slot_boxes

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        box = (min(start_point[0], end_point[0]), min(start_point[1], end_point[1]),
               max(start_point[0], end_point[0]), max(start_point[1], end_point[1]))
        slot_boxes.append(box)
        print(f"✅ Added slot: {box}")
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

# Mở camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("❌ Không thể mở camera.")
    exit()

cv2.namedWindow("Xác định ô đỗ từ camera")
cv2.setMouseCallback("Xác định ô đỗ từ camera", draw_rectangle)

print("🎥 Camera đã mở. Dùng chuột để vẽ các khung đỗ xe. Nhấn 's' để lưu, 'q' để thoát.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được từ camera.")
        break

    temp = frame.copy()
    for box in slot_boxes:
        cv2.rectangle(temp, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    cv2.imshow("Xác định ô đỗ từ camera", temp)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('s'):
        print("\n📦 Danh sách tọa độ các slot đã lưu:")
        for i, box in enumerate(slot_boxes):
            print(f"Slot {i}: {box}")

cap.release()
cv2.destroyAllWindows()
