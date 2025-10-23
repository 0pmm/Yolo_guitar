import cv2
from ultralytics import YOLO
from core.config import Config
from core.state_manager import StateManager
from services.detection_pipeline import DetectionPipeline
from modules.draw_boxes import draw, draw_chord
from data.chords import chords
from modules.chord_matcher import AudioEventProcessor

A_MAJOR = "src/data/images/A_MAJOR.png"
B_MAJOR = "src/data/images/B_MAJOR.png"
C_MAJOR = "src/data/images/C_MAJOR.png"
D_MAJOR = "src/data/images/D_MAJOR.png"
E_MAJOR = "src/data/images/E_MAJOR.png"
F_MAJOR = "src/data/images/F_MAJOR.png"
G_MAJOR = "src/data/images/G_MAJOR.png"

CHORD_IMAGES = {
    "A_MAJOR": A_MAJOR,
    "B_MAJOR": B_MAJOR,
    "C_MAJOR": C_MAJOR,
    "D_MAJOR": D_MAJOR,
    "E_MAJOR": E_MAJOR,
    "F_MAJOR": F_MAJOR,
    "G_MAJOR": G_MAJOR,
}

WEBCAM_WIDTH, WEBCAM_HEIGHT = 640, 480
CHORD_WIDTH, CHORD_HEIGHT = 300, 400


def resize_image(image, width, height):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def main():
    model = YOLO(Config.MODEL_PATH)
    state = StateManager()
    pipeline = DetectionPipeline(model, state)
    processor = AudioEventProcessor()  # processador de áudio

    cap = cv2.VideoCapture(Config.WEBCAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT)

    current_chord_name = "A_MAJOR"
    current_chord = chords[current_chord_name]
    chord_img = resize_image(cv2.imread(CHORD_IMAGES[current_chord_name]), CHORD_WIDTH, CHORD_HEIGHT)

    detection_text = "Aguardando som..."
    detection_color = (180, 180, 180)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        data = pipeline.process_frame(frame)
        display = draw_chord(frame.copy(), data.get('casas', []), current_chord)

        # --- PROCESSAMENTO DE ÁUDIO (DEBUG) ---
        # Aqui simulamos a captura de áudio real em loop
        # Caso você use WebRTC ou sounddevice, substitua audio_buffer por chunks reais
        audio_result = None  # processará se houver um chunk real
        # Exemplo: audio_result = processor.process_audio_chunk(chunk)

        # Atualiza texto de debug com base no resultado
        if audio_result is not None:
            if audio_result["status"] == "OK":
                detected_chord = audio_result["acorde"]
                similarity = audio_result["similarity"]
                if detected_chord == current_chord_name:
                    detection_text = f"{detected_chord} detectado ({similarity*100:.1f}%)"
                    detection_color = (0, 255, 0)
                else:
                    detection_text = f"Som ≠ {current_chord_name} ({similarity*100:.1f}%)"
                    detection_color = (0, 0, 255)
                print(f"[DEBUG] Acorde detectado: {detected_chord} | Similaridade: {similarity:.3f}")
            else:
                detection_text = "Nenhum acorde reconhecido"
                detection_color = (0, 0, 255)
                print("[DEBUG] Nenhum acorde reconhecido")
        else:
            detection_text = "Detectando som..."
            detection_color = (180, 180, 180)

        cv2.putText(display, detection_text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, detection_color, 2, cv2.LINE_AA)

        # --- GARANTE MESMO TIPO E ALTURA PARA CONCAT ---
        if len(display.shape) == 2:
            display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
        if len(chord_img.shape) == 2:
            chord_img = cv2.cvtColor(chord_img, cv2.COLOR_GRAY2BGR)
        if display.shape[0] != chord_img.shape[0]:
            chord_img = cv2.resize(chord_img, (chord_img.shape[1], display.shape[0]))
        if display.dtype != chord_img.dtype:
            chord_img = chord_img.astype(display.dtype)

        combined = cv2.hconcat([display, chord_img])
        cv2.imshow("Chord Detector", combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif chr(key) in Config.VIEW_MODE:
            allowed_classes = Config.VIEW_MODE[chr(key)]
        elif key in [ord('a'), ord('b'), ord('c'), ord('d'), ord('e'), ord('f'), ord('g')]:
            chord_map = {
                ord('a'): "A_MAJOR",
                ord('b'): "B_MAJOR",
                ord('c'): "C_MAJOR",
                ord('d'): "D_MAJOR",
                ord('e'): "E_MAJOR",
                ord('f'): "F_MAJOR",
                ord('g'): "G_MAJOR",
            }
            current_chord_name = chord_map[key]
            current_chord = chords[current_chord_name]
            chord_img = resize_image(cv2.imread(CHORD_IMAGES[current_chord_name]), CHORD_WIDTH, CHORD_HEIGHT)
            detection_text = "Aguardando som..."
            detection_color = (180, 180, 180)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
