from communication import message
from robot.comm.priority import Priority
from robot.botClient import get_bot_client
from robot.comm.pluginBase import Session
from robot.comm.command import SplitCommand, SplitArgCommand
from alicebot.adapter.mirai.event import MessageEvent


class TestPlugin(Session, priority=Priority.Chat):
    async def handle(self) -> None:
        client = get_bot_client()
        args = self.event.get_plain_text().split(maxsplit=1)[1:]
        print(233)
        if len(args) != 1:
            event = await self.event.ask('请输入内容')
            text = event.get_plain_text()
        else:
            text = args[0]
        user = self.event.sender.id
        ret = client.send(message.chat_msg.build(user_id=user, text=text))
        await self.event.reply(ret)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        if not self.event.get_plain_text():
            return False
        return self.event.get_plain_text().split()[0] == '/chat'


@SplitCommand('/split')
async def test_split(session: Session, x):
    await session.reply(f'split {x=}')


@SplitCommand('/split')
async def test_split(session: Session, x, y):
    await session.reply(f'split {x=}, {y=}')


@SplitArgCommand('/arg', ['请输入x', '请输入y'], '参数过多', 10)
async def test_split_arg(session: Session, x, y):
    await session.reply(f'参数为 {x=}, {y=}')
