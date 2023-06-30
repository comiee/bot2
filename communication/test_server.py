from communication.server import ServerProtocol

async def f(server):
    while True:
        server.send('msg\n')
        await