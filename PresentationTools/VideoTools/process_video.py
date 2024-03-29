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
            if "yellow_zone" in speedometer:
                meter.set_yellow_zone(speedometer["yellow_zone"])
            if "red_zone" in speedometer:
                meter.set_red_zone(speedometer["red_zone"]) 
            self.add_speedometer(meter)

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



# video = STKVideo('raw_videos/X-AXIS-OCT18-OCT23_2025_LONGEST_PASS.mp4')
# video.load_from_json('config/X-AXIS-OCT18-17-00-OCT23-17-00-VALID-VIDEO.json')
# video.process("X-AXIS-LONGEST-PASS-VIDEO.mp4")

video = STKVideo('raw_videos/Y-AXIS-OCT18-OCT23_2025_LONGEST_PASS.mp4')
video.load_from_json('config/Y-AXIS-OCT18-17-00-OCT23-17-00-VALID-VIDEO.json')
video.process("Y-AXIS-LONGEST-PASS-VIDEO.mp4")