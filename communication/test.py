import os

# os.system('start python server.py')
# os.system('start python client.py')
# os.system('start python client.py')

from client import Client
from threading import Thread
import message

if __name__ == '__main__':
    client = Client('test2')
    Thread(target=client.run).start()
    while True:
        print('result', client.send(message.debug_msg.build(input())))
