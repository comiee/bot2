from masterServer.admin.Admin import Admin
from communication.server import Server
from communication import message


class CmdAdmin(Admin):
    def __init__(self, server: Server):
        super().__init__(server)
        self.cmd_dict = {}
        self.init_cmd_dict()

    def parse_cmd(self, s):
        cmd, *args = s.split()
        if cmd not in self.cmd_dict:
            print('命令错误')
            return
        self.cmd_dict[cmd](*args)

    def run(self):
        while True:
            s = input()
            self.parse_cmd(s)

    def add_cmd(self, cmd):
        def get_function(fun):
            assert cmd not in self.cmd_dict, '命令已被注册'
            self.cmd_dict[cmd] = fun
            return fun

        return get_function

    def init_cmd_dict(self):
        @self.add_cmd('debug')
        def debug(client_name, text):
            self.server.send_to(client_name, message.debug_msg.build(text))
# TODO 主动发消息
