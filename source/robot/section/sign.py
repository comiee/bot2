from public.message import sign_in_msg
from public.error_code import ErrorCode
from public.log import bot_logger
from public.currency import Currency
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand
from robot.botClient import get_bot_client


@FullCommand('签到')
async def sign(session: Session):
    ret = get_bot_client().send(sign_in_msg.build(user_id=session.qq))
    match ret:
        case ErrorCode.success:
            coin = session.user.query(Currency.coin)
            await session.reply(f'签到成功，金币+10，体力恢复为200，当前金币{coin}', at=True)
        case ErrorCode.already_signed:
            await session.reply('你今天已经签到过了，明天再来吧。', at=True)
        case ErrorCode.sql_disconnected:
            await session.reply('数据库连接失败，请联系小魅的主人。', at=True)
        case _:
            bot_logger.error(f'预期外的错误码：{ret}')
            await session.reply(f'遇到了预期外的错误，请联系小魅的主人，错误码：{ret}')
