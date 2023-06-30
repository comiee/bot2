import asyncio
import json


class ClientProtocol(asyncio.Protocol):
    def connection_made(self, transport: asyncio.transports.Transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

        self.transport.write('{"msg":"hi"}'.encode())

    def data_received(self, data):
        message = data.decode()
        result = self.parse(message)
        self.transport.write(json.dumps(result).encode())

    def connection_lost(self, exc):
        print('The connection closed')
        self.transport.close()

    def send(self, msg):
        self.transport.write(msg.encode())

    async def main(self, host, port):
        # Get a reference to the event loop as we plan to use
        # low-level APIs.
        loop = asyncio.get_running_loop()
        await loop.create_connection(lambda: self, host, port)
        await loop.create_future()

    def run(self, host, port, *coroutines):
        asyncio.run(asyncio.gather(self.main(host, port), *coroutines))

    def parse(self, message):
        print('已接收：' + message)
        return {"msg":input()}


asyncio.run(ClientProtocol().main('127.0.0.1', 8888))
