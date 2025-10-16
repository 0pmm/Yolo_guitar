from itertools import zip_longest
import math

def predict_frets_positions(axis_info, n_frets=19):
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

def compare_projected_predicted(data):
    out = {'pt_projected_final': []}


    if 'nut' not in data or not data['nut']:
        return out
    
    pt_expected = [item['pt'] for item in data['expected']]
    pt_projected = [item['pt'] for item in data['projections']]
    pt_projected.sort(key=lambda x: x[0], reverse=True)

    pt_projected_final = []
    
    axis_unit = data['axis_unit']
    nut = data['nut'][0][:2]

    n_trastes = len(pt_expected)

    for i in range(n_trastes):
        if i < len(pt_projected):
            if i < len(pt_projected) - 1 and i < len(pt_expected) - 1:
                expected_diff = abs(pt_expected[i][0] - pt_expected[i+1][0])
                projected_diff = abs(pt_projected[i][0] - pt_projected[i+1][0])

                if expected_diff * 1.5 < projected_diff:
                    pt = pt_expected[i+1]
                    pt_projected_final.append({
                        'pt': pt,
                        'ordem': i + 1,
                        'distance': axis_distance(pt, nut, axis_unit)
                    })
                    # print(f"[FALHA] Traste {i+1} ausente → usando EXPECTED")
                    pt = pt_projected[i]
                    pt_projected_final.append({
                        'pt': pt,
                        'ordem': i,
                        'distance': axis_distance(pt, nut, axis_unit)
                    })
                    # print(f"[FALHA] Traste {i} OK → usando PROJECTED")
                else:
                    pt = pt_projected[i]
                    pt_projected_final.append({
                        'pt': pt,
                        'ordem': i,
                        'distance': axis_distance(pt, nut, axis_unit)
                    })
                    # print(f"[YOLO] Traste {i+1} OK → usando PROJECTED")
            else:
                pt = pt_projected[i]
                pt_projected_final.append({
                    'pt': pt,
                    'ordem': i,
                    'distance': axis_distance(pt, nut, axis_unit)
                })
                # print(f"[YOLO] Traste {i+1} OK → usando PROJECTED")

    out['pt_projected_final'] = pt_projected_final
    return out


def axis_distance(pt, nut, axis_unit):
    vx = int(pt[0] - nut[0])
    vy = int(pt[1] - nut[1])
    return vx * axis_unit[0] + vy * axis_unit[1]