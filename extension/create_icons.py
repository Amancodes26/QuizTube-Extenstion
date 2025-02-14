from PIL import Image, ImageDraw

def create_icon(size):
    img = Image.new('RGB', (size, size), color='red')
    draw = ImageDraw.Draw(img)
    draw.text((size/4, size/4), f"YT", fill='white', size=size//2)
    img.save(f'icon{size}.png')

for size in [16, 48, 128]:
    create_icon(size)
