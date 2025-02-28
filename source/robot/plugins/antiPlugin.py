from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase, Session
from robot.comm.user import User
from alicebot.adapter.mirai.event import FriendRecallEvent, GroupRecallEvent, MessageEvent
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment


class AntiFriendRecallPlugin(PluginBase, priority=Priority.Anti):
    async def handle(self) -> None:
        target = self.event.authorId
        try:
            ret = await self.call_api('messageFromId',
                                      messageId=self.event.messageId,
                                      target=target)
        except Exception:
            return
        reply_message = MiraiMessage('撤回也没用，我已经看见了，你刚才发送的是：\n', ret['data']['messageChain'])
        await self.send(reply_message, 'friend', target)

    async def rule(self) -> bool:
        if not isinstance(self.event, FriendRecallEvent):
            return False
        if User(self.event.authorId).is_super_user():
            return False
        return True


class AntiGroupRecallPlugin(PluginBase, priority=Priority.Anti):
    async def handle(self) -> None:
        group = self.event.group.id
        try:
            ret = await self.call_api('messageFromId',
                                      messageId=self.event.messageId,
                                      target=group)
        except Exception:
            return
        author = self.event.authorId
        operator = self.event.operator.id
        if operator == author:
            head_message = MiraiMessageSegment.at(operator) + '撤回也没用，我已经看见了，你刚才发送的是：\n'
        else:
            head_message = MiraiMessageSegment.at(operator) + '撤回也没用，我已经看见了，' + \
                           MiraiMessageSegment.at(author) + '刚才发送的是：\n'
        reply_message = MiraiMessage(head_message, ret['data']['messageChain'])
        await self.send(reply_message, 'group', group)

    async def rule(self) -> bool:
        if not isinstance(self.event, GroupRecallEvent):
            return False
        if User(self.event.operator.id).is_super_user():
            return False
        return True


class AntiFlashPlugin(Session[str, None], priority=Priority.Anti):
    async def handle(self) -> None:
        await self.reply('发闪照太见外了，我帮你直接发出来吧\n' + MiraiMessageSegment.image(self.state), at=True)

    async def rule(self) -> bool:
        if not isinstance(self.event, MessageEvent):
            return False
        for msg_seg in self.event.message:
            if msg_seg.type == 'FlashImage':
                self.state = msg_seg['imageId']
                return True
        return False
