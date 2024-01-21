import svgwrite
import cairosvg
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageSequenceClip
import numpy as np
import math
import os
from speedometer import Speedometer

class STKVideo:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_clip = VideoFileClip(video_path)
        self.total_frames = int(self.video_clip.fps * self.video_clip.duration)
        self.speedometers = []

    def get_total_frames(self):
        return self.total_frames

    def get_frame_rate(self):
        return self.video_clip.fps

    def get_duration(self):
        return self.video_clip.duration

    def add_speedometer(self, speedometer):
        self.speedometers.append(speedometer)
    
    def process(self, output_path):
        for frame in range(self.total_frames):
            for speedometer in self.speedometers:
                speedometer.generate_frame_png(speedometer.get_interpolated_value(frame, self.total_frames), frame)

        image_sequence = [f'frame_{frame}.png' for frame in range(self.total_frames)]
        svg_clip = ImageSequenceClip(image_sequence, fps=self.video_clip.fps)

        svg_clip = svg_clip.set_position(("center", "center")).set_duration(self.video_clip.duration)

        composite_clip = CompositeVideoClip([self.video_clip, svg_clip.set_start(0)], size=self.video_clip.size)

        composite_clip.write_videofile(output_path, fps=self.video_clip.fps)

        for frame in range(self.total_frames):
            os.remove(f'frame_{frame}.png')
        os.remove('temp.svg')


video = STKVideo('ex_video.mov')
speedometer = Speedometer(0, 100, 'km/h', [0, 100, 0, 100, 0, 100, 0, 100, 0, 100, 100])
video.add_speedometer(speedometer)
video.process("output_video.mp4")