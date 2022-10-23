import cv2 

cap = cv2.VideoCapture(1) 
# cap = cv2.VideoCapture("media/helmet_test.mp4")

while 1:
    ret, frame = cap.read()
    
    frame = cv2.resize(frame,(1280, 960))
    cv2.imshow("CAM", frame)   
    key=cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()