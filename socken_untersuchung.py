#!/usr/bin/env python3
"""Erzeugt einen kurzen, animierten Hochkant-Erklärfilm über verschwundene Socken."""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH, HEIGHT, FPS = 720, 1280, 24
SCENE_SECONDS = 5
OUTPUT = Path("socken_untersuchung.mp4")
BG = (14, 21, 39)
WHITE = (247, 245, 232)
MINT = (103, 232, 198)
YELLOW = (255, 205, 87)
PINK = (255, 125, 157)
BLUE = (91, 157, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/Library/Fonts/Arial Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT = font( thirty := 30)
TITLE = font(52, True)
SUBTITLE = font(27)
SMALL = font(22)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill=WHITE):
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((WIDTH - (box[2] - box[0])) / 2, y), text, font=fnt, fill=fill)


def wrapped(draw: ImageDraw.ImageDraw, text: str, fnt, width: int):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(draw, text, y, fnt=SUBTITLE, fill=WHITE, width=610, gap=12):
    for line in wrapped(draw, text, fnt, width):
        centered(draw, line, y, fnt, fill)
        y += fnt.size + gap
    return y


def sock(draw, x, y, scale=1.0, color=YELLOW, tilt=0):
    # Sock silhouette with a contrasting cuff; coordinates are scaled from a compact shape.
    layer = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((62, 18, 115, 104), radius=20, fill=color)
    d.rounded_rectangle((62, 72, 116, 121), radius=18, fill=color)
    d.rounded_rectangle((84, 99, 150, 145), radius=22, fill=color)
    d.rounded_rectangle((59, 13, 118, 36), radius=9, fill=WHITE)
    layer = layer.rotate(tilt, resample=Image.Resampling.BICUBIC, expand=False)
    layer = layer.resize((int(180 * scale), int(180 * scale)), Image.Resampling.LANCZOS)
    image.paste(layer, (int(x), int(y)), layer)


def washer(draw, t, x=190, y=400, size=340):
    draw.rounded_rectangle((x, y, x + size, y + size), radius=36, fill=(222, 230, 235), outline=WHITE, width=5)
    draw.rounded_rectangle((x + 25, y + 24, x + size - 25, y + 85), radius=18, fill=(193, 205, 213))
    draw.ellipse((x + 45, y + 39, x + 85, y + 79), fill=BLUE)
    draw.ellipse((x + size - 75, y + 36, x + size - 42, y + 69), fill=(120, 135, 145))
    cx, cy = x + size / 2, y + size * .62
    r = size * .36
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(41, 58, 76), outline=(153, 183, 199), width=12)
    draw.ellipse((cx-r*.76, cy-r*.76, cx+r*.76, cy+r*.76), fill=(31, 68, 87))
    # A sock orbiting inside makes the drum motion readable without claiming it vanishes magically.
    angle = t * 2.4
    sx = cx + math.cos(angle) * r * .42 - 35
    sy = cy + math.sin(angle) * r * .42 - 43
    sock(draw, sx, sy, .65, YELLOW, int(math.degrees(angle)))


def scene_frame(scene: int, t: float) -> Image.Image:
    global image
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(image)
    # Subtle decorative dots
    for px, py in [(55, 160), (654, 220), (80, 1070), (635, 1020)]:
        d.ellipse((px-4, py-4, px+4, py+4), fill=(48, 69, 89))

    if scene == 0:
        centered(d, "DIE SOCKEN-AKTE", 165, SMALL, MINT)
        centered(d, "Warum verschwinden", 260, TITLE)
        centered(d, "Socken in der", 330, TITLE)
        centered(d, "Waschmaschine?", 400, TITLE, YELLOW)
        washer(d, t, 190, 555, 340)
        centered(d, "Eine kleine Untersuchung", 1010, SUBTITLE, MINT)
    elif scene == 1:
        centered(d, "SPUR 1: DIE TÜRDICHTUNG", 160, SMALL, MINT)
        washer(d, t, 190, 320, 340)
        # Magnifying-glass callout points at the rubber seal.
        d.ellipse((445, 675, 570, 800), outline=YELLOW, width=12)
        d.line((550, 780, 615, 845), fill=YELLOW, width=15)
        centered(d, "Kleine Wäschestücke können", 870, SUBTITLE)
        centered(d, "sich an Dichtung oder Trommel", 915, SUBTITLE)
        centered(d, "verfangen – je nach Gerät.", 960, SUBTITLE, YELLOW)
    elif scene == 2:
        centered(d, "SPUR 2: STATISCHE AUFLADUNG", 160, SMALL, MINT)
        sock(d, 185, 345, 1.2, PINK, -13)
        sock(d, 365, 435, 1.0, BLUE, 14)
        for i in range(5):
            xx = 150 + i * 95
            d.line((xx, 650, xx + 25, 690), fill=YELLOW, width=5)
            d.line((xx + 25, 650, xx, 690), fill=YELLOW, width=5)
        paragraph(d, "Socken kleben manchmal an größeren Teilen oder bleiben in Bettwäsche und Ärmeln hängen.", 790)
        centered(d, "Prüfe zuerst die ganze Ladung.", 1030, SUBTITLE, YELLOW)
    elif scene == 3:
        centered(d, "SPUR 3: DIE SORTIERUNG", 160, SMALL, MINT)
        d.rounded_rectangle((95, 360, 625, 740), radius=32, fill=(33, 48, 66), outline=(74, 99, 120), width=4)
        sock(d, 180, 420, .9, YELLOW, -8)
        sock(d, 365, 485, .85, YELLOW, 12)
        centered(d, "zwei ähnliche Socken", 770, SUBTITLE)
        paragraph(d, "Manchmal ist die Socke nicht weg – sie steckt noch im Wäschekorb, Ärmel oder unter der Maschine.", 850, SMALL, width=600)
    elif scene == 4:
        centered(d, "DIE UNTERSUCHUNG", 160, SMALL, MINT)
        steps = [("01", "Trommel und Türdichtung ansehen"), ("02", "Bettwäsche und Ärmel ausschütteln"), ("03", "Wäschekorb und Umgebung prüfen")]
        for i, (num, text) in enumerate(steps):
            yy = 360 + i * 155
            d.ellipse((70, yy, 135, yy + 65), fill=MINT)
            d.text((85, yy + 14), num, font=SMALL, fill=BG)
            for j, line in enumerate(wrapped(d, text, SMALL, 440)):
                d.text((165, yy + 5 + j * 36), line, font=SMALL, fill=WHITE)
        paragraph(d, "Filter oder Gerätegehäuse nur nach Anleitung des Herstellers prüfen lassen.", 890, SMALL, YELLOW)
    else:
        centered(d, "FALL GELÖST?", 180, SMALL, MINT)
        sock(d, 265, 360, 1.05, YELLOW, -4)
        centered(d, "Meist steckt eine", 670, TITLE)
        centered(d, "ganz normale Spur", 740, TITLE, YELLOW)
        centered(d, "dahinter.", 810, TITLE)
        paragraph(d, "Und wenn wirklich eine Socke fehlt: Erst die Wäscheladung und Umgebung gründlich absuchen.", 960, SMALL)
        centered(d, "Ende der Akte", 1120, SMALL, MINT)

    # Progress bar and scene label
    progress = min(1.0, (t % SCENE_SECONDS) / SCENE_SECONDS)
    d.rounded_rectangle((55, 1200, 665, 1212), radius=6, fill=(49, 65, 81))
    d.rounded_rectangle((55, 1200, 55 + int(610 * progress), 1212), radius=6, fill=MINT)
    return image


def main():
    total_frames = 6 * SCENE_SECONDS * FPS
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(OUTPUT),
    ]
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        assert process.stdin is not None
        for frame_no in range(total_frames):
            elapsed = frame_no / FPS
            scene = min(int(elapsed // SCENE_SECONDS), 5)
            frame = scene_frame(scene, elapsed)
            process.stdin.write(frame.tobytes())
            if frame_no % (FPS * 5) == 0:
                print(f"Rendere {frame_no}/{total_frames} Frames…", flush=True)
        process.stdin.close()
        result = process.wait()
        if result:
            raise subprocess.CalledProcessError(result, command)
    except (BrokenPipeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Video konnte nicht erstellt werden: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Fertig: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
