from communication.asyncClient import AsyncClient
from robot.comm.command import SplitArgCommand, RegexCommand
from robot.comm.pluginBase import Session


@SplitArgCommand('百科', ['请输入要查询的内容：'])
@RegexCommand(r'^(?:什么|谁)是(.*)')
@RegexCommand(r'(.*)是(?:什么|谁)$')
async def baike(session: Session, question: str):
    async with AsyncClient('baike') as client:
        res = await client.send(question)
        res += '\n————来自百度百科'
        await session.reply(res)
