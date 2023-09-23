from public.message import sign_in_msg
from public.currency import Currency
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand
from robot.botClient import get_bot_client


@FullCommand('签到')
async def sign(session: Session):
    if get_bot_client().send(sign_in_msg.build(user_id=session.qq)):
        coin = session.user.query(Currency.coin)
        await session.reply(f'签到成功，金币+10，体力恢复为200，当前金币{coin}', at=True)
    else:
        await session.reply('你今天已经签到过了，明天再来吧。', at=True)
