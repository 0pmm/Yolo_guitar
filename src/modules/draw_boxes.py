import cv2 

def draw(data, frame, allowed_classes):
    if allowed_classes is None or "frets_box" in allowed_classes:
        frets_box = data.get('frets_box', [])
        for (pt1, pt2, conf) in frets_box:
            x1, y1 = pt1
            x2, y2 = pt2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    if allowed_classes is None or "nut" in allowed_classes:
        nut = data.get('nut', [])
        for (cx, cy, conf) in nut:
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), 2)

    if allowed_classes is None or "neck" in allowed_classes:
        neck_box = data.get('neck_box', [])
        for (pt1, pt2, conf) in neck_box:
            x1, y1 = pt1
            x2, y2 = pt2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    valid = data.get('valid', False)
    if valid:
        if allowed_classes is None or "axis" in allowed_classes:
            axis_data = data.get('axis')
            if axis_data:
                start, end = axis_data
                cv2.line(frame, start, end, (0, 255, 255), 2)
        
        if allowed_classes is None or "projections" in allowed_classes:
            projections = data.get('projections', [])
            for p in projections:
                pt = p.get('pt')
                proj = p.get('proj')
                if pt and proj:
                    cv2.circle(frame, pt, 3, (0, 200, 0), -1)
                    cv2.circle(frame, proj, 3, (0, 0, 200), -1)
                    cv2.line(frame, pt, proj, (200, 200, 0), 1)
        
        if allowed_classes is None or "expected" in allowed_classes:
            expected = data.get('expected', [])
            for p in expected:
                pt = p.get('pt')
                if pt:
                    cv2.circle(frame, pt, 3, (255, 0, 255), -1)
        
        if allowed_classes is None or "pt_projected_final" in allowed_classes:
            pt_projected_final = data.get('pt_projected_final', [])
            for p in pt_projected_final:
                pt = p.get('pt')
                if pt:
                    cv2.circle(frame, pt, 3, (255, 0, 0), -1)

    return frame

def draw_chord(frame, casas, chord):
    if not casas:
        return frame
    
    if chord["pestana"]["active"]:
        casa_pestana = chord["pestana"]["casa_start"]
        if casa_pestana not in casas:
            return frame

    if chord["pestana"]["active"]:
        casa_pestana = chord["pestana"]["casa_start"]
        cordas_pestana = chord["pestana"]["cordas"]
        
        if all(casa_pestana in casas and corda in casas[casa_pestana] for corda in cordas_pestana):
            pt_inicio = casas[casa_pestana][cordas_pestana[0]]
            pt_fim = casas[casa_pestana][cordas_pestana[-1]]
            cv2.line(frame, pt_inicio, pt_fim, (0, 255, 255), 3)
            
            pt_medio = casas[casa_pestana][cordas_pestana[len(cordas_pestana)//2]]
            cv2.putText(frame, f"P{chord['pestana']['dedo']}", 
                       (pt_medio[0]-15, pt_medio[1]-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    for corda, info in chord["position"].items():
        if not info["tocar"]:
            if 0 in casas and corda in casas[0]:
                pt = casas[0][corda]
                cv2.circle(frame, pt, 4, (0,0,0), 1)
                cv2.putText(frame, "X", (pt[0], pt[1]),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    for corda, info in chord["position"].items():
        casa = info["casa"]
        dedo = info["dedo"]
        tocar = info["tocar"]
        
        if casa == 0 or dedo == 0:
            continue
            
        if casa in casas and corda in casas[casa]:
            pt = casas[casa][corda]
            cv2.circle(frame, pt, 4, (255, 0, 0), -1)
            cv2.putText(frame, str(dedo), (pt[0]-10, pt[1]+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)
    
    return frame