def collect(results):
    frets = [] # trastes
    nut = [] # pestana
    neck = [] # braço

    frets_box = []
    neck_box = []
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1,y1,x2,y2 = map(int, box.xyxy[0])

            conf = float(box.conf[0])
            classes = int(box.cls[0])
            label = r.names[classes]

            cx = int((x1 + x2)/2)
            cy = int((y1 + y2)/2)

            if label == 'fret':
                frets.append((cx,cy,conf))
                frets_box.append(((x1,y1),(x2,y2), conf))
            elif label == 'nut':
                nut.append((cx,cy,conf))
            else:
                neck.append((cx,cy,conf))
                neck_box.append(((x1,y1),(x2,y2), conf))
    
    return {'frets': frets, 'nut': nut, 'neck': neck, 'frets_box': frets_box, 'neck_box': neck_box}
