# ex2tron's blog:
# http://ex2tron.wang

import cv2
import numpy as np

# 1.Canny边缘检测
img = cv2.imread('../ctpn/data/results/cropped_pic_77374694-1-64_110/77374694-1-64_110_0.jpg', 1)
# img = cv2.imread('../data/1.png', 1)

img_temp = img.copy()
blur = cv2.GaussianBlur(img_temp, (5, 5), 0)
edges = cv2.Canny(blur, 40, 90)

im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(img_temp, contours, -1, (0, 255, 0), 2)
area = []
for i in range(len(contours)):
    # area.append(cv2.contourArea(contours[i]))
    cv2.fillConvexPoly(img_temp, contours[i], [0, 0, 255])

# max_idx = np.argmax(area)
# cv2.fillConvexPoly(img_temp, contours[max_idx], [0,0,255])

cv2.imshow('canny', np.hstack((img, img_temp)))
cv2.waitKey(0)

#
# # 2.先阈值，后边缘检测
# # 阈值分割（使用到了番外篇讲到的Otsu自动阈值）
# _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# edges = cv2.Canny(thresh, 30, 70)
#
# cv2.imshow('canny', np.hstack((img, thresh, edges)))
# cv2.waitKey(0)
