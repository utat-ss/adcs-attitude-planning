import numpy as np
import math
import svgwrite
import cairosvg

class Speedometer:
    def __init__(self, min_value, max_value, unit_text, label, values):
        self.min_value = min_value
        self.max_value = max_value
        self.unit_text = unit_text
        self.label = label
        self.values = values
        self.decimal_accuracy = 0

    def get_interpolated_value(self, frame, total_frames):
        index = np.interp(frame, [0, total_frames], [0, len(self.values) - 1])
        if index < 0:
            return self.values[0]
        elif index >= len(self.values) - 1:
            return self.values[-1]
        else:
            return np.interp(index, [math.floor(index), math.ceil(index)], [self.values[math.floor(index)], self.values[math.ceil(index)]])

    def set_yellow_zone(self, yellow_zone):
        self.yellow_zone = yellow_zone

    def set_red_zone(self, red_zone):
        self.red_zone = red_zone
    
    def set_custom_zone(self, range, color):
        self.custom_zone = [range, color]

    def set_decimal_accuracy(self, decimal_accuracy):
        self.decimal_accuracy = decimal_accuracy


    def add_dial_path(self, dwg, value, width, color='white', radius = 100, start_value = None):
        start_pct = 40
        if start_value is not None:
            start_pct = np.interp(start_value, [self.min_value, self.max_value], [40, 110])

        end_pct = np.interp(value, [self.min_value, self.max_value], [40, 110])

        start_angle = start_pct / 100 * 360
        end_angle = end_pct / 100 * 360
        center = (radius * 2, radius * 2)

        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        start_point = (center[0] + radius * math.cos(start_rad), center[1] + radius * math.sin(start_rad))
        end_point = (center[0] + radius * math.cos(end_rad), center[1] + radius * math.sin(end_rad))

        large_arc = 1 if end_angle - start_angle > 180 else 0

        path = dwg.path(d=('M', start_point, 'A', radius, radius, 0, large_arc, 1, end_point),
                        stroke=color, fill='none', stroke_width=width)
        dwg.add(path)

    
    def get_text_color(self, value):
        if hasattr(self, 'red_zone') and value >= self.red_zone[0] and value <= self.red_zone[1]:
            return 'red'
        elif hasattr(self, 'yellow_zone') and value >= self.yellow_zone[0] and value <= self.yellow_zone[1]:
            return 'yellow'
        else:
            return 'white'

    def set_default_font(self, dwg):
        dwg.add_stylesheet('style.css', title='style')


    def add_dial_text(self, dwg, value, radius = 100):
        center = (radius * 2, radius * 2)
        rounded_value = round(value, self.decimal_accuracy)
        if self.decimal_accuracy == 0:
            rounded_value = int(rounded_value)
        text = dwg.text(f'{rounded_value}', insert=(center[0], center[1]), text_anchor='middle', font_size=50, fill=self.get_text_color(value), font_family='syncrone')
        dwg.add(text)
        text = dwg.text(f'{self.unit_text}', insert=(center[0], center[1] + 40), text_anchor='middle', font_size=23, fill='grey', font_family='syncrone')
        dwg.add(text)

        text = dwg.text(self.label, insert=(center[0], center[1] - 120), text_anchor='middle', font_size=30, fill='white', font_family='syncrone')
        dwg.add(text)


    def generate_frame_png(self, value, frame):
        radius = 100
        dwg = svgwrite.Drawing('temp.svg', profile='tiny', size=(4 * radius, 4 * radius))
        self.set_default_font(dwg)
        self.add_dial_path(dwg, 100, 10, 'gray')

        if hasattr(self, 'yellow_zone'):
            self.add_dial_path(dwg, self.yellow_zone[1], 10, 'yellow', start_value=self.yellow_zone[0])
        if hasattr(self, 'red_zone'):
            self.add_dial_path(dwg, self.red_zone[1], 10, 'red', start_value=self.red_zone[0])
        if hasattr(self, 'custom_zone'):
            self.add_dial_path(dwg, self.custom_zone[1][1], 10, self.custom_zone[1][0], start_value=self.custom_zone[0][0])

        self.add_dial_path(dwg, value, 10)
        self.add_dial_text(dwg, value)
        dwg.save()
        cairosvg.svg2png(url='temp.svg', write_to=f'frame_{frame}.png')
    
    