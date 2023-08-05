from robot.comm.priority import Priority
from robot.comm.pluginBase import PluginBase
from alicebot.adapter.mirai.event import FriendRecallEvent, GroupRecallEvent
from alicebot.adapter.mirai.message import MiraiMessage, MiraiMessageSegment


class AntiFriendRecallPlugin(PluginBase, priority=Priority.AntiRecall):
    async def handle(self) -> None:
        target = self.event.authorId
        try:
            ret = await self.call_api('messageFromId',
                                      messageId=self.event.messageId,
                                      target=target)
        except:
            return
        reply_message = MiraiMessage(['撤回也没用，我已经看见了，你刚才发送的是：\n'] + ret['data']['messageChain'])
        await self.send(reply_message, 'friend', target)

    async def rule(self) -> bool:
        if isinstance(self.event, FriendRecallEvent):
            return True


class AntiGroupRecallPlugin(PluginBase, priority=Priority.AntiRecall):
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
        reply_message = MiraiMessage([head_message] + ret['data']['messageChain'])
        await self.send(reply_message, 'group', group)

    async def rule(self) -> bool:
        if isinstance(self.event, GroupRecallEvent):
            return True
