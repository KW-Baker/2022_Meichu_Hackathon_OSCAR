from asyncore import loop
import tensorflow as tf
from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4
import time
import cv2 
import sys
from Adafruit_IO import MQTTClient

cap = cv2.VideoCapture(1) 
# cap = cv2.VideoCapture("media/helmet_test.mp4")

WIDTH, HEIGHT = (640, 480) 

model = YOLOv4(
    input_shape=(HEIGHT, WIDTH, 3), 
    anchors=YOLOV4_ANCHORS,
    num_classes=3,     
    yolo_max_boxes=50, 
    yolo_iou_threshold=0.25, 
    yolo_score_threshold=0.25, 
)
 
model.load_weights('yolov4.h5') 

CLASSES = [
    'head', 'helmet', 'human'
]

while 1:
    # if cam == 'on':
        stime=time.time()
        ret, frame = cap.read()
        frame = cv2.resize(frame,(WIDTH, HEIGHT))

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = tf.expand_dims(tf.convert_to_tensor(image, dtype=tf.float32) , axis=0) / 255

        boxes, scores, classes, null = model.predict(image)
        boxes = boxes[0] * [WIDTH, HEIGHT, WIDTH, HEIGHT]
        scores = scores[0]
        classes = classes[0].astype(int)

        for (xmin, ymin, xmax, ymax), score, class_idx in zip(boxes, scores, classes):
            if score > 0.5: 
                if class_idx==0:
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 0, 255), 3)
                elif class_idx==1:
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 3)
                elif class_idx==2:
                    cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (255, 178, 50), 3)

                text = CLASSES[class_idx] + ': {0:.2f}'.format(score)            
                cv2.putText(frame, text,  (int(xmin), int(ymin)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)

        etime=time.time()
        fps=round(1/(etime-stime),2)
        cv2.putText(frame, str(fps),  (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)
        frame = cv2.resize(frame,(1280, 960))
        cv2.imshow("YOLO", frame)   
        key=cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

cap.release()

cv2.destroyAllWindows()