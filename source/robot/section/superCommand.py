from public.currency import Currency
from public.message import debug_msg, sql_msg
from public.convert import convert_to
from robot.comm.command import get_command_cls_list, NormalCommand, FullCommand, SplitCommand
from robot.comm.pluginBase import Session
from robot.comm.user import User
from robot.botClient import get_bot_client

__all__ = []


@NormalCommand('exec').trim_super()
async def exec_code(session: Session, text: str):
    text = convert_to('plain', text)
    exec('async def func(session):\n\t' + text.replace('\n', '\n\t'))
    ret = await eval('func(session)')
    if ret is not None:
        await session.reply(str(ret))


@NormalCommand('eval').trim_super()
async def eval_code(session: Session, text: str):
    text = convert_to('plain', text)
    ret = eval(text)
    await session.reply(str(ret))


@NormalCommand('sql').trim_super()
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
    user = User(int(''.join(c for c in user_str if c.isdigit())))
    num = int(num_str)
    currency = Currency[currency_str]
    old = user.query(currency)
    user.gain(num, currency)
    new = user.query(currency)
    await session.reply(f'执行成功，用户{user} {currency.value} {old}->{new}')


# TODO 保存自定义代码
