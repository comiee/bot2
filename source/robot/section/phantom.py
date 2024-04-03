from public.message import phantom_msg
from public.utils import save_image, get_pic_url_from_internal
from public.config import data_path
from robot.comm.pluginBase import Session
from robot.comm.command import SplitArgCommand
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.message import MiraiMessageSegment


@SplitArgCommand('幻影', ['请输入第一张图片', '请输入第二张图片'])
async def phantom(session: Session, pic_internal_1, pic_internal_2):
    try:
        pic_url_1 = get_pic_url_from_internal(pic_internal_1)
        pic_url_2 = get_pic_url_from_internal(pic_internal_2)
    except AssertionError:
        await session.reply('未发现图片')
        return

    pic_path_1 = data_path('phantom', 'pic1.jpg')
    pic_path_2 = data_path('phantom', 'pic2.jpg')
    await save_image(pic_url_1, pic_path_1)
    await save_image(pic_url_2, pic_path_2)

    res_path = get_bot_client().send(phantom_msg.build(path1=pic_path_1, path2=pic_path_2))
    await session.reply(MiraiMessageSegment.image(path=res_path))
