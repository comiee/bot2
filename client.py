import asyncio


class EchoClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport: asyncio.transports.Transport):
        self.transport = transport
        self.send(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def send(self, data):
        self.transport.write(data)

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        print('addr:', addr)
        self.data_received(data)

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = 'Hello World!'

    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(message, on_con_lost),
        '127.0.0.1', 8888)

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    try:
        # await on_con_lost
        async def f():
            await asyncio.sleep(1)
            print(233)

        await asyncio.gather(f())

    finally:
        transport.close()


asyncio.run(main())
input()
