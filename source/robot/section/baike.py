from communication.asyncClient import AsyncClient
from robot.comm.command import SplitArgCommand, RegexCommand
from robot.comm.pluginBase import Session
from robot.comm.status import ChatStatus


def judge_chat(session: Session):
    if not ChatStatus[session.id].switch:
        return False
    if ChatStatus[session.id].at_switch:
        return False
    return True


@SplitArgCommand('百科', ['请输入要查询的内容：'])
@RegexCommand(r'^(?:什么|谁)是(.*)').trim_filter(before=judge_chat)
@RegexCommand(r'(.*)是(?:什么|谁)$').trim_filter(before=judge_chat)
async def baike(session: Session, question: str):
    if not question.strip():
        session.skip()
    async with AsyncClient('baike') as client:
        res = await client.send(question)
        res += '\n————来自百度百科'
        await session.reply(res)
