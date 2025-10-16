import cv2
import numpy as np
from ultralytics import YOLO
from data.dados import chords
from modules.draw_boxes import draw, draw_chord
from modules.calc_axis import calc_axis
from modules.collect_data import collect
from modules.predict_frets import predict_frets_positions, compare_projected_predicted
from modules.grid_formation import grid_formalization

# =========================
# MODELO YOLO E CONFIG
# =========================
model = YOLO("runs/detect/train/weights/best.onnx")
cap = cv2.VideoCapture(0)
allowed_classes = None

# ACORDES
A_MAJOR = chords["A_MAJOR"]
B_MAJOR = chords["B_MAJOR"]
C_MAJOR = chords["C_MAJOR"]
D_MAJOR = chords["D_MAJOR"]
E_MAJOR = chords["E_MAJOR"]
F_MAJOR = chords["F_MAJOR"]
G_MAJOR = chords["G_MAJOR"]

# =========================
# FRAME PLACEHOLDER
# =========================
frame_placeholder = cv2.imread("violao.jpg")
if frame_placeholder is None:
    print("Erro: não foi possível carregar 'violao.jpg' como placeholder.")
    exit()

frame = frame_placeholder.copy()  # primeiro frame seguro

# =========================
# LOOP PRINCIPAL
# =========================
while True:
    ret, webcam_frame = cap.read()
    if ret:
        frame = webcam_frame  # usa a webcam se disponível
    else:
        frame = frame_placeholder.copy()  # caso contrário, mantém placeholder

    # ======== DETECÇÃO YOLO ========
    results = model.predict(source=frame, verbose=False)
    data = collect(results)

    # ======== PROCESSAMENTO ========
    axis = calc_axis(frame, data['nut'], data['frets'], data['neck_box'])
    data.update(axis)

    expected = predict_frets_positions(data, 20)
    data.update(expected)

    teste = compare_projected_predicted(data)
    data.update(teste)

    try:
        test2 = grid_formalization(
            data['neck_box'],
            data['nut'][0][:2],
            data['axis_unit'],
            data['pt_projected_final']
        )
        data.update(test2)
    except Exception as e:
        data['casas'] = {}

    # ======== DESENHO ========
    # frame_draw2 = draw(data, frame, allowed_classes)
    frame_draw = draw_chord(frame, data['casas'], E_MAJOR)

    # cv2.imshow("Sonorum app (CAIXAS)", frame_draw2)
    cv2.imshow("Sonorum app (ACORDE)", frame_draw)

    # ======== CONTROLE DE TECLAS ========
    key = cv2.waitKey(1) & 0xFF
    match key:
        case k if key == ord('q'):
            print("Aplicativo finalizado")
            break
        case k if key == ord('0'):
            allowed_classes = None
        case k if key == ord('1'):
            allowed_classes = ['pt_projected_final', 'frets_box', 'nut', 'axis']
        case k if key == ord('2'):
            allowed_classes = ['projections', 'expected', 'axis']

cap.release()
cv2.destroyAllWindows()
