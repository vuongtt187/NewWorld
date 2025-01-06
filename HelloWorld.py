import cv2
import numpy as np

# Đường dẫn đến file hình ảnh
image_path = "C:/Users/imleg/VuongTr/Test/NewWorld/bienso.jpg"
# Đọc ảnh
img = cv2.imread(image_path)
# Chuyển ảnh sang grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Áp dụng bộ lọc Gaussian blur
blur = cv2.GaussianBlur(gray, (5,5), 0)

# Tìm các cạnh trong ảnh
edged = cv2.Canny(blur, 30, 150)

# Tìm các contour
contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Vẽ các contour lên ảnh
cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

# Hiển thị ảnh
cv2.imshow('Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()