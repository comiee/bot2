from public.utils import get_pic_url_from_internal, open_image
from public.config import data_path
from robot.comm.command import SplitArgCommand
from robot.comm.pluginBase import Session
from alicebot.adapter.mirai.message import MiraiMessageSegment
from PIL import Image


def paste_step_number(jpg_image, png_image):
    # 确保PNG图片与JPG图片大小相同
    png_image = png_image.resize(jpg_image.size)

    # 将PNG图片叠加到JPG图片上
    jpg_image.paste(png_image, (0, 0), png_image)

    return jpg_image


@SplitArgCommand('步数', ['请输入图片'])
async def step_number(session: Session, pic_str):
    try:
        url = get_pic_url_from_internal(pic_str)
    except AssertionError:
        await session.reply('未找到图片')
        return
    result = paste_step_number(
        await open_image(url),
        Image.open(data_path('step_number', '1.png'))
    )
    path = data_path('step_number', 'result.jpg')
    result.save(path)
    await session.reply(MiraiMessageSegment.image(path=path))
