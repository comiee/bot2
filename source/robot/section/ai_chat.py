from communication.asyncClient import AsyncClient
from robot.comm.command import SplitCommand
from robot.comm.pluginBase import Session


@SplitCommand('ai')
@SplitCommand('AI')
async def ai_chat(session: Session, text: str):
    async with AsyncClient('ai_chat') as client:
        ret = await client.send(text)
        await session.reply(ret)