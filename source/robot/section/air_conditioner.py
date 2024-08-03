from communication.asyncClient import AsyncClient
from robot.comm.pluginBase import Session
from robot.comm.command import NormalCommand, FullCommand


@NormalCommand('空调学习').trim_super().trim_friend()
async def air_conditioner_learn(session: Session, cmd):
    cmd = cmd.strip()
    async with AsyncClient('air_conditioner_get_all') as client:
        cmds = await client.send('')
        if cmd in cmds:
            await session.reply(f'已有同名命令，当前已学习的命令：{cmds}')
            return
    async with AsyncClient('air_conditioner_learn') as client:
        await session.reply('开始学习')
        res = await client.send(cmd)
        await session.reply(res)


@NormalCommand('空调删除').trim_super().trim_friend()
async def air_conditioner_remove(session: Session, cmd):
    cmd = cmd.strip()
    async with AsyncClient('air_conditioner_remove') as client:
        res = await client.send(cmd)
        await session.reply(res)


@FullCommand('空调检查').trim_super().trim_friend()
async def air_conditioner_check(session: Session):
    async with AsyncClient('air_conditioner_check') as client:
        res = await client.send('')  # 发送空字符串提高兼容性，服务器不会使用这个参数
        await session.reply(res)


@NormalCommand('空调').trim_super().trim_friend()  # 这条放在最后，防止匹配不到其他的
async def air_conditioner_run(session: Session, cmd):
    cmd = cmd.strip()
    async with AsyncClient('air_conditioner_run') as client:
        res = await client.send(cmd)
        await session.reply(res)
