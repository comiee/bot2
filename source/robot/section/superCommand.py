from public.currency import Currency
from public.message import debug_msg, sql_msg
from public.convert import convert_to
from robot.comm.command import get_command_cls_list, NormalCommand, RegexCommand, FullCommand, SplitCommand
from robot.comm.pluginBase import Session
from robot.comm.user import User
from robot.botClient import get_bot_client
import re

__all__ = []


@RegexCommand(re.compile(r'^exec\s(.*)$', re.S)).trim_super()
async def exec_code(session: Session, text: str):
    text = convert_to('plain', text)
    exec('async def func(session):\n\t' + text.replace('\n', '\n\t'))
    ret = await eval('func(session)')
    if ret is not None:
        await session.reply(str(ret))


@RegexCommand(re.compile(r'^eval\s(.*)$', re.S)).trim_super()
async def eval_code(session: Session, text: str):
    text = convert_to('plain', text)
    ret = eval(text)
    await session.reply(str(ret))


@RegexCommand(re.compile(r'^sql\s(.*)$', re.S)).trim_super()
async def exec_sql(session: Session, sql: str):
    sql = convert_to('plain', sql)
    res = get_bot_client().send(sql_msg.build(sql))
    await session.reply(res)


@NormalCommand('debug ').trim_super()
def debug(_: Session, text: str):
    get_bot_client().send(debug_msg.build(text))


@FullCommand('show_cmd').trim_super()
async def show_cmd(session: Session):
    temp = []
    for command_cls in get_command_cls_list():
        for command in command_cls.commands:
            temp.append(repr(command))
    await session.reply('\n'.join(temp))


@SplitCommand('gain').trim_super()
async def gain(session: Session, user: str, num: str):
    await gain(session, user, num, 'coin')


@SplitCommand('gain').trim_super()
async def gain(session: Session, user_str: str, num_str: str, currency_str: str):
    user = User(user_str)
    num = int(num_str)
    currency = Currency[currency_str]
    old = user.query(currency)
    user.gain(num, currency)
    new = user.query(currency)
    await session.reply(f'执行成功，用户{user} {currency.value} {old}->{new}')


@NormalCommand('gain').trim_super()
async def gain_(session: Session, _):  # 函数名不能是gain，会破坏重载
    message_list = list(session.event.message)  # 列表第一项为MessageSegment<Source>，计算长度要+1
    if len(message_list) == 4 \
            and message_list[1].type == 'Plain' and str(message_list[1]).strip() == 'gain' \
            and message_list[2].type == 'At' \
            and message_list[3].type == 'Plain':
        args = str(message_list[3]).strip().split()
        if len(args) == 1 or len(args) == 2:
            num, currency, *_ = *args, 'coin'
            # SplitCommand的重载是用多个不同的命令实现的，此处只能调用最后一次定义的函数
            await gain(session, message_list[2].data['target'], num, currency)
            return
    session.skip()

# TODO 保存自定义代码
