import asyncio
import time


class EchoServerProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport: asyncio.transports.Transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self.addr = addr
        print('addr:', addr)
        #self.data_received(data)

    def eof_received(self, *args):
        print('eof_received', *args)

    def send(self, data):
        self.transport.write(data)
        # self.transport.sendto(data, self.addr)

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))

        time.sleep(1)

        print('Send: {!r}'.format(message))
        self.send(data)

        # print('Close the client socket')
        # self.transport.close()


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 8888)

    async with server:
        await server.serve_forever()


asyncio.run(main())
input()
