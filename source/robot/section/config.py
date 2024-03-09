from public.currency import Currency
from public.log import bot_logger
from robot.comm.status import status_dict, ChatStatus
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand, RegexCommand, SplitCommand


@RegexCommand(r'^(?:聊天|开|开启)$').trim_group('聊天开关只在群聊中有效哦').trim_cost((10, Currency.coin))
@FullCommand('on').trim_super()
async def chat_on(session: Session):
    if ChatStatus[session.id].at_switch is not False:
        ChatStatus[session.id].at_switch = False
        await session.reply('聊天功能开启，快来和小魅聊天吧！')
    else:
        await session.reply('聊天功能已经是开启状态了哦。')
        session.stop()  # 提前结束防止扣钱


@RegexCommand(r'^(?:闭嘴|关|关闭)$').trim_group('聊天开关只在群聊中有效哦').trim_cost((10, Currency.coin))
@FullCommand('off').trim_super()
async def chat_off(session: Session):
    if ChatStatus[session.id].at_switch is not True:
        ChatStatus[session.id].at_switch = True
        await session.reply('聊天功能关闭，不过艾特小魅的话，小魅还是会回复的。')
    else:
        await session.reply('我已经闭嘴了，你还要我怎样？')
        session.stop()  # 提前结束防止扣钱


@SplitCommand('config').trim_super()
async def config(session: Session, option: str, value: str):
    for name, status_cls in status_dict.items():
        if option in status_cls.options:
            await config(session, name, option, value)


@SplitCommand('config').trim_super()
async def config(session: Session, name: str, option: str, value: str):
    # 使用的super命令，不用判断是否含有成员，报错会打印
    status_cls = status_dict[name]
    setattr(status_cls[session.id], option, eval(value))
    text = f'{name} {option}项已设为{value}'
    bot_logger.info(text)
    await session.reply(text)


@FullCommand('config show').trim_super()
async def config_show(session: Session):
    text_list = []
    for name, status_cls in status_dict.items():
        text_list.append(f'{name}:')
        for option in status_cls.options:
            value = getattr(status_cls[session.id], option)
            text_list.append(f'\t{option}: {value}')
    await session.reply('\n'.join(text_list))
