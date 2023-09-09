from robot.comm.pluginBase import Session
from robot.comm.command import SplitCommand, SplitArgCommand
from alicebot import Plugin
from alicebot.adapter.mirai import MiraiAdapter
from alicebot.adapter.mirai.event import GroupMessage
from alicebot.adapter.mirai.exceptions import ActionFailed


class MutePlugin(Plugin[GroupMessage, int, None]):

    async def handle(self) -> None:
        try:
            await self.bot.get_adapter(MiraiAdapter).call_api('mute', target=self.event.sender.group.id, memberId=self.state, time=1)
        except ActionFailed as e:
            await self.event.reply(str(e.resp))
        else:
            await self.event.reply('done')

    async def rule(self) -> bool:
        if not isinstance(self.event, GroupMessage):
            return False
        args = self.event.get_plain_text().strip().split()
        if len(args) != 2 or args[0] != '/mute' or not args[1].isdigit():
            return False
        self.state = int(args[1])
        return True


@SplitCommand('/split')
async def test_split(session: Session, x):
    await session.reply(f'split {x=}')


@SplitCommand('/split')
async def test_split(session: Session, x, y):
    await session.reply(f'split {x=}, {y=}')


@SplitArgCommand('/arg', ['请输入x', '请输入y'], '参数过多', 10)
async def test_split_arg(session: Session, x, y):
    await session.reply(f'参数为 {x=}, {y=}')
