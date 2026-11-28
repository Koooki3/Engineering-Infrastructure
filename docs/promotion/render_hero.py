"""Render the repository cover and social preview at a 2:1 aspect ratio."""

from pathlib import Path
import math

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont


def font(size, weight='normal', family='DejaVu Sans'):
    path = font_manager.findfont(font_manager.FontProperties(family=family, weight=weight))
    return ImageFont.truetype(path, size)


def main():
    width, height = 1600, 800
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            glow = math.exp(-((x - 1270) / 590) ** 2 - ((y - 360) / 490) ** 2)
            pixels[x, y] = (int(12 + glow * 7), int(22 + glow * 36), int(39 + glow * 34))
    draw = ImageDraw.Draw(image)
    ink, subtle, aqua = '#f4f8ff', '#bbcadc', '#75efd0'

    for x in range(50, width, 36):
        for y in range(46, height, 36):
            if x > 748 and y < 716:
                draw.ellipse((x, y, x + 2, y + 2), fill='#386276')

    def text(position, value, size, color=ink, weight='normal', family='DejaVu Sans'):
        draw.text(position, value, font=font(size, weight, family), fill=color, anchor='lt')

    def circle(x, y, color):
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=color)

    def pill(x, y, value):
        measured = draw.textlength(value, font=font(21, 'bold'))
        draw.rounded_rectangle((x, y, x + measured + 38, y + 44), radius=22, outline='#46667d', width=2)
        text((x + 19, y + 13), value, 21, subtle, 'bold')
        return x + measured + 51

    draw.rounded_rectangle((71, 106, 79, 148), radius=4, fill=aqua)
    text((94, 114), 'ENGINEERING INFRASTRUCTURE', 24, aqua, 'bold')
    text((72, 204), 'From change', 79, weight='bold')
    text((72, 300), 'to verified', 79, weight='bold')
    text((72, 396), 'delivery.', 79, aqua, 'bold')
    text((78, 527), 'A shared workflow for coding agents', 31, subtle)
    text((78, 572), 'with executable checks and recovery.', 31, subtle)
    x = 78
    for label in ('Codex', 'Claude Code', 'OpenCode', 'Antigravity'):
        x = pill(x, 670, label)

    steps = [
        (841, 102, '#7ab4ff', 'Inspect the workspace', 'inputs  /  branch  /  risk'),
        (937, 294, '#75efd0', 'Verify the result', 'tests  /  evidence  /  runtime'),
        (1033, 486, '#ffc487', 'Deliver and recover', 'PR  /  checkpoint  /  rollback'),
    ]
    for i, (x, y, color, title, details) in enumerate(steps):
        w, h = 465, 148
        if i < len(steps) - 1:
            nx, ny = steps[i + 1][:2]
            draw.line((x + 61, y + h, x + 61, y + h + 22, nx + 61, y + h + 22, nx + 61, ny),
                      fill='#71a3bb', width=4)
            draw.polygon(((nx + 54, ny - 13), (nx + 68, ny - 13), (nx + 61, ny)), fill='#71a3bb')
        draw.rounded_rectangle((x + 7, y + 11, x + w + 7, y + h + 11), radius=19, fill='#0b1427')
        draw.rounded_rectangle((x, y, x + w, y + h), radius=19, fill='#142b42', outline='#456d85', width=2)
        circle(x + 30, y + 41, color)
        text((x + 49, y + 27), title, 30, ink, 'bold')
        draw.line((x + 26, y + 74, x + w - 25, y + 74), fill='#36576e', width=2)
        text((x + 27, y + 96), details, 21, color, family='DejaVu Sans Mono')
    text((1044, 695), 'Native installs for Windows and WSL', 23, subtle)
    image.save(Path(__file__).resolve().parents[1] / 'diagrams/engineering-infrastructure.png', optimize=True)


if __name__ == '__main__':
    main()
