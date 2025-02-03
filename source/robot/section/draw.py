from public.message import draw_msg
from public.error_code import ErrorCode
from robot.comm.pluginBase import Session
from robot.comm.command import SplitArgCommand, RegexCommand
from robot.botClient import get_bot_client

help_str = '''\
花费1体力和1金币进行1次抽奖，概率获得以下物品：
4金币（10%）
2金币（20%）
1金币（30%)
0金币（40%）
请输入抽奖次数：'''


@RegexCommand(r'^抽奖(\d+)$')
@SplitArgCommand('抽奖', [help_str])
async def draw(session: Session, count: str):
    try:
        count = int(count)
        assert count > 0
    except Exception:
        await session.reply('错误的次数，命令已取消')
        return

    ret, result = get_bot_client().send(draw_msg.build(user_id=session.qq, count=count))
    match ret:
        case ErrorCode.success:
            await session.reply(f'''\
已消耗{count}体力和{count}金币进行{count}次抽奖。
抽奖结果如下，欢迎下次再来。
{result}
共{sum(result)}金币''')
        case ErrorCode.invalid_input:
            await session.reply('错误的次数，命令已取消')
        case _:
            await session.handle_error(ret)
