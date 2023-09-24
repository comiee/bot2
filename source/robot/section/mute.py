from public.tools import to_int
from public.log import bot_logger
from public.currency import Currency
from robot.comm.pluginBase import Session
from robot.comm.command import SplitArgCommand, RegexCommand
from alicebot.adapter.mirai.exceptions import ActionFailed
import re


@SplitArgCommand('禁言', ['请输入要禁言的人的QQ号', '请输入要禁言的时长（单位：秒）']) \
        .trim_administrator('请在群聊中使用此功能，并确保小魅为管理员')
async def mute_other(session: Session, qq: str, time: str):
    if qq.strip().isdigit():
        qq = int(qq.strip())
    elif m := re.search(r'^\[at:(\d+)]$', qq):
        qq = int(m.group(1))
    else:
        await session.reply('QQ号无效')
        return
    if time.strip().isdigit():
        time = int(time.strip())
    else:
        await session.reply('时长无效')
        return

    await session.check_cost((time, Currency.coin))

    try:
        await session.call_api('mute', target=session.id, memberId=qq, time=time)
    except ActionFailed as e:
        text = f'禁言{qq}失败：{e.resp["data"]["msg"]}'
        bot_logger.warning(text)
        await session.reply(text)
        return

    await session.ensure_cost((time, Currency.coin))
    await session.reply(f'禁言{qq}成功')


@RegexCommand(r'来([\d〇一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟億两貮兆]+).*([秒分时天]).*禁言') \
        .trim_administrator('请在群聊中使用此功能，并确保小魅为管理员')
async def mute_self(session: Session, num: str, unit: str):
    time = to_int(num) * {'秒': 1, '分': 60, '时': 60 * 60, '天': 60 * 60 * 24}[unit]
    try:
        await session.call_api('mute', target=session.id, memberId=session.qq, time=time)
    except ActionFailed as e:
        text = f'禁言{session.qq}失败：{e.resp["data"]["msg"]}'
        bot_logger.warning(text)
        await session.reply(text)
