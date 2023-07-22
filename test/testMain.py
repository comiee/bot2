import multiprocessing

from communication.server import Server
from communication.client import Client
from communication import message
from threading import Thread
from itertools import count
import time


def server_main():
    server = Server()
    Thread(target=server.run).start()
    for i in count(0):
        for name in 'client1', 'client2':
            try:
                server.send_to(name, message.debug_msg.build(f'服务器第{i * 7}秒心跳包'))
            except Exception as e:
                print(e.args[0])
        time.sleep(7)


def client_test(name, seconds):
    client = Client(name)
    Thread(target=client.listen_server).start()
    for i in count(0):
        client.send(message.debug_msg.build(f'客户端[{name}]第{i * seconds}秒心跳包'))
        time.sleep(seconds)


def main():
    multiprocessing.Process(target=server_main).start()
    multiprocessing.Process(target=client_test, args=('client1', 11)).start()
    multiprocessing.Process(target=client_test, args=('client2', 13)).start()


if __name__ == '__main__':
    main()
