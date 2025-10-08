"""
    frets = [] # trastes
    nut = [] # parte branca
    neck = [] # braço
"""

def calc_axis(frame, nut, frets):
    """

    Returns a minimal dict: valid, nut_point, mean_frets, axis, angle_deg, projections (list of s values and proj pts).
    """
    import math

    out = {'valid': False, 'nut_point': None, 'mean_frets': None, 'axis': None, 'angle_deg': None, 'projections': []}

    if not frets:
        return out

    # choose nut
    if nut:
        nut_pt = (int(nut[0][0]), int(nut[0][1]))
    else:
        # fallback to top-most fret
        fx = min(frets, key=lambda x: x[1])
        nut_pt = (int(fx[0]), int(fx[1]))

    # mean of frets
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

    # axis endpoints for drawing (extend across image)
    h, w = frame.shape[:2]
    pad = max(w, h)
    start = (int(nut_pt[0] - ux * pad), int(nut_pt[1] - uy * pad))
    end = (int(nut_pt[0] + ux * pad), int(nut_pt[1] + uy * pad))

    angle_deg = math.degrees(math.atan2(uy, ux))

    out.update({'valid': True, 'nut_point': nut_pt, 'mean_frets': mean_pt, 'axis': (start, end), 'angle_deg': angle_deg})

    # project each fret onto the axis and compute scalar s
    projections = []
    for cx, cy, conf in frets:
        rx = cx - nut_pt[0]
        ry = cy - nut_pt[1]
        s = rx * ux + ry * uy
        proj_x = int(nut_pt[0] + ux * s)
        proj_y = int(nut_pt[1] + uy * s)
        projections.append({'pt': (int(cx), int(cy)), 'proj': (proj_x, proj_y), 's': s, 'conf': conf})

    out['projections'] = projections

    return out