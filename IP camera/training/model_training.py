from ultralytics import YOLO
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# import torch
# torch.cuda.set_device(0)
def train():
    model = YOLO("yolov8s.pt")
    results = model.train(data="coco.yaml", device="0")

def detect():
    model = YOLO("../runs/detect/train/weights/best.pt")
    model.predict("test.jpg")

if __name__ == "__main__":
    # train()
    detect()
