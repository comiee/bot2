from communication.asyncClient import AsyncClient
from robot.comm.pluginBase import Session
from robot.comm.command import NormalCommand


@NormalCommand('空调学习').trim_super().trim_friend()
async def air_conditioner_learn(session: Session, cmd):
    cmd = cmd.strip()
    async with AsyncClient('air_conditioner_learn') as client:
        await session.reply('开始学习')
        res = await client.send(cmd)
        await session.reply(res)


@NormalCommand('空调').trim_super().trim_friend()
async def air_conditioner_run(session: Session, cmd):
    cmd=cmd.strip()
    async with AsyncClient('air_conditioner_run') as client:
        res = await client.send(cmd)
        await session.reply(res)
