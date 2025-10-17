import cv2
import numpy as np # Adicionado explicitamente para manipulação de arrays
from ultralytics import YOLO
from core.config import Config
from core.state_manager import StateManager
from services.detection_pipeline import DetectionPipeline
from modules.draw_boxes import draw, draw_chord
from data.chords import chords 


def resize_to_fit_window(frame, target_width, target_height):

    h, w = frame.shape[:2]

    scale_x = target_width / w
    scale_y = target_height / h
    scale = max(scale_x, scale_y) 
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cv2.resize(frame, (new_w, new_h))

    start_x = max(0, (new_w - target_width) // 2)
    start_y = max(0, (new_h - target_height) // 2)
    cropped = resized[start_y:start_y + target_height, start_x:start_x + target_width]
    
    return cropped

def main():
    model = YOLO(Config.MODEL_PATH)
    state = StateManager()
    pipeline = DetectionPipeline(model, state)

    cap = cv2.VideoCapture(Config.WEBCAM_ID)
    placeholder = cv2.imread(Config.IMAGE_PATH)

    current_frame = placeholder.copy() if placeholder is not None else None
    allowed_classes = None
    current_chord = chords["A_MAJOR"]

    if current_frame is None:
        print("Placeholder nao foi carregado")
        return

    # --- INÍCIO DA LÓGICA DE OVERLAY DA IMAGEM ---
    
    # 1. Constrói o caminho da imagem (ex: data/images/A_MAJOR.png)
    chord_name = current_chord['name'].upper() # Assumindo que current_chord tem a chave 'name'
    CHORD_IMAGE_PATH = f"./src/data/images/{chord_name}.png" 

    # 2. Carrega a imagem com canal alpha (transparência)
    corner_img = cv2.imread(CHORD_IMAGE_PATH, cv2.IMREAD_UNCHANGED)

    # 3. Define o tamanho e redimensiona
    CORNER_W, CORNER_H = 200, 150 # Tamanho fixo para o canto
    
    if corner_img is None:
        print(f"ERRO: Nao foi possivel carregar a imagem de overlay: {CHORD_IMAGE_PATH}")
        corner_img_resized = None
    else:
        # Redimensiona a imagem uma única vez
        corner_img_resized = cv2.resize(corner_img, (CORNER_W, CORNER_H))
    
    # Define a posição (Canto Superior Esquerdo com margem de 10px)
    CORNER_POS_X, CORNER_POS_Y = 10, 10
    # --- FIM DA LÓGICA DE OVERLAY DA IMAGEM ---

    cv2.namedWindow("Chord", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Chord", 1000, 700)


    while True:
        ret, webcam_frame = cap.read()
        frame = webcam_frame if ret else current_frame.copy()

        data = pipeline.process_frame(frame)

        # frame_detection = draw(data, frame.copy(), allowed_classes)
        
        if data.get('casas') and 1 in data['casas']:
            frame_chord = draw_chord(frame.copy(), data['casas'], current_chord)
        else:
            frame_chord = frame.copy()
            cv2.putText(frame_chord, "Waiting Detection...", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # --- APLICAÇÃO DA SOBREPOSIÇÃO DENTRO DO LOOP ---
        if corner_img_resized is not None:
            
            # Pega as dimensões da imagem redimensionada
            oh, ow = corner_img_resized.shape[:2]

            # Seleciona a Região de Interesse (ROI) no frame principal
            roi = frame_chord[CORNER_POS_Y : CORNER_POS_Y + oh, 
                              CORNER_POS_X : CORNER_POS_X + ow]

            # Verifica se o ROI tem o mesmo tamanho que a imagem de overlay (prevenção de erro)
            if roi.shape[:2] == (oh, ow):
                # Verifica se a imagem tem canal Alpha (transparência - 4 canais)
                if corner_img_resized.shape[2] == 4:
                    # PNG com transparência: faz a mistura (blending)
                    bgr = corner_img_resized[:, :, :3]
                    alpha = corner_img_resized[:, :, 3].astype(float) / 255.0  # Normaliza Alpha
                    
                    alpha_inv = 1.0 - alpha
                    
                    # Mistura o plano de fundo (ROI) e o primeiro plano (bgr)
                    for c in range(0, 3):
                        roi[:, :, c] = (roi[:, :, c] * alpha_inv) + (bgr[:, :, c] * alpha)
                else:
                    # JPG ou PNG sem transparência (3 canais): atribuição direta
                    roi[:, :] = corner_img_resized[:, :, :3]
        # ----------------------------------------------------
        
        try:
            window_rect = cv2.getWindowImageRect("Chord")
            if window_rect[2] > 0 and window_rect[3] > 0:
                win_w, win_h = window_rect[2], window_rect[3]
                frame_resized = cv2.resize(frame_chord, (win_w, win_h))
                cv2.imshow("Chord", frame_resized)
            else:
                cv2.imshow("Chord", frame_chord)
        except:
            cv2.imshow("Chord", frame_chord)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif chr(key) in Config.VIEW_MODE: 
            allowed_classes = Config.VIEW_MODE[chr(key)]
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()