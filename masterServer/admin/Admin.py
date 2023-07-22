from tools.log import get_logger, LogLevel


class Admin:
    logger = get_logger('admin', LogLevel.DEBUG)

    def __init__(self, server):
        self.server = server

    def run(self):
        pass
