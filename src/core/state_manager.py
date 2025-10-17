class StateManager:
    def __init__(self):
        self.previus_data = {
            'frets_box': [],
            'nut': [],
            'neck_box': [],
            'frets': [],
            'neck': [],
            'valid': False,
            'casas': {},
            'projections': [],
            'expected': [],
            'pt_projected_final': []
        }

    def update_with_fallback(self, new_data):
        for key in self.previus_data.keys():
            if key not in new_data:
                new_data[key] = self.previus_data[key]

        if self._is_valid_detection(new_data):
            self.previus_data.update(new_data)
            return new_data
        else:
            return self.previus_data
    
    def _is_valid_detection(self, data):
        has_casas = data.get('casas') and len(data['casas']) > 0
        has_axis = data.get('axis_unit') is not None
        return has_casas and has_axis