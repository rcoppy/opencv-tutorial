import cv2 as cv

# img = cv.imread('photos/cat.jpg')
# cv.imshow('Cat', img)

# capture = cv.VideoCapture('videos/example.mp4')

capture = cv.VideoCapture(0)

while True: 
    isTrue, frame = capture.read()

    if isTrue:
        cv.imshow('Video', frame)

    if 0xFF==ord('d'): 
        break

    cv.waitKey(0)

capture.release()
cv.destroyAllWindows()
