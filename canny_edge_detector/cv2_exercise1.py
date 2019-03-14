# ex2tron's blog:
# http://ex2tron.wang

import cv2
import numpy as np


def track_back(x):
    pass


img = cv2.imread('../ctpn/data/results/cropped_pic_77374694-1-64_110/77374694-1-64_110_0.jpg', 0)
cv2.namedWindow('window')

# 创建滑动条
cv2.createTrackbar('maxVal', 'window', 100, 255, track_back)
cv2.createTrackbar('minVal', 'window', 200, 255, track_back)

while (True):
    # 获取滑动条的值
    max_val = cv2.getTrackbarPos('maxVal', 'window')
    min_val = cv2.getTrackbarPos('minVal', 'window')

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(img, min_val, max_val)

    # blur = cv2.GaussianBlur(img, (5, 5), 0)
    # _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # edges = cv2.Canny(thresh, 30, 70)

    cv2.imshow('window', edges)

    # 按下ESC键退出
    if cv2.waitKey(30) == 27:
        break
