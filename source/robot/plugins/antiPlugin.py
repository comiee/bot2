from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase, Session
from robot.comm.status import AntiStatus
from alicebot.adapter.mirai.event import FriendRecallEvent, GroupRecallEvent, MessageEvent
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment


class AntiFriendRecallPlugin(PluginBase, priority=Priority.Anti):
    anti_status: AntiStatus = AntiStatus  # anti系列功能共用一个status

    async def handle(self) -> None:
        target = self.event.authorId
        try:
            ret = await self.call_api('messageFromId',
                                      messageId=self.event.messageId,
                                      target=target)
        except:
            return
        reply_message = MiraiMessage('撤回也没用，我已经看见了，你刚才发送的是：\n', ret['data']['messageChain'])
        await self.send(reply_message, 'friend', target)

    async def rule(self) -> bool:
        if not self.anti_status.switch:
            return False
        if isinstance(self.event, FriendRecallEvent):
            return True
        return False


class AntiGroupRecallPlugin(PluginBase, priority=Priority.Anti):
    anti_status: AntiStatus = AntiStatus  # anti系列功能共用一个status

    async def handle(self) -> None:
        group = self.event.group.id
        try:
            ret = await self.call_api('messageFromId',
                                      messageId=self.event.messageId,
                                      target=group)
        except:
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
        if not self.anti_status.switch:
            return False
        if isinstance(self.event, GroupRecallEvent):
            return True
        return False


class AntiFlashPlugin(Session[str, None], priority=Priority.Anti):
    anti_status: AntiStatus = AntiStatus  # anti系列功能共用一个status

    async def handle(self) -> None:
        await self.reply('发闪照太见外了，我帮你直接发出来吧\n' + MiraiMessageSegment.image(self.state), at=True)

    async def rule(self) -> bool:
        if not self.anti_status.switch:
            return False
        if not isinstance(self.event, MessageEvent):
            return False
        for msg_seg in self.event.message:
            if msg_seg.type == 'FlashImage':
                self.state = msg_seg['imageId']
                return True
        return False
