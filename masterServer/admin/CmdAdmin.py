from tools.log import admin_logger
from masterServer.admin.Admin import Admin
from communication.server import Server
from communication import message


class CmdAdmin(Admin):
    def __init__(self, server: Server):
        super().__init__(server)
        self.cmd_dict = {}
        self.init_cmd_dict()

    def parse_cmd(self, s):
        try:
            cmd, *args = s.split()
            self.cmd_dict[cmd](*args)
            admin_logger.info(f'执行命令{s}')
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print(e)

    def run(self):
        while True:
            s = input()
            self.parse_cmd(s)

    def add_cmd(self, cmd):
        # 空格分隔后，第一项为命令字，其他的作为参数传给fun
        def get_function(fun):
            assert cmd not in self.cmd_dict, '命令已被注册'
            self.cmd_dict[cmd] = fun
            return fun

        return get_function

    def init_cmd_dict(self):
        @self.add_cmd('debug')
        def debug(client_name, text):
            self.server.send_to(client_name, message.debug_msg.build(text))

        @self.add_cmd('send')
        def send(client_name, user_id, text):
            self.server.send_to(client_name, message.chat_msg.build(
                user_id=int(user_id),
                text=text,
            ))
