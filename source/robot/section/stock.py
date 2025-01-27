from public.message import stock_msg, query_stock_price_msg
from public.error_code import ErrorCode
from public.currency import Currency
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand, RegexCommand
from robot.botClient import get_bot_client


@FullCommand('股市')
@FullCommand('股票')
async def stock_help(session: Session):
    price = get_bot_client().send(query_stock_price_msg.build())
    quantity = session.user.query(Currency.stock)
    money = session.user.query(Currency.coin)
    count = await session.ask(f'''\
当前股价为{price}，你持有的股份为{quantity}，你拥有的金币为{money}。
小魅开机的时候每到整点会随机更新股价（范围1~30）。
买入花费的金币自动向上取整，卖出花费的金币自动向下取整。
请输入操作的股份数量（正数为买入，负数为卖出）：''')
    if price != get_bot_client().send(query_stock_price_msg.build()):
        await session.reply('股价已变动，请重新操作。')
        return
    count = count.replace(' ', '').replace('买入', '').replace('卖出', '-')
    await stock(session, count)


@RegexCommand(r'(?:股市|股票) ?([+\-]?\d+)')
async def stock(session: Session, count: str):
    try:
        count = int(count)
    except Exception:
        await session.reply('错误的输入，命令已取消。')
        return

    ret = get_bot_client().send(stock_msg.build(user_id=session.qq, count=count))
    match ret:
        case ErrorCode.success:
            quantity = session.user.query(Currency.stock)
            money = session.user.query(Currency.coin)
            op = "购买" if count >= 0 else "出售"
            await session.reply(f'{op}成功，当前金币{money}，当前股份{quantity}')
        case _:
            await session.handle_error(ret)


@FullCommand('股价')
@FullCommand('股份')
async def stock_query(session: Session):
    price = get_bot_client().send(query_stock_price_msg.build())
    quantity = session.user.query(Currency.stock)
    await session.reply(f'当前股价为{price}，你持有的股份为{quantity}')
