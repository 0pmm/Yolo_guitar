"""
Módulo collect_data.py - Organização de Dados do YOLO
=====================================================
Converte resultados brutos do YOLO em dados estruturados
organizados por tipo de objeto detectado na guitarra.

Função principal: collect()
- Entrada: resultados brutos do YOLO
- Saída: dicionário organizado por classes
"""

def collect(results):
    """
    Organiza as detecções do YOLO por tipo de objeto.
    
    Args:
        results: Lista de resultados do YOLO (uma entrada por imagem)
        
    Returns:
        dict: {
            'frets': [(cx,cy,conf), ...],  # Lista de trastes
            'nut': [(cx,cy,conf), ...],    # Lista de pestanas  
            'neck': [(cx,cy,conf), ...]    # Lista de braços
        }
    """
    # === INICIALIZAÇÃO DAS LISTAS ===
    frets = []  # Lista para armazenar trastes detectados
    nut = []    # Lista para armazenar pestana detectada
    neck = []   # Lista para armazenar braço detectado

    # === PROCESSAMENTO DE CADA RESULTADO ===
    for r in results:  # Para cada imagem processada pelo YOLO
        # Extrai todas as caixas delimitadoras desta imagem
        boxes = r.boxes  # Contém todas as detecções da imagem
        
        # === PROCESSAMENTO DE CADA DETECÇÃO ===
        for box in boxes:  # Para cada objeto detectado
            # --- EXTRAÇÃO DAS COORDENADAS ---
            # box.xyxy[0] contém [x1, y1, x2, y2] da caixa delimitadora
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Converte para inteiros
            
            # --- EXTRAÇÃO DE METADADOS ---
            conf = float(box.conf[0])      # Confiança da detecção (0.0 a 1.0)
            classes = int(box.cls[0])      # Índice numérico da classe
            label = r.names[classes]       # Nome da classe ('fret', 'nut', 'neck')
            
            # --- CÁLCULO DO CENTRO ---
            # Centro da caixa delimitadora (ponto médio)
            cx = int((x1 + x2) / 2)        # Centro X
            cy = int((y1 + y2) / 2)        # Centro Y
            
            # === CLASSIFICAÇÃO E ARMAZENAMENTO ===
            # Organiza por tipo de objeto detectado
            if label == 'fret':             # Se é um traste
                frets.append((cx, cy, conf))   # Adiciona à lista de trastes
            elif label == 'nut':            # Se é a pestana
                nut.append((cx, cy, conf))     # Adiciona à lista de pestana
            else:                           # Qualquer outra coisa (braço)
                neck.append((cx, cy, conf))    # Adiciona à lista de braço
    
    # === RETORNO ESTRUTURADO ===
    # Retorna dicionário com todas as detecções organizadas
    return {
        'frets': frets,  # Lista de trastes: [(x,y,confiança), ...]
        'nut': nut,      # Lista de pestana: [(x,y,confiança), ...]
        'neck': neck     # Lista de braço: [(x,y,confiança), ...]
    }
