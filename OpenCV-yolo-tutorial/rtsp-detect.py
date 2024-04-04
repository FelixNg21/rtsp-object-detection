#############################################
# Object detection via RTSP - YOLO - OpenCV
# Author : Frank Schmitz   (Dec 11, 2018)
# Website : https://www.github.com/zishor
############################################

# python rtsp-detect.py --input rtsp://localhost:8554/driveway --framestart 10 --framelimit 50 --config cfg/yolov3.cfg --weights yolov3.weights --classes cfg/yolov3.txt

import os
import os.path
import cv2
import numpy as np
import imageio_ffmpeg as imageio
import datetime
import arguments


def get_output_layers(nnet):
    layer_names = nnet.getLayerNames()
    output_layers = [layer_names[i - 1] for i in nnet.getUnconnectedOutLayers()]
    return output_layers


def save_bounded_image(image, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    dirname = os.path.join(args.outputdir, label, datetime.datetime.now().strftime('%Y-%m-%d'))
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    image_filename = label + '_' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f') + '_conf' + "{:.2f}".format(
        confidence) + '.jpg'
    print('Saving bounding box:' + image_filename)
    roi = image[y:y_plus_h, x:x_plus_w]
    if roi.any():
        if not args.invertcolor:
            roi = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(dirname, image_filename), roi)


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    label = "{}: {:.4f}".format(label, confidence)
    color = COLORS[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 3)
    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def detect(image):
    width = image.shape[1]
    height = image.shape[0]
    blob = cv2.dnn.blobFromImage(image, 1.0 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)

    outs = net.forward(get_output_layers(net))
    outs = np.vstack(outs)

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    for output in outs:
        scores = output[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > conf_threshold:
            x, y, w, h = output[:4] * np.array([width, height, width, height])
            p0 = int(x - w // 2), int(y - h // 2)
            boxes.append([*p0, int(w), int(h)])
            confidences.append(float(confidence))
            class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    if len(indices) > 0:
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            if args.saveimages:
                save_bounded_image(image.copy(), class_ids[i], confidences[i], round(x), round(y), round(x + w),
                                   round(y + h))
            draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))

    if args.invertcolor:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image


def processvideo(file):
    cap = cv2.VideoCapture(file)

    writer = imageio.write_frames(args.outputdir + args.outputfile, (int(cap.get(3)), int(cap.get(4))))
    writer.send(None)
    frame_counter = 0
    while cap.isOpened():
        frame_counter = frame_counter + 1
        ret, frame = cap.read()
        print(f'Detecting objects in frame {str(frame_counter)}')
        if not ret:
            break
        if frame is not None:
            image = detect(frame)
            writer.send(image)
        else:
            print(f'Frame error in frame {str(frame_counter)}')
    cap.release()
    writer.close()


if __name__ == "__main__":
    args = arguments.arg_parse()

    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

    # get the yolov3 network
    net = cv2.dnn.readNetFromDarknet(args.config, args.weights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    if args.input.startswith('rtsp'):
        cap = cv2.VideoCapture(args.input)
        writer = imageio.write_frames(args.outputdir + args.outputfile, (int(cap.get(3)), int(cap.get(4))))
        writer.send(None)
        frame_counter = 0
        while True:
            if args.framelimit > 0 and frame_counter > int(args.framestart) + int(args.framelimit):
                writer.close()
                break

            if frame_counter % int(args.fpsthrottle) == 0:
                ret, frame = cap.read()
                if ret and frame_counter >= int(args.framestart):
                    print(f'Detecting objects in frame {str(frame_counter)}')
                    frame = detect(frame)
                    if int(args.framelimit) > 0:
                        writer.send(frame)
                else:
                    print(f'Skipping frame {str(frame_counter)}')
            else:
                print(f'FPS throttling. Skipping frame {str(frame_counter)}')
            frame_counter = frame_counter + 1

    elif os.path.isdir(args.input):
        for dirpath, dirnames, filenames in os.walk(args.input):
            for filename in [f for f in filenames if f.endswith(".mp4")]:
                print(f'Processing video {os.path.join(dirpath, filename)}')
                processvideo(os.path.join(dirpath, filename))
    else:
        processvideo(os.path.join(args.input))
