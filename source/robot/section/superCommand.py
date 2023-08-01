from public import message
from robot.comm.command import NormalCommand, RegexCommand, FullCommand, get_command_cls_list
from robot.comm.pluginBase import Session
from robot.botClient import get_bot_client
import re


@RegexCommand(re.compile(r'^exec\s(.*)$', re.S)).trim_super()
async def exec_code(session: Session, text: str):
    try:
        exec('async def func(session):\n\t' + text.replace('\n', '\n\t'))
        ret = await eval('func(session)')
        if ret is not None:
            await session.reply(str(ret))
    except Exception as e:
        await session.reply(str(e))


@RegexCommand(re.compile(r'^eval\s(.*)$', re.S)).trim_super()
async def eval_code(session: Session, text: str):
    try:
        ret = eval(text)
        await session.reply(str(ret))
    except Exception as e:
        await session.reply(str(e))


@NormalCommand('debug ').trim_super()
def debug(_: Session, text: str):
    get_bot_client().send(message.debug_msg.build(text))


@FullCommand('show_cmd').trim_super()
async def show_cmd(session: Session):
    temp = []
    for command_cls in get_command_cls_list():
        for command in command_cls.commands:
            temp.append(repr(command))
    await session.reply('\n'.join(temp))

# TODO 保存自定义代码
