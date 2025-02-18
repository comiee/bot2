from public.currency import Currency
from robot.comm.command import FullCommand
from robot.comm.pluginBase import Session


@FullCommand('金币')
async def coin_inquiry(session: Session):
    coin = session.user.query(Currency.coin)
    await session.reply(f'金币数：{coin}', at=True)


@FullCommand('体力')
async def stamina_inquiry(session: Session):
    stamina = session.user.query(Currency.stamina)
    await session.reply(f'体力值：{stamina}', at=True)


# @FullCommand('金币排行').trim_group('请在群聊中使用此命令')
async def coin_rank(session: Session):
    # TODO 封装一个通用排行消息，在服务器端处理
    pass
