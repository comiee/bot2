import public.messageDefine
from robot.comm.command import super_command, NormalCommand, RegexCommand
from robot.comm.pluginBase import Session
from robot.botClient import get_bot_client
import re

@super_command(RegexCommand(re.compile(r'^exec\s(.*)$',re.S)))
async def exec_code(session: Session, text: str):
    try:
        exec('async def func(session):\n\t' + text.replace('\n', '\n\t'))
        ret = await eval('func(session)')
        if ret is not None:
            await session.reply(str(ret))
    except Exception as e:
        await session.reply(str(e))


@super_command(RegexCommand(re.compile(r'^eval\s(.*)$',re.S)))
async def eval_code(session: Session, text: str):
    try:
        ret = eval(text)
        await session.reply(str(ret))
    except Exception as e:
        await session.reply(str(e))


@super_command(NormalCommand('debug '))
def debug(_: Session, text: str):
    get_bot_client().send(public.messageDefine.debug_msg.build(text))

# TODO 保存自定义代码
