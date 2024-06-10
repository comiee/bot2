from communication.asyncClient import AsyncClient
from public.utils import get_pic_url_from_internal
from robot.comm.pluginBase import Session
from robot.comm.command import SplitArgCommand


@SplitArgCommand('识图', ['请输入图片'])
async def identify_image(session: Session, pic_str):
    async with AsyncClient('identify_image') as client:  # 提前发送cmd过去，让服务器提前打开浏览器
        try:
            url = get_pic_url_from_internal(pic_str)
        except AssertionError:
            await session.reply('未找到图片')
            return
        res = await client.send(url)
        await session.reply('找到以下内容：\n' + '\n'.join(res[:3]))
