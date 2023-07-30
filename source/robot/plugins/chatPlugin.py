from public import message
from public.currency import Currency
from robot.comm.priority import Priority
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand, RegexCommand
from robot.comm.state import State
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.event import MessageEvent


class ChatPlugin(Session, priority=Priority.Chat):
    switch = State(False)

    async def handle(self) -> None:
        client = get_bot_client()
        ret = client.send(
            message.chat_msg.build(user_id=self.qq, text=self.msg))  # TODO 图片等消息如何传递给服务器？计划将其转换为通用的转义格式
        await self.reply(ret)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        if not ChatPlugin.switch[self.id]:
            return False
        return True

    @RegexCommand(r'^(?:聊天|开|开启)$').trim_cost(10, Currency.coin)
    @FullCommand('on').trim_super()
    async def chat_on(self):
        if ChatPlugin.switch[self.id] is not True:
            ChatPlugin.switch[self.id] = True
            await self.reply('聊天功能开启')
        else:
            await self.reply('聊天功能已经是开启状态了哦。')
            self.stop()  # 提前结束防止扣钱

    @RegexCommand(r'^(?:闭嘴|关|关闭)$').trim_cost(10, Currency.coin)
    @FullCommand('off').trim_super()
    async def chat_off(self):
        if ChatPlugin.switch[self.id] is not False:
            ChatPlugin.switch[self.id] = False
            await self.reply('聊天功能关闭')
        else:
            await self.reply('我已经闭嘴了，你还要我怎样？')
            self.stop()  # 提前结束防止扣钱
