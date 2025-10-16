import cv2 

def draw(data, frame, allowed_classes):
    if allowed_classes is None or "frets_box" in allowed_classes:
        for (pt1, pt2, conf) in data['frets_box']:
            x1, y1 = pt1
            x2, y2 = pt2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    if allowed_classes is None or "nut" in allowed_classes:
        for (cx, cy, conf) in data['nut']:
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), 2)

    if allowed_classes is None or "neck" in allowed_classes:
        for (pt1, pt2, conf) in data['neck_box']:
            x1, y1 = pt1
            x2, y2 = pt2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    if 'valid' in data and data['valid']:
        if allowed_classes is None or "axis" in allowed_classes:
            start, end = data['axis']
            cv2.line(frame, start, end, (0, 255, 255), 2)
        if allowed_classes is None or "projections" in allowed_classes:
            for p in data['projections']:
                pt = p.get('pt')
                proj = p.get('proj')
                if pt and proj:
                    cv2.circle(frame, pt, 3, (0, 200, 0), -1)
                    cv2.circle(frame, proj, 3, (0, 0, 200), -1)
                    cv2.line(frame, pt, proj, (200, 200, 0), 1)
        if allowed_classes is None or "expected" in allowed_classes:
            for p in data['expected']:
                pt = p.get('pt')
                cv2.circle(frame, pt, 3, (255, 0, 255), -1)
        if allowed_classes is None or "pt_projected_final" in allowed_classes:
            for p in data['pt_projected_final']:
                pt = p.get('pt')
                cv2.circle(frame, pt, 3, (255,0,0), -1)

    return frame

def draw_chord(frame, casas, chord):
    if not casas:
        return frame
    
    if chord["pestana"]["active"]:
        casa_pestana = chord["pestana"]["casa_start"]
        if casa_pestana not in casas:
            return frame 
    
    for corda, info in chord["position"].items():
        casa = info["casa"]
        if casa > 0 and casa not in casas:
            return frame
        
    if chord["pestana"]["active"]:
        casa_pestana = chord["pestana"]["casa_start"]
        cordas_pestana = chord["pestana"]["cordas"]
        
        pt_inicio = casas[casa_pestana][cordas_pestana[0]]
        pt_fim = casas[casa_pestana][cordas_pestana[-1]]
        cv2.line(frame, pt_inicio, pt_fim, (0, 255, 255), 3)
        
        pt_medio = casas[casa_pestana][cordas_pestana[len(cordas_pestana)//2]]
        cv2.putText(frame, f"P{chord['pestana']['dedo']}", 
                   (pt_medio[0]-15, pt_medio[1]-20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    for corda, info in chord["position"].items():
        casa = info["casa"]
        dedo = info["dedo"]
        tocar = info["tocar"]
        
        if casa == 0 or dedo == 0:
            continue
            
        pt = casas[casa][corda]
        
        cv2.circle(frame, pt, 8, (255, 0, 0), -1)
        cv2.putText(frame, str(dedo), (pt[0]-10, pt[1]+5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    for corda, info in chord["position"].items():
        if not info["tocar"] and info["casa"] == 0:
            pt = casas[0][corda]
            cv2.putText(frame, "X", (pt[0]-15, pt[1]-30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return frame

