from ultralytics import YOLO
from modules.draw_boxes import draw
from modules.calc_axis import calc_axis
from modules.collect_data import collect
from modules.predict_frets import predict_frets_positions, compare_projected_predicted
import cv2
import ThreadPoolExecutorPlus


model = YOLO("runs/detect/train/weights/best.onnx")
cap = cv2.VideoCapture(0)
allowed_classes = None

while True:
        ret, frame = cap.read()
        if not ret: 
            print("Erro, nenhum vídeo identificado")
            break
    
  
        
        # frame = cv2.imread("violao.jpg")

        results = model.predict(source=frame,verbose=False)

        data = collect(results,)

        axis = calc_axis(frame, data['nut'], data['frets'], data['neck_box'])

        expected = predict_frets_positions(axis,20)

        data.update(axis)
        data.update(expected)
        
        teste = compare_projected_predicted(data)

        data.update(teste)

        frame_draw = draw(data, frame, allowed_classes)  

        cv2.imshow("Sonorum", frame_draw)
        key = cv2.waitKey(1) &  0xFF
        match key:
            case k if key == ord('q'):
                print("Aplicativo finalizado")
                break
            case k if key == ord('0'): # TUDO
                allowed_classes = None
            case k if key == ord('1'): # APENAS TRASTES
                allowed_classes = ['projections','frets_box','nut','expected']
            case k if key == ord('2'): # APENAS CENTRÓIDES
                allowed_classes = ['projections','nut','axis']
            case k if key == ord('3'): #APENAS PREDIÇÃO
                allowed_classes = ['expected']
            case k if key == ord('4'): # COMPARAÇÃO PROJEÇÃO x PREDIÇÃO
                allowed_classes = ['pt_projected_final']


cap.release
cv2.destroyAllWindows()