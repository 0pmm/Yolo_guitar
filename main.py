from ultralytics import YOLO
from draw_boxes import draw
from calc_axis import calc_axis
from collect_data import collect
import cv2

model = YOLO("runs/detect/train/weights/best.onnx")
cap = cv2.VideoCapture(0)
allowed_classes = None

while True:
    # ret, frame = cap.read()
    # if not ret: 
    #     print("Erro, nenhum vídeo identificado")
    #     break

    frame = cv2.imread("violao.jpg")

    results = model(frame)
    data = collect(results)
    axis = calc_axis(frame, data['nut'], data['frets'])
    data.update(axis)


    frame_draw = draw(data, frame, allowed_classes)  

    cv2.imshow("Sonorum", frame_draw)
    key = cv2.waitKey(1) &  0xFF
    if key == ord('q'):
        print("Aplicativo finalizado")
        break
    # TUDO
    elif key == ord('1'):
        allowed_classes = ['frets','frets_box','nut','axis']
    # APENAS TRASTES
    elif key == ord('2'):
        allowed_classes = ['frets','frets_box','projections','mean_frets']
    # APENAS PROJEÇÃO
    elif key == ord('3'):
        allowed_classes = ['projections']
    # PROJEÇÃO COMPARADO A CENTROIDES
    elif key == ord('4'):
        allowed_classes = ['projections','frets']
    elif key == ord('5'):
        allowed_classes = None

cap.release
cv2.destroyAllWindows()
