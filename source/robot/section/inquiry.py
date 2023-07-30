from public.currency import Currency
from robot.comm.command import FullCommand
from robot.comm.pluginBase import Session


@FullCommand('金币')
async def coin_inquiry(session: Session):
    coin = session.user.query(Currency.coin)
    await session.reply(f'金币数：{coin}', at=True)
