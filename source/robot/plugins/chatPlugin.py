from public.message import chat_msg
from public.currency import Currency
from public.state import State
from public.log import bot_logger
from robot.comm.priority import Priority
from robot.comm.pluginBase import Session
from robot.comm.command import FullCommand, RegexCommand, SplitCommand
from robot.botClient import get_bot_client
from alicebot.adapter.mirai.event import MessageEvent
from collections import deque
import time
import asyncio


class ChatStatus:
    def __init__(self):
        self.switch: bool = True  # 总开关
        self.at_switch: bool = True  # 是否只有艾特才会回应
        self.interval: float = 3  # 两次回复间间隔的秒数
        # TODO 最大回复次数
        # TODO 回复间隔和回复次数改为所有回复均适用

        self._last_reply_timestamp: float = 0  # 上次处理的时间戳，用于间隔回复
        self._history: deque = deque(maxlen=10)  # 聊天记录

    def save_reply_timestamp(self) -> None:
        self._last_reply_timestamp = time.time()

    def need_wait_time(self) -> float:
        return self._last_reply_timestamp + self.interval - time.time()

    def save_history(self, text):
        self._history.append(text)

    def get_repetitions(self, text):
        n = 0
        for s in reversed(self._history):
            if s == text:
                n += 1
            else:
                break
        return n


class ChatPlugin(Session, priority=Priority.Chat):
    chat_status = State(default_factory=ChatStatus)

    @property
    def status(self) -> ChatStatus:
        return ChatPlugin.chat_status[self.id]

    async def reply(self, message, quote: bool = False, at: bool = False) -> None:
        # 间隔回复
        if self.status.interval:
            while (t := self.status.need_wait_time()) > 0:
                bot_logger.info(f'间隔时间不足，将等待{t}秒后回复：{message}')
                await asyncio.sleep(t)

        self.status.save_reply_timestamp()
        return await super().reply(message, quote, at)

    async def handle(self) -> None:
        # 防复读
        n = self.status.get_repetitions(self.text)
        if 4 <= n <= 6:
            await self.reply(['复读机？', '一直重复一句话有意思吗？', '再这样我就不理你了！'][n - 4])
            return
        elif n > 6:
            return

        text = self.exclude_at_bot_text() if self.status.at_switch else self.text
        client = get_bot_client()
        ret = client.send(
            chat_msg.build(user_id=self.qq, text=text))
        if ret:
            await self.reply(ret)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        self.status.save_history(self.text)

        if not self.status.switch:
            return False
        if self.status.at_switch and not self.is_at_bot():
            return False
        return True


@RegexCommand(r'^(?:聊天|开|开启)$').trim_cost(10, Currency.coin)
@FullCommand('on').trim_super()
async def chat_on(session: Session):
    if ChatPlugin.chat_status[session.id].switch is not True:
        ChatPlugin.chat_status[session.id].switch = True
        await session.reply('聊天功能开启')
    else:
        await session.reply('聊天功能已经是开启状态了哦。')
        session.stop()  # 提前结束防止扣钱


@RegexCommand(r'^(?:闭嘴|关|关闭)$').trim_cost(10, Currency.coin)
@FullCommand('off').trim_super()
async def chat_off(session: Session):
    if ChatPlugin.chat_status[session.id].switch is not False:
        ChatPlugin.chat_status[session.id].switch = False
        await session.reply('聊天功能关闭')
    else:
        await session.reply('我已经闭嘴了，你还要我怎样？')
        session.stop()  # 提前结束防止扣钱


@SplitCommand('chatConfig').trim_super()
async def chat_config(session: Session, option: str, value: str):
    options = ['switch', 'at_switch', 'interval']
    if option not in options:
        return
    setattr(ChatPlugin.chat_status[session.id], option, eval(value))
    bot_logger.info(f'chatPlugin {option}项已设为{value}')
    await session.reply(f'{option}项已设为{value}')


@FullCommand('chatConfigShow').trim_super()
async def chat_config_show(session: Session):
    options = ['switch', 'at_switch', 'interval']
    get = ChatPlugin.chat_status[session.id].__getattribute__
    text = '\n'.join(f'{opt}:{get(opt)}' for opt in options)
    await session.reply(text)
    return
