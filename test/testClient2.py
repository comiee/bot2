import public.messageDefine
from communication.client import Client
from communication import message
from threading import Thread


def test_client2():
    client = Client('test2')
    Thread(target=client.listen_server).start()
    while True:
        print('result', client.send(public.messageDefine.debug_msg.build(input('client2'))))


if __name__ == '__main__':
    test_client2()
