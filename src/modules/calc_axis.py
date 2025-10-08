import math

def calc_axis(frame, nut, frets, neck_box):
    out = {'valid': False, 'nut_point': None, 'mean_frets': None, 'axis': None, 'angle_deg': None, 'projections': []}

    if not frets:
        return out

    if nut:
        nut_pt = (int(nut[0][0]), int(nut[0][1]))
    else:
        fx = min(frets, key=lambda x: x[1])
        nut_pt = (int(fx[0]), int(fx[1]))

    sx = sy = 0.0
    for cx, cy, _ in frets:
        sx += cx; sy += cy
    mean_x = sx / len(frets)
    mean_y = sy / len(frets)
    mean_pt = (int(mean_x), int(mean_y))

    dx = mean_x - nut_pt[0]
    dy = mean_y - nut_pt[1]
    norm = math.hypot(dx, dy)
    if norm < 1e-6:
        return out
    ux = dx / norm
    uy = dy / norm

    # DEFINIR start E end SEMPRE (mesmo sem neck_box)
    start = nut_pt  # start é sempre a nut
    
    if neck_box and len(neck_box) > 0:
        # Usar o comprimento da neck box como referência
        (nx1, ny1), (nx2, ny2), conf = neck_box[0]
        neck_length = math.hypot(nx2 - nx1, ny2 - ny1)
        
        # Eixo vai da nut até o final do neck
        end = (
            int(nut_pt[0] + ux * neck_length),
            int(nut_pt[1] + uy * neck_length)
        )
    else:
        # Fallback: usar um comprimento padrão baseado na imagem
        h, w = frame.shape[:2]
        # Usar 80% da largura da imagem como comprimento máximo
        max_length = w * 0.8
        end = (
            int(nut_pt[0] + ux * max_length),
            int(nut_pt[1] + uy * max_length)
        )

    angle_deg = math.degrees(math.atan2(uy, ux))

    out.update({
        'valid': True, 
        'nut_point': nut_pt, 
        'mean_frets': mean_pt, 
        'axis': (start, end), 
        'angle_deg': angle_deg
    })

    projections = []
    for cx, cy, conf in frets:
        rx = cx - nut_pt[0]
        ry = cy - nut_pt[1]
        s = rx * ux + ry * uy
        proj_x = int(nut_pt[0] + ux * s)
        proj_y = int(nut_pt[1] + uy * s)
        projections.append({
            'pt': (int(cx), int(cy)), 
            'proj': (proj_x, proj_y), 
            's': s, 
            'conf': conf
        })

    out['projections'] = projections
    return out