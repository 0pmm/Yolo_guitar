from modules.collect_data import collect
from modules.calc_axis import calc_axis
from modules.predict_frets import predict_frets_positions, compare_projected_predicted
from modules.grid_formation import grid_formalization

class DetectionPipeline:
    def __init__(self, model, state_manager):
        self.model = model
        self.state = state_manager
    
    def process_frame(self, frame):
        yolo_data = collect(self.model.predict(source=frame, verbose = False))

        if yolo_data['frets'] or yolo_data['nut']:
            axis_data = calc_axis(
                frame,
                yolo_data['nut'],
                yolo_data['frets'],
                yolo_data['neck_box']
            )
            yolo_data.update(axis_data)

            if yolo_data.get('valid', False):
                expected_data = predict_frets_positions(yolo_data, 20)
                yolo_data.update(expected_data)

                projected_data = compare_projected_predicted(yolo_data)
                yolo_data.update(projected_data)

                grid_data = grid_formalization(
                    yolo_data['neck_box'],
                    yolo_data['nut'][0][:2] if yolo_data['nut'] else None,
                    yolo_data.get('axis_unit', (0,0)),
                    yolo_data.get('pt_projected_final', [])
                )
                yolo_data.update(grid_data)
        
        return self.state.update_with_fallback(yolo_data)
