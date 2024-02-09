from public.message import phantom_msg
from public.convert import convert_to
from public.config import data_path
from robot.comm.pluginBase import Session
from robot.comm.command import SplitArgCommand
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.message import MiraiMessageSegment
import aiohttp


async def save_pic(url, path):
    async with aiohttp.ClientSession() as aio_session:
        async with aio_session.get(url) as resp:
            with open(path, 'wb') as f:
                f.write(await resp.content.read())


async def get_pic_url(pic_internal: str):
    pic_data = convert_to('data', pic_internal)
    assert len(pic_data) >= 1
    pic_dict = pic_data[0]
    assert 'imageId' in pic_dict and 'url' in pic_dict
    return pic_dict['url']


@SplitArgCommand('幻影', ['请输入第一张图片', '请输入第二张图片'])
async def phantom(session: Session, pic_internal_1, pic_internal_2):
    try:
        pic_url_1 = await get_pic_url(pic_internal_1)
        pic_url_2 = await get_pic_url(pic_internal_2)
    except AssertionError:
        await session.reply('未发现图片')
        return

    pic_path_1 = data_path('phantom', 'pic1.jpg')
    pic_path_2 = data_path('phantom', 'pic2.jpg')
    await save_pic(pic_url_1, pic_path_1)
    await save_pic(pic_url_2, pic_path_2)

    res_path = get_bot_client().send(phantom_msg.build(path1=pic_path_1, path2=pic_path_2))
    await session.reply(MiraiMessageSegment.image(path=res_path))
