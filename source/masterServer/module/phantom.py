from public.message import phantom_msg
from public.config import data_path
from PIL import Image


def main(img2, img1):
    img1_g = img1.convert("L")
    img2_g = img2.convert("L")
    img2_r = img2_g.resize((int(img1_g.width), int(img1_g.height)))  # 可调大小
    img1_g = img1_g.resize((int(img1_g.width), int(img1_g.height)))
    img1 = light_degree(img1_g, 0)
    img2 = light_degree(img2_r, 1)
    line = opposed_line(img2, img1)
    divided = divide(img1, line)
    return final(divided, line)


def light_degree(img, i):
    if i > 0:
        img = img.point(lambda x: x * 1.1)
    else:
        img = img.point(lambda x: x * 0.3)
    return img


# noinspection SpellCheckingInspection
def opposed_line(img2, img1):
    imgb = img2.load()
    imga = img1.load()
    for x in range(0, img2.width, 1):
        for y in range(0, img2.height, 1):
            b = imgb[x, y]
            a = imga[x, y]
            color = (255 - b + a,)
            if color > (220,):
                imgb[x, y] = (160 - b + a,)
            else:
                imgb[x, y] = color
    return img2


# noinspection PyPep8Naming,SpellCheckingInspection
def divide(img1, imgO):
    imga = img1.load()
    imgo = imgO.load()
    for x in range(0, img1.width, 1):
        for y in range(0, img1.height, 1):
            A = imga[x, y]
            O = imgo[x, y]
            if O == 0:
                color = (int(A * 0.3),)
            elif A / O >= 1:
                color = (int(A * 6.2),)
            else:
                color = (int(255 * A / O),)
            imga[x, y] = color
    return img1


# noinspection PyPep8Naming
def final(divided, line):
    LINE = line.load()
    divided_RGBA = divided.convert("RGBA")
    DIV_RGBA = divided_RGBA.load()
    line = line.convert("RGBA")
    for x in range(0, line.width, 1):
        for y in range(0, line.height, 1):
            DIV_RGBA[x, y] = (DIV_RGBA[x, y][0], DIV_RGBA[x, y][1], DIV_RGBA[x, y][2], LINE[x, y])
    return divided_RGBA


@phantom_msg.on_receive
def phantom(path1: str, path2: str) -> str:
    res = main(Image.open(path1), Image.open(path2))
    res_path = data_path('phantom', 'res.png')
    res.save(res_path)
    return res_path
