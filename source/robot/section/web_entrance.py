from public.config import data_path
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand
import re


@FullCommand('网页版')
async def web_entrance(session: Session):
    log_path = data_path("web", "natapp.txt")  # 与webpage/config.ini内保持一致
    with open(log_path, encoding='utf-8') as f:
        for s in f:
            if m := re.search(r'Tunnel established at (\S+)', s):
                await session.reply(m.group(1))
                return
    await session.reply('未找到网址，natapp可能未启动')
