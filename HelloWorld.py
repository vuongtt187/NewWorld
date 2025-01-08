import cv2
import numpy as np

# # Đường dẫn đến file hình ảnh
# image_path = "C:/Users/imleg/VuongTr2/NewWorld/bienso.jpg"
# # Đọc ảnh
# img = cv2.imread(image_path)
# # Chuyển ảnh sang grayscale
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # Áp dụng bộ lọc Gaussian blur
# blur = cv2.GaussianBlur(gray, (5,5), 0)

# # Tìm các cạnh trong ảnh
# edged = cv2.Canny(blur, 30, 150)

# # Tìm các contour
# contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # Vẽ các contour lên ảnh
# cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

# # Hiển thị ảnh
# cv2.imshow('Image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# Tạo đối tượng để capture video từ camera
cap = cv2.VideoCapture(0)

# Tải bộ phân loại Haar cascade
plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')

while True:
    # Đọc một frame từ video
    ret, frame = cap.read()

    # Chuyển đổi ảnh thành grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Phát hiện biển số
    plates = plate_cascade.detectMultiScale(gray, 1.1, 4)

    # Vẽ hình chữ nhật quanh các biển số được phát hiện
    for (x,y,w,h) in plates:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

    # Hiển thị kết quả
    cv2.imshow('Video', frame)

    # Thoát khỏi vòng lặp nếu nhấn phím 'q'
    if cv2.waitKey(1) == ord('q'):
        break

# Giải phóng các tài nguyên
cap.release()
cv2.destroyAllWindows()