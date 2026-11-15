"""Vẽ icon ổ khoá màu hồng cho ứng dụng (cần Pillow):  python tools/make_icon.py"""

import os

from PIL import Image, ImageDraw

SIZE = 512
PINK_TOP, PINK_BOTTOM = (249, 168, 212), (236, 72, 153)
WHITE, DEEP = (255, 255, 255, 255), (190, 24, 93, 255)


def draw_icon() -> Image.Image:
    gradient = Image.new("RGBA", (SIZE, SIZE))
    pixels = ImageDraw.Draw(gradient)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(PINK_TOP, PINK_BOTTOM)) + (255,)
        pixels.line([(0, y), (SIZE, y)], fill=color)
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([8, 8, SIZE - 8, SIZE - 8], radius=120, fill=255)
    icon = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    icon.paste(gradient, (0, 0), mask)

    draw = ImageDraw.Draw(icon)
    draw.arc([166, 96, 346, 300], start=180, end=360, fill=WHITE, width=40)          # quai khoá
    draw.line([(186, 196), (186, 250)], fill=WHITE, width=40)
    draw.line([(326, 196), (326, 250)], fill=WHITE, width=40)
    draw.rounded_rectangle([118, 232, 394, 420], radius=44, fill=WHITE)             # thân khoá
    # trái tim ở giữa thân khoá
    draw.ellipse([204, 282, 262, 340], fill=DEEP)
    draw.ellipse([250, 282, 308, 340], fill=DEEP)
    draw.polygon([(207, 322), (305, 322), (256, 386)], fill=DEEP)
    return icon


if __name__ == "__main__":
    target = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(target, exist_ok=True)
    image = draw_icon()
    image.save(os.path.join(target, "icon.ico"),
               sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    image.resize((256, 256), Image.LANCZOS).save(os.path.join(target, "icon.png"))
    print("Đã tạo assets/icon.ico")
