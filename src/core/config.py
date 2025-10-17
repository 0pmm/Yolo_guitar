import cv2

class Config:
    MODEL_PATH = "runs/detect/train/weights/best.onnx"
    IMAGE_PATH = "src/data/violao.jpg"
    WEBCAM_ID = 0

    VIEW_MODE = {
        '0': None, 
        '1': ['pt_projected_final', 'frets_box', 'nut', 'axis'],
        '2': ['projections', 'expected', 'axis']
    }

    MAX_FRETS = 20
    RMSE_THRESHOLD = 10.0
    SMOOTHING_ALFA = 0.6