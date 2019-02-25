import cv2

videoCapture = cv2.VideoCapture('../data/video/0.flv')
success, frame = videoCapture.read()
while (success):
    success, frame = videoCapture.read()
    cv2.imshow('test', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
