from public.message import p24_start_msg, p24_game_msg, p24_over_msg
from public.error_code import ErrorCode
from public.convert import convert_to
from robot.comm.priority import Priority
from robot.comm.pluginBase import Session
from robot.comm.status import P24GameStatus
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.event import MessageEvent


class P24GamePlugin(Session, priority=Priority.Game):
    p24_game_state: P24GameStatus = P24GameStatus

    async def game_start(self):
        self.p24_game_state.in_game = True
        self.p24_game_state.question = get_bot_client().send(p24_start_msg.build(
            group_id=self.id,
        ))
        await self.reply(f'''\
24点游戏开始！不玩了请说“不玩了”哦。
游戏规则：
随机抽取4个1~9的数字，请通过运算得到24（所有的数必须全部使用且只能使用一次）。
答对得5分，得分自动转为金币。
可用的运算符如下（^代表乘方）：
+ - * / ^ ( )
第一题：{self.p24_game_state.question}''')

    async def game_run(self):
        if self.p24_game_state.add_count_and_check_has_limited():
            await self.reply('答错次数过多，自动结束游戏')
            await self.game_over()
            return

        ret, self.p24_game_state.question = get_bot_client().send(p24_game_msg.build(
            group_id=self.id,
            user_id=self.qq,
            answer=self.plain,
        ))
        match ret:
            case ErrorCode.correct_answer:
                await self.reply(f'答对，加五分！\n下一题：{self.p24_game_state.question}', at=True)
            case ErrorCode.wrong_answer:
                await self.reply('这个式子的结果不是24，再好好想想吧')
            case ErrorCode.not_compliant_rule:
                await self.reply('不对啦，所有的数必须全部使用且只能使用一次')
            case ErrorCode.not_equation:
                await self.reply('你在逗我吗？这压根就不是个式子')
            case _:
                await self.handle_error(ret)

    async def game_over(self):
        self.p24_game_state.in_game = False
        score = get_bot_client().send(p24_over_msg.build(
            group_id=self.id,
        ))
        if self.is_group():
            text = '\n'.join(f'[at:{k}]\t{v}' for k, v in score)
        else:
            text = '\n'.join(f'{k}\t{v}' for k, v in score)
        await self.reply(convert_to('mirai', f'24点游戏结束！得分情况：\n{text}\n下次想玩还可以找我哦。'))

    async def handle(self) -> None:
        match self.plain:
            case '24点':
                if self.p24_game_state.in_game:
                    await self.reply(f'24点游戏已经开始啦，现在的题目是{self.p24_game_state.question}')
                else:
                    await self.game_start()
            case '不玩了':
                await self.game_over()
            case _:
                await self.game_run()

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False

        if self.p24_game_state.in_game:
            return True
        if self.plain == '24点':
            return True
        return False
