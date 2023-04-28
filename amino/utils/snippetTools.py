try:
    import textwrap
    from PIL import Image, ImageDraw, ImageFont
except: raise Exception("You haven't Pillow to work with link snippets!\nInstall it by using this command:\n\npip install -U Pillow")

import io
import base64
from typing import Union, BinaryIO

class SnippetTools:
    @staticmethod
    def makeCommunity(title: str, body: str, image: BinaryIO, font_size = 22, titleFont: str = "arial.ttf", bodyFont: str = "arial.ttf"):
        canvas = Image.new("RGB", (807, 396), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

    def makeUser(title: str, body: str, image: BinaryIO, font_size = 22, titleFont: str = "arial.ttf", bodyFont: str = "arial.ttf"):
        canvas = Image.new("RGB", (807, 216), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

    @staticmethod
    def makeBlog(title: str, body: str, image: BinaryIO = None, font_size = 22, titleFont: str = "arial.ttf", bodyFont: str = "arial.ttf"):
        canvas = Image.new("RGB", (807, 662) if image else (807, 218), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

    @staticmethod
    def makeLinkSnippet(title: str, body: str, source: str = "created by amino.api", image: BinaryIO = None, font_size: int = 22, titleFont: str = "arial.ttf", bodyFont: str = "arial.ttf"):
        canvas = Image.new("RGB", (807, 201), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        if image is not None:
            img = Image.open(image)
            img = img.resize((170, 170))
            canvas.paste(img, (15, 15))
            x_shift = 197
        else:
            x_shift = 15
        
        draw.text(
            (x_shift, 21),
            title[:120] + "..." if len(title) > 120 else title,
            font=ImageFont.truetype(titleFont, font_size),
            fill=(51, 51, 51)
        )
        
        body_font = ImageFont.truetype(bodyFont, font_size)
        body_x, body_y = x_shift, 75
        body_max_width, body_max_height = 375 - body_x, 135 - body_y

        lines = textwrap.wrap(body, width=int(body_max_width/body_font.getsize(' ')[0]))

        max_lines = int(body_max_height / body_font.getsize(' ')[1])
        lines = lines[:max_lines]

        for i, line in enumerate(lines):
            draw.text(
                (body_x, body_y + i * body_font.getsize(' ')[1] + 5*i),
                line,
                font=body_font,
                fill=(183, 183, 183)
            )
            if i >= 1: break
        
        draw.text((x_shift, 155), source, font=ImageFont.truetype(bodyFont, font_size), fill=(183, 183, 183))

        canvas.save("aaa.PNG")

        return canvas

    @staticmethod
    def prepareImage(image_buffer: BinaryIO, crop=False):
        img = Image.open(io.BytesIO(image_buffer))
        width, height = img.size
        
        if width > 1000 or height > 1000:
            if crop:
                new_width, new_height = 1000 if width > 1000 else width, 1000 if height > 1000 else height
                left = (width - new_width) / 2
                top = (height - new_height) / 2
                right = (width + new_width) / 2
                bottom = (height + new_height) / 2
                img = img.crop((left, top, right, bottom))
            else:
                new_width, new_height = 1000 if width > 1000 else width, 1000 if height > 1000 else height
                img.thumbnail((new_width, new_height))
            
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
            
        return base64.b64encode(buffer.getvalue())
    

