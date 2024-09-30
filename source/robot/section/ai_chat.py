from communication.asyncClient import AsyncClient
from robot.comm.command import SplitCommand, NormalCommand
from robot.comm.pluginBase import Session


@SplitCommand('ai')
@SplitCommand('AI')
async def ai_chat(session: Session, text: str):
    async with AsyncClient('ai_chat') as client:
        ret = await client.send(text)
        await session.reply(ret)


@NormalCommand('猫娘')
async def ai_cat(session: Session, text: str):
    async with AsyncClient('ai_cat') as client:
        ret = await client.send(text)
        await session.reply(ret)
