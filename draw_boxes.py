"""
Módulo draw_boxes.py - Visualização das Detecções
=================================================
Desenha círculos coloridos nas posições detectadas pelo YOLO
para visualizar onde estão os trastes, pestana e braço da guitarra.

Esquema de cores:
- Verde (0,255,0): Trastes (frets)
- Azul (255,0,0): Pestana (nut) 
- Vermelho (0,0,255): Braço (neck)

Nota: OpenCV usa formato BGR (Blue-Green-Red)
"""

import cv2  # OpenCV para desenho de formas geométricas

def draw(data, frame, allowed_classes):
    """
    Desenha visualizações das detecções na imagem.
    
    Args:
        data: Dicionário com detecções organizadas (do collect_data.py)
        frame: Imagem onde desenhar (será modificada)
        allowed_classes: Lista de classes permitidas ou None (mostra tudo)
        
    Returns:
        frame: Imagem modificada com os desenhos
    """
    
    # === DESENHO DOS TRASTES (VERDE) ===
    # Verifica se deve desenhar trastes baseado no filtro
    if (allowed_classes is None or "fret" in allowed_classes) and 'frets' in data:
        # Para cada traste detectado
        for (cx, cy, conf) in data['frets']:
            # Desenha círculo verde no centro da detecção
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            # Parâmetros: imagem, centro, raio, cor_BGR, preenchimento(-1=sólido)
            
            # OPÇÃO COMENTADA: Desenhar texto com confiança
            # cv2.putText(frame, f'fret {conf:.2f}', (cx+5, cy-5), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # === DESENHO DA PESTANA (AZUL) ===
    # Verifica se deve desenhar pestana baseado no filtro
    if (allowed_classes is None or "nut" in allowed_classes) and 'nut' in data:
        # Para cada pestana detectada
        for (cx, cy, conf) in data['nut']:
            # Desenha círculo azul no centro da detecção
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            # Cor (255,0,0) = AZUL em formato BGR
            
            # OPÇÃO COMENTADA: Desenhar texto com confiança
            # cv2.putText(frame, f'nut {conf:.2f}', (cx+5, cy-5), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # === DESENHO DO BRAÇO (VERMELHO) ===
    # Verifica se deve desenhar braço baseado no filtro
    if (allowed_classes is None or "neck" in allowed_classes) and 'neck' in data:
        # Para cada braço detectado
        for (cx, cy, conf) in data['neck']:
            # Desenha círculo vermelho no centro da detecção
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            # Cor (0,0,255) = VERMELHO em formato BGR
            
            # OPÇÃO COMENTADA: Desenhar texto com confiança
            # cv2.putText(frame, f'neck {conf:.2f}', (cx+5, cy-5), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # === RETORNO ===
    return frame  # Retorna imagem modificada com as visualizações