from communication.server import Server
import time


class Admin:
    def __init__(self, server: Server):
        self.server = server

    def run(self):
        while True:
            time.sleep(1)
