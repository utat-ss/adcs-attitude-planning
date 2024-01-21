import numpy as np
import math
import svgwrite
import cairosvg

class Speedometer:
    def __init__(self, min_value, max_value, unit_text, values):
        self.min_value = min_value
        self.max_value = max_value
        self.unit_text = unit_text
        self.values = values

    def get_interpolated_value(self, frame, total_frames):
        index = np.interp(frame, [0, total_frames], [0, len(self.values) - 1])
        if index < 0:
            return self.values[0]
        elif index >= len(self.values) - 1:
            return self.values[-1]
        else:
            return np.interp(index, [math.floor(index), math.ceil(index)], [self.values[math.floor(index)], self.values[math.ceil(index)]])


    def generate_frame_png(self, value, frame):
        start_pct = 40
        end_pct = np.interp(value, [self.min_value, self.max_value], [40, 110])
        start_angle = start_pct / 100 * 360
        end_angle = end_pct / 100 * 360
        radius = 100
        center = (radius * 2, radius * 2)

        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        start_point = (center[0] + radius * math.cos(start_rad), center[1] + radius * math.sin(start_rad))
        end_point = (center[0] + radius * math.cos(end_rad), center[1] + radius * math.sin(end_rad))

        large_arc = 1 if end_angle - start_angle > 180 else 0
        dwg = svgwrite.Drawing('temp.svg', profile='tiny', size=(4 * radius, 4 * radius))

        path = dwg.path(d=('M', start_point, 'A', radius, radius, 0, large_arc, 1, end_point),
                        stroke='white', fill='none', stroke_width=10)
        dwg.add(path)
        dwg.save()
        cairosvg.svg2png(url='temp.svg', write_to=f'frame_{frame}.png')
    
    