import svgwrite
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageSequenceClip
import numpy as np
import math
import os
from speedometer import Speedometer
import json

class STKVideo:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_clip = VideoFileClip(video_path)
        self.total_frames = int(self.video_clip.fps * self.video_clip.duration)
        self.speedometers = []
        self.spedometer_scale = 0.4

    def get_total_frames(self):
        return self.total_frames

    def get_frame_rate(self):
        return self.video_clip.fps

    def get_duration(self):
        return self.video_clip.duration

    def add_speedometer(self, speedometer):
        self.speedometers.append(speedometer)

    def get_height(self):
        return self.video_clip.size[1]

    def get_width(self):
        return self.video_clip.size[0]
    
    def get_speedometer_size(self):
        return self.get_height() * self.spedometer_scale
    
    def load_from_json(self, json_path): 
        with open(json_path, "r") as file:
            data = json.load(file)

        for speedometer in data["speedometers"]:
            meter = Speedometer(speedometer["min_value"], speedometer["max_value"], speedometer["unit_text"], speedometer["label"], speedometer["values"])
            meter.set_yellow_zone(speedometer["yellow_zone"])
            meter.set_red_zone(speedometer["red_zone"]) 
            self.add_speedometer(meter)
            
        '''
        Example JSON:
        {
            "speedometers": [
                {
                    "min_value": 0,
                    "max_value": 100,
                    "unit_text": "DEG/SEC",
                    "label": "SLEW RATE",
                    "values": [0, 100, 0, 100, 0, 100, 0, 100, 0, 100, 100],
                    "yellow_zone": [60, 80],
                    "red_zone": [80, 100]
                },
                {
                    "min_value": 0,
                    "max_value": 100,
                    "unit_text": "PX",
                    "label": "ERROR",
                    "values": [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100],
                    "yellow_zone": [60, 80],
                    "red_zone": [80, 100]
                }
            ]
        }
        '''
        pass
    
    def process(self, output_path):
        composite_clip = self.video_clip
        for index, speedometer in enumerate(self.speedometers):
            print(f'Processing speedometer {index + 1} of {len(self.speedometers)}')
            for frame in range(self.total_frames):
                speedometer.generate_frame_png(speedometer.get_interpolated_value(frame, self.total_frames), frame)
                
            image_sequence = [f'{speedometer.label}_{frame}.png' for frame in range(self.total_frames)]
            svg_clip = ImageSequenceClip(image_sequence, fps=self.video_clip.fps)

            size = self.get_speedometer_size()
            x_offset = size * 0.7 * index
            svg_clip = svg_clip.resize((size,size)).set_position((-0.1 * size + x_offset, self.get_height() - 0.8 * size)).set_duration(self.video_clip.duration)

            composite_clip = CompositeVideoClip([composite_clip, svg_clip.set_start(0)], size=self.video_clip.size)

        composite_clip.write_videofile(output_path, fps=self.video_clip.fps)

        for frame in range(self.total_frames):
            for speedometer in self.speedometers:
                os.remove(f'{speedometer.label}_{frame}.png')
        if os.path.exists('temp.svg'):
            os.remove('temp.svg')



video = STKVideo('ex_video.mov')
video.load_from_json('example_config.json')
video.process("output_video.mp4")
# slewmeter = Speedometer(0, 100, 'DEG/SEC', 'SLEW RATE', [0, 100, 0, 100, 0, 100, 0, 100, 0, 100, 100])
# slewmeter.set_yellow_zone([60, 80])
# slewmeter.set_red_zone([80, 100])
# video.add_speedometer(slewmeter)
# errormeter = Speedometer(0, 100, 'PX', 'ERROR', [0, 50, 60, 10, 50, 60, 80, 100, 0, 100, 100])
# errormeter.set_yellow_zone([60, 80])
# errormeter.set_red_zone([80, 100])
# video.add_speedometer(errormeter)
# errormeter = Speedometer(0, 100, 'DEG', 'SUN ANGLE', [0, 100, 50, 40, 30, 20, 10, 0, 0, 100, 100])
# errormeter.set_yellow_zone([60, 80])
# errormeter.set_red_zone([80, 100])
# video.add_speedometer(errormeter)
# video.process("output_video.mp4")