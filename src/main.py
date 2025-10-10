from ultralytics import YOLO
from modules.draw_boxes import draw, draw_chord
from modules.calc_axis import calc_axis
from modules.collect_data import collect
from modules.predict_frets import predict_frets_positions, compare_projected_predicted
from modules.grid_formation import grid_formalization
import cv2
import ThreadPoolExecutorPlus


model = YOLO("runs/detect/train/weights/best.onnx")
cap = cv2.VideoCapture(0)
allowed_classes = None

E_MAJOR = {
    6: 0,
    5: 18,
    4: 18,
    3: 18,
    2: 0,
    1: 0
}
A_MAJOR = {
    6: 0,
    5: 0,
    4: 12,
    3: 12,
    2: 12,
    1: 0
}

while True:
        # ret, frame = cap.read()
        # if not ret: 
        #     print("Erro, nenhum vídeo identificado")
        #     break
    
        
        frame = cv2.imread("violao.jpg")

        results = model.predict(source=frame,verbose=False)

        data = collect(results)

        axis = calc_axis(frame, data['nut'], data['frets'], data['neck_box'])

        expected = predict_frets_positions(axis,20)

        data.update(axis)
        data.update(expected)
        
        teste = compare_projected_predicted(data)

        data.update(teste)

        test2 = grid_formalization(data['neck_box'], data['nut'][0][:2], data['axis_unit'], data['pt_projected_final'])

        data.update(test2)
    
        frame_draw2 = draw(data, frame, allowed_classes)  
        frame_draw = draw_chord(frame, data['casas'], E_MAJOR)

        cv2.imshow("Sonorum app", frame_draw)
        cv2.imshow("Sonorum app", frame_draw2)
        key = cv2.waitKey(1) &  0xFF
        match key:
            case k if key == ord('q'):
                print("Aplicativo finalizado")
                break
            case k if key == ord('0'): # TUDO
                allowed_classes = None
            case k if key == ord('1'): # APENAS TRASTES
                allowed_classes = ['pt_projected_final','frets_box','nut','axis']
            case k if key == ord('2'): # COMPARAÇÃO PROJEÇÂO X PREDIÇÃO
                allowed_classes = ['projections','expected','axis']


cap.release
cv2.destroyAllWindows()