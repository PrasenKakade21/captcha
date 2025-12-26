import random
import string
from PIL import Image, ImageDraw, ImageFont
import math
import io
# Function to generate random CAPTCHA text
def generate_captcha_text(length=6):
    characters = string.ascii_uppercase + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(length))
    return captcha_text


def wave_distortion(img):
    width, height = img.size
    new_img = Image.new("RGB", (width, height), "white")
    for x in range(width):
        for y in range(height):
            new_y = int(y + 5 * math.sin(2 * math.pi * x / 60))
            if 0 <= new_y < height:
                new_img.putpixel((x, y), img.getpixel((x, new_y)))
    return new_img

# Function to generate CAPTCHA image
def generate_captcha_image(captcha_text):
    width, height = 200, 80
    w, h = 200, 80
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Load font (use default if font file not available)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # Draw text
    text_x = 20
    text_y = 20
    draw.text((text_x, text_y), captcha_text, fill='black', font=font)
    
    for i in range(100):
        draw.point(
            (random.randint(0,w), random.randint(0,h)),
            fill="black"
    )

    # Add noise lines
    for i in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill='gray', width=2)
    
    # image = wave_distortion(image)
    buffer = io.BytesIO()
    image.save("captcha.png")
    image.save(buffer,format="PNG")
    # buffer.write(image)
    buffer.seek(0)
    return buffer.getvalue()


# Main Program
def generate_captcha(data): 
    captcha_text = generate_captcha_text()
    captcha_buffer = generate_captcha_image(captcha_text)
    return captcha_text,captcha_buffer
    

