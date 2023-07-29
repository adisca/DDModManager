from PIL import Image
import io
import os


def resize_img(src, new_size):
    img = Image.open(src)

    cur_width, cur_height = img.size
    if new_size:
        new_width, new_height = new_size
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)))

    img_png = io.BytesIO()
    img.save(img_png, format="PNG")
    return img_png.getvalue()


def mods_path(gameFolder):
    return os.path.join(gameFolder, "mods")
