import math

def predict_frets_positions(axis_info, n_frets=20):
    out = {'expected': []}

    if not axis_info.get('valid', False):
        return out
    
    projections = axis_info['projections']
    if not projections or len(projections) < 2:
        return out

    nut_point = axis_info['nut_point']
    farthest_proj = max(projections, key=lambda x: x['s'])
    
    ux = farthest_proj['proj'][0] - nut_point[0]
    uy = farthest_proj['proj'][1] - nut_point[1]
    norm = math.hypot(ux, uy)
    ux /= norm
    uy /= norm

    max_s = farthest_proj['s']
    scale_length = max_s * 1.489
    expected = []
    for n in range(1, n_frets + 1):
        s = scale_length * (1 - 1 / (2 ** (n / 12)))
        
        px = int(nut_point[0] + ux * s)
        py = int(nut_point[1] + uy * s)
        
        expected.append({'n': n, 's': s, 'pt': (px, py)})

    out['expected'] = expected
    return out