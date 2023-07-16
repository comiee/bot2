from robot.comm import priority
from robot.botClient import get_bot_client
from communication import message
from alicebot import Plugin
from alicebot.adapter.mirai.event import MessageEvent

logger = get_bot_client().logger


class ChatPlugin(Plugin):
    priority = priority.CHAT
    block = False

    async def handle(self) -> None:
        client = get_bot_client()
        args = self.event.get_plain_text().split(maxsplit=1)[1:]
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
