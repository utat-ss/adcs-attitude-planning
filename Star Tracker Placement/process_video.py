import svgwrite
import cairosvg
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageSequenceClip
import numpy as np
import math
import os

# Constants
total_duration = 10
fps = 24
total_frames = total_duration * fps

for frame in range(total_frames):
    start_pct = 40
    end_pct = np.interp(frame, [0, total_frames], [40, 110])
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

video_clip = VideoFileClip('ex_video.mov')

image_sequence = [f'frame_{frame}.png' for frame in range(total_frames)]
svg_clip = ImageSequenceClip(image_sequence, fps=fps)

svg_clip = svg_clip.set_position(("center", "center")).set_duration(total_duration)

composite_clip = CompositeVideoClip([video_clip, svg_clip.set_start(0)], size=video_clip.size)

composite_clip.write_videofile("output_video.mp4", fps=fps)

for frame in range(total_frames):
    os.remove(f'frame_{frame}.png')
os.remove('temp.svg')

