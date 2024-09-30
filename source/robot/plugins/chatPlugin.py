from communication.asyncClient import AsyncClient
from public.message import chat_msg
from public.convert import convert_to
from robot.comm.priority import Priority
from robot.comm.pluginBase import Session
from robot.comm.status import ChatStatus
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.event import MessageEvent


class ChatPlugin(Session, priority=Priority.Chat):
    chat_state: ChatStatus = ChatStatus

    async def handle(self) -> None:
        # 防复读
        n = self.chat_state.get_repetitions(self.text)
        if 4 <= n <= 6:
            await self.reply(['复读机？', '一直重复一句话有意思吗？', '再这样我就不理你了！'][n - 4])
            return
        elif n > 6:
            return

        client = get_bot_client()
        ret = client.send(chat_msg.build(
            user_id=self.qq,
            group_id=self.id if self.is_group() else 0,
            text=self.exclude_at_bot_text(),
        ))
        if ret:
            await self.reply(convert_to('mirai', ret))
            self.stop()

        if self.is_at_bot():
            async with AsyncClient('ai_chat') as client:
                ret = await client.send(self.exclude_at_bot_text())
                await self.reply(ret)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        self.chat_state.save_history(self.text)

        if not self.chat_state.switch:
            return False
        if self.chat_state.at_switch and not self.is_at_bot():
            return False
        return True
