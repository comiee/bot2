from public.message import chat_msg
from robot.comm.priority import Priority
from robot.botClient import get_bot_client
from robot.comm.pluginBase import Session
from robot.comm.command import SplitCommand, SplitArgCommand


@SplitCommand('/split')
async def test_split(session: Session, x):
    await session.reply(f'split {x=}')


@SplitCommand('/split')
async def test_split(session: Session, x, y):
    await session.reply(f'split {x=}, {y=}')


@SplitArgCommand('/arg', ['请输入x', '请输入y'], '参数过多', 10)
async def test_split_arg(session: Session, x, y):
    await session.reply(f'参数为 {x=}, {y=}')
