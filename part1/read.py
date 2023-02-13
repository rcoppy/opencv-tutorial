import cv2 as cv
import time

# img = cv.imread('photos/cat.jpg')
# cv.imshow('Cat', img)

# capture = cv.VideoCapture('videos/example.mp4')

capture = cv.VideoCapture(0)

font = cv.FONT_HERSHEY_TRIPLEX
font_color = (255, 125, 255)
font_thickness = 2

while True: 
    isTrue, frame = capture.read()

    if isTrue:
        coords = (int(frame.shape[1] * 0.2), int(frame.shape[0] * 0.75))

        cv.putText(frame, 'Hello, world', coords, font, 1.0, font_color, font_thickness)

        cv.imshow('Video', frame)

    if cv.waitKey(0) & 0xFF == ord('q'): 
        break

capture.release()
cv.destroyAllWindows()
