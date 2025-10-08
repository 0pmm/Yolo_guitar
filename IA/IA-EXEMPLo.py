import cv2
import numpy as np
from ultralytics import YOLO
from statistics import median

# --- parâmetros ---
MAX_FRETS_TO_COMPUTE = 20
MAX_START_CANDIDATE = 6
RMSE_ACCEPT_THRESHOLD = 10.0
SMOOTHING_ALPHA = 0.6

# Acordes exemplo: (corda, casa)
acordes = {
    "E_major": [(3,1),(5,2),(4,2)]
}

# --- funções auxiliares ---
def unit_vector(v):
    n = np.linalg.norm(v)
    return v/n if n > 0 else np.array([1.0,0.0])

def project_scalar(point, origin, axis_unit):
    return float(np.dot(point-origin, axis_unit))

def estimate_scale_from_observed(s_obs, start_candidate_max=MAX_START_CANDIDATE):
    s_obs = np.array(s_obs, dtype=float)
    best = (None, None, float("inf"))
    if len(s_obs) == 0:
        return best
    for m in range(1, start_candidate_max+1):
        L_candidates = []
        valid = True
        for j,s in enumerate(s_obs,start=0):
            n = m+j
            denom = 1 - 2**(-n/12)
            if denom <= 1e-6:
                valid=False; break
            L_candidates.append(s/denom)
        if not valid: continue
        L_med = float(median(L_candidates))
        if L_med <= 0: continue
        d_pred = np.array([L_med*(1-2**(-(m+j)/12)) for j in range(len(s_obs))])
        rmse = float(np.sqrt(np.mean((s_obs-d_pred)**2)))
        if L_med < max(s_obs)*1.01: continue
        if rmse < best[2]:
            best=(m,L_med,rmse)
    return best

def compute_fret_theoretical_positions(nut_pos, axis_unit, L, n_frets=MAX_FRETS_TO_COMPUTE):
    pts=[]
    for n in range(1,n_frets+1):
        d_n = L*(1-2**(-n/12))
        pt = tuple((nut_pos+axis_unit*d_n).astype(int))
        pts.append((n,pt,d_n))
    return pts

def build_grid_from_frets(nut_pos, axis_unit, perp_unit, fret_positions, neck_box, n_strings=6):
    x1,y1,x2,y2 = neck_box
    neck_width = y2-y1
    string_spacing = neck_width/n_strings
    casas={}
    d_list=[0.0]+[d for (_,_,d) in fret_positions]
    for i in range(1,len(d_list)):
        d_left,d_right = d_list[i-1],d_list[i]
        d_mid = 0.5*(d_left+d_right)
        center = nut_pos+axis_unit*d_mid
        casas[i]={}
        for k in range(n_strings):
            offset=(k+0.5)-(n_strings/2.0)
            pos=center+perp_unit*(offset*string_spacing)
            casas[i][k+1]=(int(pos[0]),int(pos[1]))
    return casas

# --- rotina principal ---
def process_frame(frame, results, prev_state=None):
    state={'L':None,'axis_unit':None,'perp_unit':None,'fret_theoretical':None,'casas':None,'nut':None,'neck_box':None}

    if len(results)==0: return frame,state
    r=results[0]
    if r.boxes is None: return frame,state

    classes=r.boxes.cls.cpu().numpy().astype(int)
    boxes=r.boxes.xyxy.cpu().numpy().astype(int)

    frets_centers=[]
    nut_center=None
    neck_box=None

    for cls,box in zip(classes,boxes):
        x1,y1,x2,y2=box
        cx,cy=int((x1+x2)/2),int((y1+y2)/2)
        if cls==0: # fret
            frets_centers.append((cx,cy))
            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),1)
        elif cls==1: # neck
            neck_box=(x1,y1,x2,y2)
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
        elif cls==2: # nut
            nut_center=np.array((cx,cy),dtype=float)
            cv2.circle(frame,(cx,cy),5,(0,255,255),-1)

    if nut_center is None:
        if prev_state and prev_state.get('nut') is not None:
            nut_center=prev_state['nut']
        else:
            if len(frets_centers)>0:
                min_x=min(fx for fx,fy in frets_centers)
                nut_center=np.array((min_x-40.0,np.mean([fy for fx,fy in frets_centers])),dtype=float)
            else:
                return frame,state
    if neck_box is None:
        if prev_state and prev_state.get('neck_box') is not None:
            neck_box=prev_state['neck_box']
        else:
            if len(frets_centers)==0: return frame,state
            ys=[fy for fx,fy in frets_centers]
            y_top,y_bot=min(ys)-50,max(ys)+50
            x_left=min(fx for fx,fy in frets_centers)-40
            x_right=max(fx for fx,fy in frets_centers)+40
            neck_box=(x_left,y_top,x_right,y_bot)

    mean_frets=np.array(np.mean(np.array(frets_centers),axis=0)) if len(frets_centers)>0 else None
    axis_unit=unit_vector(mean_frets-nut_center) if mean_frets is not None else np.array([1.0,0.0])
    perp_unit=np.array([-axis_unit[1],axis_unit[0]])

    frets_proj=[]
    for (fx,fy) in frets_centers:
        s=project_scalar(np.array([fx,fy],dtype=float),nut_center,axis_unit)
        if s>0: frets_proj.append((s,(fx,fy)))
    if len(frets_proj)==0 and prev_state: return frame,prev_state

    frets_proj=sorted(frets_proj,key=lambda x:x[0])
    s_obs=[s for s,_ in frets_proj]

    best_m,best_L,best_rmse=estimate_scale_from_observed(s_obs)

    if best_L is None or best_rmse is None or best_rmse>RMSE_ACCEPT_THRESHOLD:
        if prev_state and prev_state.get('L') is not None:
            L_est=SMOOTHING_ALPHA*prev_state['L']+(1-SMOOTHING_ALPHA)*(best_L if best_L else prev_state['L'])
            axis_unit=SMOOTHING_ALPHA*prev_state['axis_unit']+(1-SMOOTHING_ALPHA)*axis_unit
            axis_unit=unit_vector(axis_unit)
            perp_unit=np.array([-axis_unit[1],axis_unit[0]])
        else:
            if len(s_obs)>=1:
                guessed_n=len(s_obs)
                L_est=s_obs[-1]/(1-2**(-guessed_n/12))
            else:
                return frame,state
    else:
        L_est=best_L

    if prev_state and prev_state.get('L') is not None:
        L_est=SMOOTHING_ALPHA*prev_state['L']+(1-SMOOTHING_ALPHA)*L_est

    fret_theoretical=compute_fret_theoretical_positions(nut_center,axis_unit,L_est)
    casas=build_grid_from_frets(nut_center,axis_unit,perp_unit,fret_theoretical,neck_box)

    for house_idx,mapping in casas.items():
        for s_idx,(x,y) in mapping.items():
            cv2.circle(frame,(x,y),2,(0,0,255),-1)

    state.update({'L':L_est,'axis_unit':axis_unit,'perp_unit':perp_unit,
                  'fret_theoretical':fret_theoretical,'casas':casas,
                  'nut':nut_center,'neck_box':neck_box})

    return frame,state

# --- main webcam ---
if __name__=="__main__":
    model=YOLO(r"C:\Users\Pedro\Documents\Estudos\IF 4°\PICO\yolo_guitar\runs\detect\train\weights\best.pt")
    cap=cv2.VideoCapture(0)
    prev_state=None

    while True:
        # ret,frame=cap.read()
        # if not ret: break
        frame = cv2.imread("violao.jpg")
        
        results=model(frame)
        frame_drawn,prev_state=process_frame(frame,results,prev_state)

        if prev_state and prev_state.get('casas'):
            grid=prev_state['casas']
            for corda,casa in acordes["E_major"]:
                if casa in grid and corda in grid[casa]:
                    x,y=grid[casa][corda]
                    cv2.circle(frame_drawn,(x,y),10,(0,255,0),-1)

        cv2.imshow("Assistente Acordes",frame_drawn)
        if cv2.waitKey(1)&0xFF==ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
