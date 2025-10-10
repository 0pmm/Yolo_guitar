import math

def calc_axis(frame, nut, frets, neck_box):
    out = {'valid': False, 'nut_point': None, 'mean_frets': None, 'axis': None, 'axis_unit': None, 'angle_deg': None, 'projections': []}

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

    start = nut_pt    
    if neck_box and len(neck_box) > 0:
        (nx1, ny1), (nx2, ny2), conf = neck_box[0]
        neck_length = math.hypot(nx2 - nx1, ny2 - ny1) - 12
        
        end = (
            int(nut_pt[0] + ux * neck_length),
            int(nut_pt[1] + uy * neck_length)
        )
    else:
        frame_height = frame.shape[0]
        default_length = frame_height * 0.8
        end = (
            int(nut_pt[0] + ux * default_length),
            int(nut_pt[1] + uy * default_length)
        )
    ax = end[0] - start[0]
    ay = end[1] - start[1]
    norm = math.hypot(ax,ay)
    angle_deg = math.degrees(math.atan2(uy, ux))

    out.update({
        'valid': True, 
        'nut_point': nut_pt, 
        'mean_frets': mean_pt, 
        'axis': (start, end),
        'axis_unit': (ax/norm, ay/norm),
        'angle_deg': angle_deg
    })

    projections = []
    n = 1
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
            'n': n,
            'conf': conf
        })
        n += 1

    out['projections'] = projections
    return out