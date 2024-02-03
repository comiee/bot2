from public.message import momo_calendar_msg
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand
from robot.botClient import get_bot_client


@FullCommand('momo日历')
async def momo_calendar(session: Session):
    path = get_bot_client().send(momo_calendar_msg.build())
    if not path:
        await session.reply('日历生成失败')
        return
    with open(path, encoding='utf-8') as f:
        await session.reply(f.read())
