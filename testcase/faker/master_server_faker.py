from communication.asyncServer import AsyncServer
from masterServer import server_main
from masterServer.admin.Admin import Admin
from multiprocessing import Process, Value
import time


class ServerController:
    def __init__(self):
        self.running_val = Value('b', True)

    def main(self):
        class TestAdmin(Admin):
            # noinspection PyMethodParameters
            def run(this):
                while self.running_val.value:
                    time.sleep(1)
                AsyncServer().wait_close()
                this.server.close()

        server_main(TestAdmin)

    def start(self):
        self.process = Process(target=self.main)
        self.process.start()

    def close(self):
        self.running_val.value = False
