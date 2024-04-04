import time


class Admin:
    def __init__(self, server):
        self.server = server

    def run(self):
        while True:
            time.sleep(1)
