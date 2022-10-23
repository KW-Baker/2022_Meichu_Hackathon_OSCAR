import numpy as np
import cv2
import os
import imutils

import time

NMS_THRESHOLD=0.25
MIN_CONFIDENCE=0.2

label_colors = {0: (0, 0, 255), 1: (0, 255, 0), 2: (0, 255, 255)}

def pedestrian_detection(image, model, layer_name, personidz=0):
    (H, W) = image.shape[:2]
    results = []

    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
    model.setInput(blob)
    layerOutputs = model.forward(layer_name)

    boxes = []
    centroids = []
    confidences = []
    classIDs = []

    for output in layerOutputs:
        for detection in output:

            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if classID == 0 or classID == 1 and confidence > MIN_CONFIDENCE:

                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                centroids.append((centerX, centerY))
                confidences.append(float(confidence))
                classIDs.append(classID)
    idzs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONFIDENCE, NMS_THRESHOLD)
    
    if len(idzs) > 0:
        for i in idzs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            res = (confidences[i], (x, y, x + w, y + h), centroids[i], classIDs[i])
            results.append(res)
    return results

# 讀入類別名稱
labelsPath = "./configs/yolov4-helmet-detection.names"
LABELS = open(labelsPath).read().strip().split("\n")

# 讀入yolo-v4參數以及設定檔
weights_path = "./configs/yolov4-helmet-detection.weights"
config_path = "./configs/yolov4-helmet-detection.cfg"
model = cv2.dnn.readNetFromDarknet(config_path, weights_path)
layer_name = model.getLayerNames()
layer_name = [layer_name[i[0] - 1] for i in model.getUnconnectedOutLayers()]

model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


# 針對筆電視訊影像進行偵測，也可改為其他影像來源
cap = cv2.VideoCapture(0)

start_time = time.time()
counter = 0

while True:
    (grabbed, image) = cap.read()

    if not grabbed:
        break
    
    image = imutils.resize(image, width=700)
    results = pedestrian_detection(image, model, layer_name,
		personidz=LABELS.index("helmet"))

    # 畫出偵測到的每個方框
    for res in results:
        cv2.rectangle(image, (res[1][0],res[1][1]), (res[1][2],res[1][3]), label_colors[res[3]], 2)


    counter += 1  # 計算幀數
    if (time.time() - start_time) != 0:  # 實時顯示幀數
        cv2.putText(image, "FPS {0}".format(float('%.1f' % (counter / (time.time() - start_time)))), (550, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                    2)
        # src = cv2.resize(image, (416 // 2, 416 // 2), interpolation=cv2.INTER_CUBIC)  # 窗口大小
        cv2.imshow("Detection",image)
        # cv2.imshow('frame', src)
        print("FPS: ", counter / (time.time() - start_time))
        counter = 0
        start_time = time.time()

    




        
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()


# https://ithelp.ithome.com.tw/articles/10270068