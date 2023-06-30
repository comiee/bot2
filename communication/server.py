import asyncio
import json
import traceback


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport: asyncio.transports.Transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        try:
            message = json.loads(data.decode())
            result = json.dumps(self.parse(message))
            self.transport.write(result.encode())
        except:
            traceback.print_exc()

    def connection_lost(self, exc):
        print('The connection closed')
        self.transport.close()

    def send(self, msg):
        self.transport.write(msg.encode())

    async def main(self, host, port):
        # Get a reference to the event loop as we plan to use
        # low-level APIs.
        loop = asyncio.get_running_loop()
        server = await loop.create_server(lambda: self, host, port)
        async with server:
            await server.serve_forever()

    def parse(self, json_msg):
        """解析数据，参数和返回值都是dict"""
        print(f'[server]recv: {json_msg}')
        return {"msg":"hello"}


asyncio.run(ServerProtocol().main('127.0.0.1', 8888))
