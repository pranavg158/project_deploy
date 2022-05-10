# -*- coding: utf-8 -*-
"""streamlib_new.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kwZIehAqs3nTJS3lk6F5eM4W4mNpHHh1
"""

import streamlit as st
import cv2
import dlib
import imutils
import time
from scipy import spatial
import math
import tempfile
from PIL import Image
import tensorflow as tf
import os
import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, BatchNormalization, Flatten, GlobalAveragePooling2D
import numpy as np
from keras.applications.resnet import ResNet50
from tqdm import tqdm  
from keras.models import Sequential
from keras import layers
from keras.layers import Dense,InputLayer
from sklearn.model_selection import train_test_split


st.title("Vehicle Detection & Classification")
WIDTH = 1280
HEIGHT = 720
carCascade = cv2.CascadeClassifier("vech.xml")

from PIL import Image
img = Image.open("img.jpeg")
st.image(img, width=800)

st.sidebar.subheader("You would like to process....")
TYPE = st.sidebar.selectbox(" " ,options = ['Video','Image'])
#st.write(select_type(TYPE))

def select_type():
  if TYPE == 'Video' :
    TYPE1 = st.sidebar.selectbox("Choose one.... " ,options = ['Video for speed','Video for Count'])
    if TYPE1 == 'Video for speed':
      trackMultipleObjects()
    else:
      video_count_vehicle()
  else:
    image_process()





def trackMultipleObjects():
    video_file_buffer = st.sidebar.file_uploader("Upload a video", type=[ "mp4", "mov",'avi','asf', 'm4v' ]) 
    tfflie = tempfile.NamedTemporaryFile(delete=False)
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 0

    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}
    speed = [None] * 1000

    out = cv2.VideoWriter('outNew.mp4', cv2.VideoWriter_fourcc('m','p','4','v'), 10, (WIDTH, HEIGHT))
    while video_file_buffer:
      tfflie.write(video_file_buffer.read())
      vf = cv2.VideoCapture(tfflie.name)
      while True:
          start_time = time.time()
          rc, image = vf.read()
          if type(image) == type(None):
              break

          image = cv2.resize(image, (WIDTH, HEIGHT))
          resultImage = image.copy()

          frameCounter = frameCounter + 1
          carIDtoDelete = []

          for carID in carTracker.keys():
              trackingQuality = carTracker[carID].update(image)

              if trackingQuality < 7:
                  carIDtoDelete.append(carID)

          
          for carID in carIDtoDelete:
              print("Removing carID " + str(carID) + ' from list of trackers. ')
              print("Removing carID " + str(carID) + ' previous location. ')
              print("Removing carID " + str(carID) + ' current location. ')
              carTracker.pop(carID, None)
              carLocation1.pop(carID, None)
              carLocation2.pop(carID, None)

          
          if not (frameCounter % 10):
              gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
              cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

              for (_x, _y, _w, _h) in cars:
                  x = int(_x)
                  y = int(_y)
                  w = int(_w)
                  h = int(_h)

                  x_bar = x + 0.5 * w
                  y_bar = y + 0.5 * h

                  matchCarID = None

                  for carID in carTracker.keys():
                      trackedPosition = carTracker[carID].get_position()

                      t_x = int(trackedPosition.left())
                      t_y = int(trackedPosition.top())
                      t_w = int(trackedPosition.width())
                      t_h = int(trackedPosition.height())

                      t_x_bar = t_x + 0.5 * t_w
                      t_y_bar = t_y + 0.5 * t_h

                      if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                          matchCarID = carID

                  if matchCarID is None:
                      print(' Creating new tracker' + str(currentCarID))

                      tracker = dlib.correlation_tracker()
                      tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                      carTracker[currentCarID] = tracker
                      carLocation1[currentCarID] = [x, y, w, h]

                      currentCarID = currentCarID + 1

          for carID in carTracker.keys():
              trackedPosition = carTracker[carID].get_position()

              t_x = int(trackedPosition.left())
              t_y = int(trackedPosition.top())
              t_w = int(trackedPosition.width())
              t_h = int(trackedPosition.height())

              cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)

              carLocation2[carID] = [t_x, t_y, t_w, t_h]

          end_time = time.time()

          if not (end_time == start_time):
              fps = 1.0/(end_time - start_time)

          for i in carLocation1.keys():
              if frameCounter % 1 == 0:
                  [x1, y1, w1, h1] = carLocation1[i]
                  [x2, y2, w2, h2] = carLocation2[i]

                  carLocation1[i] = [x2, y2, w2, h2]

                  if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                      if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                          d_pixels = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
                          ppm = 8.8
                          d_meter = d_pixels/ppm
                          fps = 18
                          speed[i] = d_meter * fps * 3.6

                      if speed[i] != None and y1 >= 180:
                          cv2.putText(resultImage, str(int(speed[i])) + "km/h", (int(x1 + w1/2), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 100) ,2)

          cv2.imshow('result', resultImage)

          out.write(resultImage)

          if cv2.waitKey(1) == 27:
              break

    
    cv2.destroyAllWindows()
    out.release()




def image_process():
  image_file_buffer = st.sidebar.file_uploader("Upload a image", type=[ "jpg", "png","jpeg"])

  model1 = Sequential()
  model1.add(ResNet50(input_shape=(224,224,3),include_top=False, pooling='avg', weights='imagenet'))
  model1.add(Dense(220, activation='relu'))
  model1.add(Dense(220,activation='relu'))
  model1.add(Dense(8,activation='softmax'))
  model1.layers[1].trainable=False

  opt =tf.keras.optimizers.Adam(learning_rate=0.001) 
  model1.compile(optimizer=opt, loss='sparse_categorical_crossentropy', metrics=['accuracy'])


  model1.load_weights('modelfinal.h5')
  while image_file_buffer:
      img = Image.open(image_file_buffer)
      st.image(img, width=800)
      img_arr = Image.open(image_file_buffer)
      newsize = (224,224)
      img_arr = img_arr.resize(newsize)
      data = np.asarray(img_arr)
      data = data.reshape(1, 224,224,3)
      prediction1 = model1.predict(data)
      data1 = np.argmax(prediction1)
      data1=int(data1)
    
      if(data1 == 0): 
        pre = "AMBULANCE"		
      elif(data1 == 1):
        pre = "BICYCLE"
      elif(data1 == 2):
        pre = "BUS"
      elif(data1 == 3):
        pre = "CAR"
      elif(data1 == 4):
        pre = "CART"
      elif(data1 == 5):
        pre = "HELICOPTER"
      elif(data1 == 6):
        pre = "MOTORCYCLE"
      elif(data1 == 7):
        pre = "TRUCK"
      else:
        pre = "NONE"
 
  
      st.subheader(pre)
      break






def video_count_vehicle():
  video_file1_buffer = st.sidebar.file_uploader("Upload a video", type=[ "mp4", "mov",'avi','asf', 'm4v' ])
  tfflie1 = tempfile.NamedTemporaryFile(delete=False)




  #All these classes will be counted as 'vehicles'
  list_of_vehicles = ["bicycle","car","motorbike","bus","truck", "train"]
  # Setting the threshold for the number of frames to search a vehicle for
  FRAMES_BEFORE_CURRENT = 10  
  inputWidth, inputHeight = 416, 416

  #Parse command line arguments and extract the values required
  #LABELS, weightsPath, configPath, inputVideoPath, outputVideoPath,\
  #	preDefinedConfidence, preDefinedThreshold, USE_GPU= parseCommandLineArguments()
  configPath= "yolov3.cfg"
  weightsPath= "yolov3.weights"
  labelspath= "coco.names"
  LABELS= open(labelspath).read().strip().split("\n")

  while video_file1_buffer:
    tfflie1.write(video_file1_buffer.read())
    #inputVideoPath = video_file1_buffer
    outputVideoPath = "out.mp4"
    # Initialize a list of colors to represent each possible class label
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
      dtype="uint8")
    # PURPOSE: Displays the vehicle count on the top-left corner of the frame
    # PARAMETERS: Frame on which the count is displayed, the count number of vehicles 
    # RETURN: N/A
    def displayVehicleCount(frame, vehicle_count):
      cv2.putText(
        frame, #Image
        'Detected Vehicles: ' + str(vehicle_count), #Label
        (20, 20), #Position
        cv2.FONT_HERSHEY_SIMPLEX, #Font
        0.8, #Size
        (0, 0xFF, 0), #Color
        2, #Thickness
        cv2.FONT_HERSHEY_COMPLEX_SMALL,
        )

    # PURPOSE: Determining if the box-mid point cross the line or are within the range of 5 units
    # from the line
    # PARAMETERS: X Mid-Point of the box, Y mid-point of the box, Coordinates of the line 
    # RETURN: 
    # - True if the midpoint of the box overlaps with the line within a threshold of 5 units 
    # - False if the midpoint of the box lies outside the line and threshold
    def boxAndLineOverlap(x_mid_point, y_mid_point, line_coordinates):
      x1_line, y1_line, x2_line, y2_line = line_coordinates #Unpacking

      if (x_mid_point >= x1_line and x_mid_point <= x2_line+5) and\
        (y_mid_point >= y1_line and y_mid_point <= y2_line+5):
        return True
      return False

    # PURPOSE: Displaying the FPS of the detected video
    # PARAMETERS: Start time of the frame, number of frames within the same second
    # RETURN: New start time, new number of frames 
    def displayFPS(start_time, num_frames):
      current_time = int(time.time())
      if(current_time > start_time):
        os.system('cls') # Equivalent of CTRL+L on the terminal
        print("FPS:", num_frames)
        num_frames = 0
        start_time = current_time
      return start_time, num_frames

    # PURPOSE: Draw all the detection boxes with a green dot at the center
    # RETURN: N/A
    def drawDetectionBoxes(idxs, boxes, classIDs, confidences, frame):
      # ensure at least one detection exists
      if len(idxs) > 0:
        # loop over the indices we are keeping
        for i in idxs.flatten():
          # extract the bounding box coordinates
          (x, y) = (boxes[i][0], boxes[i][1])
          (w, h) = (boxes[i][2], boxes[i][3])

          # draw a bounding box rectangle and label on the frame
          color = [int(c) for c in COLORS[classIDs[i]]]
          cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
          text = "{}: {:.4f}".format(LABELS[classIDs[i]],
            confidences[i])
          cv2.putText(frame, text, (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
          #Draw a green dot in the middle of the box
          cv2.circle(frame, (x + (w//2), y+ (h//2)), 2, (0, 0xFF, 0), thickness=2)

    # PURPOSE: Initializing the video writer with the output video path and the same number
    # of fps, width and height as the source video 
    # PARAMETERS: Width of the source video, Height of the source video, the video stream
    # RETURN: The initialized video writer
    def initializeVideoWriter(video_width, video_height, videoStream):
      # Getting the fps of the source video
      sourceVideofps = videoStream.get(cv2.CAP_PROP_FPS)
      # initialize our video writer
      fourcc = cv2.VideoWriter_fourcc(*"MJPG")
      return cv2.VideoWriter(outputVideoPath, fourcc, sourceVideofps,
        (video_width, video_height), True)

    # PURPOSE: Identifying if the current box was present in the previous frames
    # PARAMETERS: All the vehicular detections of the previous frames, 
    #			the coordinates of the box of previous detections
    # RETURN: True if the box was current box was present in the previous frames;
    #		  False if the box was not present in the previous frames
    def boxInPreviousFrames(previous_frame_detections, current_box, current_detections):
      centerX, centerY, width, height = current_box
      dist = np.inf #Initializing the minimum distance
      # Iterating through all the k-dimensional trees
      for i in range(FRAMES_BEFORE_CURRENT):
        coordinate_list = list(previous_frame_detections[i].keys())
        if len(coordinate_list) == 0: # When there are no detections in the previous frame
          continue
        # Finding the distance to the closest point and the index
        temp_dist, index = spatial.KDTree(coordinate_list).query([(centerX, centerY)])
        if (temp_dist < dist):
          dist = temp_dist
          frame_num = i
          coord = coordinate_list[index[0]]

      if (dist > (max(width, height)/2)):
        return False

      # Keeping the vehicle ID constant
      current_detections[(centerX, centerY)] = previous_frame_detections[frame_num][coord]
      return True

    def count_vehicles(idxs, boxes, classIDs, vehicle_count, previous_frame_detections, frame):
      current_detections = {}
      # ensure at least one detection exists
      if len(idxs) > 0:
        # loop over the indices we are keeping
        for i in idxs.flatten():
          # extract the bounding box coordinates
          (x, y) = (boxes[i][0], boxes[i][1])
          (w, h) = (boxes[i][2], boxes[i][3])
          
          centerX = x + (w//2)
          centerY = y+ (h//2)

          # When the detection is in the list of vehicles, AND
          # it crosses the line AND
          # the ID of the detection is not present in the vehicles
          if (LABELS[classIDs[i]] in list_of_vehicles):
            current_detections[(centerX, centerY)] = vehicle_count 
            if (not boxInPreviousFrames(previous_frame_detections, (centerX, centerY, w, h), current_detections)):
              vehicle_count += 1
              # vehicle_crossed_line_flag += True
            # else: #ID assigning
              #Add the current detection mid-point of box to the list of detected items
            # Get the ID corresponding to the current detection

            ID = current_detections.get((centerX, centerY))
            # If there are two detections having the same ID due to being too close, 
            # then assign a new ID to current detection.
            if (list(current_detections.values()).count(ID) > 1):
              current_detections[(centerX, centerY)] = vehicle_count
              vehicle_count += 1 

            #Display the ID at the center of the box
            cv2.putText(frame, str(ID), (centerX, centerY),\
              cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0,0,255], 2)

      return vehicle_count, current_detections

    # load our YOLO object detector trained on COCO dataset (80 classes)
    # and determine only the *output* layer names that we need from YOLO
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

    #Using GPU if flag is passed

    #if USE_GPU:
      #net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
      #net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    # initialize the video stream, pointer to output video file, and
    # frame dimensions
    videoStream = cv2.VideoCapture(tfflie1.name)
    video_width = int(videoStream.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(videoStream.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Specifying coordinates for a default line 
    x1_line = 0
    y1_line = video_height//2
    x2_line = video_width
    y2_line = video_height//2

    #Initialization
    previous_frame_detections = [{(0,0):0} for i in range(FRAMES_BEFORE_CURRENT)]
    # previous_frame_detections = [spatial.KDTree([(0,0)])]*FRAMES_BEFORE_CURRENT # Initializing all trees
    num_frames, vehicle_count = 0, 0
    writer = initializeVideoWriter(video_width, video_height, videoStream)
    start_time = int(time.time())
    # loop over frames from the video file stream
    while True:
      print("================NEW FRAME================")
      num_frames+= 1
      print("FRAME:\t", num_frames)
      # Initialization for each iteration
      boxes, confidences, classIDs = [], [], [] 
      vehicle_crossed_line_flag = False 

      #Calculating fps each second
      start_time, num_frames = displayFPS(start_time, num_frames)
      # read the next frame from the file
      (grabbed, frame) = videoStream.read()

      # if the frame was not grabbed, then we have reached the end of the stream
      if not grabbed:
        break

      # construct a blob from the input frame and then perform a forward
      # pass of the YOLO object detector, giving us our bounding boxes
      # and associated probabilities
      blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (inputWidth, inputHeight),
        swapRB=True, crop=False)
      net.setInput(blob)
      start = time.time()
      layerOutputs = net.forward(ln)
      end = time.time()

      # loop over each of the layer outputs
      for output in layerOutputs:
        # loop over each of the detections
        for i, detection in enumerate(output):
          # extract the class ID and confidence (i.e., probability)
          # of the current object detection
          scores = detection[5:]
          classID = np.argmax(scores)
          confidence = scores[classID]
          preDefinedConfidence=0.5
          preDefinedThreshold=0.3
          # filter out weak predictions by ensuring the detected
          # probability is greater than the minimum probability
          if confidence > preDefinedConfidence:
            # scale the bounding box coordinates back relative to
            # the size of the image, keeping in mind that YOLO
            # actually returns the center (x, y)-coordinates of
            # the bounding box followed by the boxes' width and
            # height
            box = detection[0:4] * np.array([video_width, video_height, video_width, video_height])
            (centerX, centerY, width, height) = box.astype("int")

            # use the center (x, y)-coordinates to derive the top
            # and and left corner of the bounding box
            x = int(centerX - (width / 2))
            y = int(centerY - (height / 2))
                                
            #Printing the info of the detection
            #print('\nName:\t', LABELS[classID],
              #'\t|\tBOX:\t', x,y)

            # update our list of bounding box coordinates,
            # confidences, and class IDs
            boxes.append([x, y, int(width), int(height)])
            confidences.append(float(confidence))
            classIDs.append(classID)

      # # Changing line color to green if a vehicle in the frame has crossed the line 
      # if vehicle_crossed_line_flag:
      # 	cv2.line(frame, (x1_line, y1_line), (x2_line, y2_line), (0, 0xFF, 0), 2)
      # # Changing line color to red if a vehicle in the frame has not crossed the line 
      # else:
      # 	cv2.line(frame, (x1_line, y1_line), (x2_line, y2_line), (0, 0, 0xFF), 2)

      # apply non-maxima suppression to suppress weak, overlapping
      # bounding boxes
      idxs = cv2.dnn.NMSBoxes(boxes, confidences, preDefinedConfidence,
        preDefinedThreshold)

      # Draw detection box 
      drawDetectionBoxes(idxs, boxes, classIDs, confidences, frame)

      vehicle_count, current_detections = count_vehicles(idxs, boxes, classIDs, vehicle_count, previous_frame_detections, frame)

      # Display Vehicle Count if a vehicle has passed the line 
      displayVehicleCount(frame, vehicle_count)

        # write the output frame to disk
      writer.write(frame)

      cv2.imshow('Frame', frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break	
      
      # Updating with the current frame detections
      previous_frame_detections.pop(0) #Removing the first frame from the list
      # previous_frame_detections.append(spatial.KDTree(current_detections))
      previous_frame_detections.append(current_detections)

    # release the file pointers
    print("[INFO] cleaning up...")
    writer.release()
    videoStream.release()
















if __name__ == '__main__':
  select_type()