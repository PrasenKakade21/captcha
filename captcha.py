from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import io
import math
# ---------------------------
# Text / Base Image Generator
# ---------------------------
def generate_base_image(text, size=(200, 70), color='black'):
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    font_size = int(size[1] *0.6)
    font = ImageFont.load_default(font_size)  # Use truetype if needed
    
    x_offset = 10
    for char in text:
        if isinstance(color, list):
            fill = random.choice(color)
        elif color == 'multicolor':
            fill = "#" + "".join(random.choices('0123456789ABCDEFGHIJKLMONPQRSTUVWXYZ', k=6))
        else:
            fill = color
        draw.text((x_offset, (size[1]-font_size)//2), char, fill=fill, font=font)
        x_offset += font_size * 0.8
    print((size[1]-font_size/2)//2,font_size)
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

def apply_distortion(img, distort='none'):
    if distort == 'wave':
        img = wave_distortion(img)
    elif distort == 'blur':
        img = img.filter(ImageFilter.GaussianBlur(2))
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
