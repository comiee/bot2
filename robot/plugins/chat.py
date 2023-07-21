from robot.comm.priority import Priority
from robot.comm.session import Session
from robot.comm.command import SuperCommand
from robot.botClient import get_bot_client
from communication import message
from alicebot.adapter.mirai.event import MessageEvent

logger = get_bot_client().logger


class ChatPlugin(Session, priority=Priority.Chat):
    switch = False

    async def handle(self) -> None:
        client = get_bot_client()
        ret = client.send(message.chat_msg.build(user_id=self.qq, text=self.text))
        await self.event.reply(ret)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        if not self.text:
            return False
        if not self.switch:
            return False
        return True


@SuperCommand('on')
async def chat_on(session: Session):
    ChatPlugin.switch = True
    await session.event.reply('聊天功能开启')


@SuperCommand('off')
async def chat_off(session: Session):
    ChatPlugin.switch = False
    await session.event.reply('聊天功能关闭')
