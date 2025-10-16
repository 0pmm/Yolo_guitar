import numpy as np

def grid_formalization(neck_box, nut, axis, pt_projected_final):
    out = {'casas': {}}

    if not neck_box or not nut or not axis or not pt_projected_final:
        return out

    try:
        # Converte nut e axis para np.array
        nut = np.array(nut, dtype=float)
        axis = np.array(axis, dtype=float)
        
        # Vetorizando neck
        (x1, y1), (x2, y2), conf = neck_box[0]
        neck_width = y2 - y1
        cordas = neck_width / 6

        casas = {}

        # Perpendicular unit vector
        perp_unit = np.array([-axis[1], axis[0]])
        perp_unit = perp_unit / np.linalg.norm(perp_unit)

        d_list = [0.0] + [float(d['distance']) for d in pt_projected_final]

        for i in range(1, len(d_list)):
            d_left, d_right = d_list[i-1], d_list[i]
            d_mid = 0.5 * (d_left + d_right)
            center = nut + axis * d_mid
            casas[i] = {}
            for k in range(6):
                offset = (k + 0.5) - (6/2.0)
                pos = center + perp_unit * (offset * cordas)
                casas[i][k+1] = (int(pos[0]), int(pos[1]))

        out['casas'] = casas
    except Exception as e:
        print(f"Erro no grid_formation: {e}")
        out['casas'] = {}

    return out