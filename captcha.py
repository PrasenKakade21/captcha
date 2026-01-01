from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import io
import math
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

# ---------------------------
# Text / Base Image Generator
# ---------------------------
from PIL import Image, ImageDraw, ImageFont
import random

def generate_base_image(text, size=(200, 70), color='black'):
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)

    padding = 10
    font_size = int(size[1] * 0.6)

    # IMPORTANT: Use a TrueType font if possible
    # fallback shown for safety
    try:
        font_path = "DejaVuSans.ttf"
        get_font = lambda fs: ImageFont.truetype(font_path, fs)
    except:
        get_font = lambda fs: ImageFont.load_default()

    # 🔹 Find the largest font size that fits
    while font_size > 5:
        font = get_font(font_size)

        total_width = 0
        for char in text:
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            total_width += char_width + int(font_size * 0.2)  # spacing

        total_width -= int(font_size * 0.2)  # remove last spacing

        if total_width + padding * 2 <= size[0]:
            break

        font_size -= 1

    # 🔹 Draw characters
    x_offset = padding
    for char in text:
        if isinstance(color, list):
            fill = random.choice(color)
        elif color == 'multicolor':
            fill = "#" + "".join(random.choices('0123456789ABCDEF', k=6))
        else:
            fill = color

        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        y = (size[1] - char_height) // 2
        draw.text((x_offset, y), char, fill=fill, font=font)

        x_offset += char_width + int(font_size * 0.2)

    return img

# ---------------------------
# Noise Generator (lines & dots)
# ---------------------------
def add_noise(img, lines=0, dots=0):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    for _ in range(lines):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        line_color = "#" + "".join(random.choices('0123456789ABCDEF', k=6))
        draw.line([start, end], fill=line_color)
    
    for _ in range(dots):
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        dot_color = "#" + "".join(random.choices('0123456789ABCDEF', k=6))
        draw.point((x, y), fill=dot_color)
    
    return img

# ---------------------------
# Distortion Generator
# ---------------------------

def wave_distortion(img):
    width, height = img.size
    new_img = Image.new("RGB", (width, height), "white")
    for x in range(width):
        for y in range(height):
            new_y = int(y + 5 * math.sin(2 * math.pi * x / 60))
            if 0 <= new_y < height:
                new_img.putpixel((x, y), img.getpixel((x, new_y)))
    return new_img
def elastic_distort_light(
    img: Image.Image,
    strength: int = 8,
    grid_size: int = 8
) -> Image.Image:
    """
    strength  → max pixel displacement
    grid_size → smaller = smoother & faster
    """

    w, h = img.size

    # Small random displacement grid
    dx_small = np.random.randint(-strength, strength + 1, (grid_size, grid_size))
    dy_small = np.random.randint(-strength, strength + 1, (grid_size, grid_size))

    # Upscale displacement to image size
    dx = Image.fromarray(dx_small.astype(np.int16)).resize((w, h), Image.BICUBIC)
    dy = Image.fromarray(dy_small.astype(np.int16)).resize((w, h), Image.BICUBIC)

    dx = np.array(dx)
    dy = np.array(dy)

    x, y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = np.clip(x + dx, 0, w - 1).astype(np.int32)
    map_y = np.clip(y + dy, 0, h - 1).astype(np.int32)

    img_np = np.array(img)
    distorted = img_np[map_y, map_x]

    return Image.fromarray(distorted)

def apply_distortion(img, distort='none'):
    if distort == 'wave':
        img = wave_distortion(img)
    elif distort == 'blur':
        img = img.filter(ImageFilter.GaussianBlur(2))
    elif distort == 'elastic':
        img = elastic_distort_light(img, strength=3, grid_size=6)
    return img

# ---------------------------
# Captcha Text Generator
# ---------------------------
def generate_captcha_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ---------------------------
# Main Captcha Generator
# ---------------------------
def generate_captcha(data=None):
    if data is None:
        data = {}
    
    length = data.get('length', 5)
    size = data.get('size', (150, 50))
    color = data.get('color', 'black')
    lines = data.get('lines', 0)
    dots = data.get('dots', 0)
    distort = data.get('distort', 'none')
    
    text = generate_captcha_text(length)
    img = generate_base_image(text, size=size, color=color)
    img = add_noise(img, lines=lines, dots=dots)
    img = apply_distortion(img, distort=distort)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return text, buffer
