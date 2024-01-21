import svgwrite
import cairosvg
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageSequenceClip
import numpy as np
from math import cos, sin, radians
import os

# Constants
total_duration = 10  # 10 seconds
fps = 24  # frames per second
total_frames = total_duration * fps

# Generate SVG frames
for frame in range(total_frames):
    # Calculate color transition
    color = np.interp(frame, [0, total_frames], [0, 255])
    hex_color = f'#{int(color):02x}{int(color):02x}{int(color):02x}'

    start_rad = radians(360 - 150)
    end_rad = radians(360 - 30)
    radius = 100

    # SVG Drawing initialization
    dwg = svgwrite.Drawing('temp.svg', profile='tiny', size=(4 * radius, 4 * radius))

    # Center of the semi-circle
    cx, cy = radius, radius

    # Calculate start and end points of the semi-circle
    x_start = cx + radius * cos(start_rad)
    y_start = cy - radius * sin(start_rad)
    x_end = cx + radius * cos(end_rad)
    y_end = cy - radius * sin(end_rad)

    # Path for the semi-circle
    path = dwg.path(d=('M', x_start, y_start, 
                       'A', radius, radius, 0, 0, 1, x_end, y_end),
                    stroke='white', fill='none', stroke_width=5)
    dwg.add(path)

    # Adding markers for start and end angles
    # dwg.add(dwg.line(start=(cx, cy), end=(x_start, y_start), stroke=svgwrite.rgb(10, 10, 16, '%')))
    # dwg.add(dwg.line(start=(cx, cy), end=(x_end, y_end), stroke=svgwrite.rgb(10, 10, 16, '%')))

    # Sav
    dwg.save()

    # Convert SVG to PNG
    cairosvg.svg2png(url='temp.svg', write_to=f'frame_{frame}.png')

# Load video
video_clip = VideoFileClip('ex_video.mov')

# Create an image sequence clip with the SVG frames
image_sequence = [f'frame_{frame}.png' for frame in range(total_frames)]
svg_clip = ImageSequenceClip(image_sequence, fps=fps)

# Set the position and size if necessary
svg_clip = svg_clip.set_position(("center", "center")).set_duration(total_duration)

# Composite the SVG clip over the video
composite_clip = CompositeVideoClip([video_clip, svg_clip.set_start(0)], size=video_clip.size)

# Write the result to a file
composite_clip.write_videofile("output_video.mp4", fps=fps)

# Cleanup temporary files
for frame in range(total_frames):
    os.remove(f'frame_{frame}.png')
os.remove('temp.svg')

