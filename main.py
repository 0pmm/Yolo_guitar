"""
Projeto Yolo_guitar - Sistema de Detecção de Guitarra com IA
===========================================================
Arquivo principal que coordena todo o sistema de detecção.
Integra modelo YOLO, processamento de dados e visualização.

Controles:
- Q: Sair
- 1: Mostrar trastes + pestana  
- 2: Mostrar apenas trastes
- 3: Mostrar apenas pestana
- 4: Mostrar tudo
"""

# === IMPORTAÇÕES ===
from ultralytics import YOLO          # Framework YOLO para detecção de objetos
from draw_boxes import draw           # Módulo próprio para desenhar detecções
from collect_data import collect      # Módulo próprio para organizar dados
import cv2                           # OpenCV para processamento de imagem

# === INICIALIZAÇÃO DO SISTEMA ===
# Carrega o modelo YOLO treinado especificamente para guitarra
model = YOLO("runs/detect/train/weights/best.pt")

# Configura captura de vídeo da webcam (índice 0 = primeira câmera)
cap = cv2.VideoCapture(0)

# Inicializa filtro de classes (None = mostra todas)
allowed_classes = None

# === LOOP PRINCIPAL DO PROGRAMA ===
while True:
    # --- CAPTURA DE FRAME (WEBCAM) - ATUALMENTE COMENTADO ---
    # ret, frame = cap.read()              # Captura frame da webcam
    # if not ret:                          # Se falhou ao capturar
    #     print("Erro, nenhum vídeo identificado")
    #     break                            # Encerra o programa
    
    # --- CARREGAMENTO DE IMAGEM ESTÁTICA (MODO ATUAL) ---
    frame = cv2.imread("violao.jpg")      # Carrega imagem fixa para teste
    
    # --- DETECÇÃO COM YOLO ---
    results = model(frame)                # Executa detecção na imagem
    
    # --- ORGANIZAÇÃO DOS DADOS ---
    data = collect(results)               # Organiza detecções por tipo
    
    # --- EXIBIÇÃO DOS RESULTADOS NO CONSOLE ---
    print("Trastes (x,y,conf): ", data['frets'])   # Lista trastes detectados
    print("Pestana (x,y,conf): ", data['nut'])     # Lista pestana detectada
    print("Braço (x,y,conf): ", data['neck'])      # Lista braço detectado
    
    # --- VISUALIZAÇÃO ---
    frame_draw = draw(data, frame, allowed_classes)  # Desenha detecções na imagem
    
    # --- INTERFACE COM USUÁRIO ---
    cv2.imshow("Sonorum", frame_draw)     # Mostra imagem em janela
    key = cv2.waitKey(1) & 0xFF          # Captura tecla pressionada (1ms timeout)
    
    # --- CONTROLES DO TECLADO ---
    if key == ord('q'):                   # Se pressionou 'Q'
        print("Aplicativo finalizado")
        break                             # Sai do loop (encerra programa)
    elif key == ord('1'):                 # Se pressionou '1'
        allowed_classes = ['fret','nut']  # Mostra apenas trastes e pestana
    elif key == ord('2'):                 # Se pressionou '2'
        allowed_classes = ['fret']        # Mostra apenas trastes
    elif key == ord('3'):                 # Se pressionou '3'
        allowed_classes = ['nut']         # Mostra apenas pestana
    elif key == ord('4'):                 # Se pressionou '4'
        allowed_classes = None            # Mostra tudo (remove filtros)

# === LIMPEZA DE RECURSOS ===
cap.release()                           # Libera recursos da webcam (corrigido)
cv2.destroyAllWindows()                 # Fecha todas as janelas do OpenCV
