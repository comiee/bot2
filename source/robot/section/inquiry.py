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
