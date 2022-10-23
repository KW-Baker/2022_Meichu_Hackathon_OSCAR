from asyncore import loop
import tensorflow as tf
from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4
import time
import cv2 
import sys
from Adafruit_IO import MQTTClient

ADAFRUIT_IO_KEY = 'aio_qmHC28uz3chz9KEczFdwI3oHqskI'
ADAFRUIT_IO_USERNAME = 'pin9726'
FEED_ID = 'cam'
WIDTH, HEIGHT = (640, 480) 
cam = 'on'

def connected(client):
    print('Subscribing to Feed {0}'.format(FEED_ID))
    client.subscribe(FEED_ID)
    print('Waiting for feed data...')

def disconnected(client):
    """Disconnected function will be called when the client disconnects."""
    sys.exit(1)

def message(client, feed_id, payload):
    """Message function will be called when a subscribed feed has a new value.
    The feed_id parameter identifies the feed, and the payload parameter has
    the new value.
    """
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    global cam
    cam = payload

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

client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.connect()
# client.loop_background()

cap = cv2.VideoCapture(0) 
# cap = cv2.VideoCapture("media/helmet_test.mp4")

while 1:
    if cam == 'on':
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

        cv2.imshow("YOLO", frame)   
        key=cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
    client.loop()


cap.release()

cv2.destroyAllWindows()