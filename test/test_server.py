from communication.server import Server, send_to
from communication import message
from threading import Thread


def test_server():
    server = Server()
    Thread(target=server.run).start()
    while True:
        print('result ', send_to('test', message.debug_msg.build(input('server:'))))
        print('result ', send_to('test2', message.debug_msg.build(input('server:'))))


if __name__ == '__main__':
    test_server()
