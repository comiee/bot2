from public.message import exit_msg, debug_msg, chat_msg
from public.log import admin_logger
from public.exception import ActiveExitException
from masterServer.admin.Admin import Admin
from communication.server import Server
import inspect


class CmdAdmin(Admin):
    def __init__(self, server: Server):
        super().__init__(server)
        self.cmd_dict = {}
        self.init_cmd_dict()

    def run(self):
        while True:
            try:
                s = input()
                cmd, *args = s.split()
                admin_logger.info(f'即将执行命令：{s}')
                self.cmd_dict[cmd](*args)
                admin_logger.info('执行命令成功')
            except ActiveExitException:
                self.server.send_to_all(exit_msg.build())
                self.server.close()
                return
            except Exception as e:
                admin_logger.warning(f'执行命令失败：{e}')  # TODO 优化打印

    def add_cmd(self, cmd):
        # 空格分隔后，第一项为命令字，其他的作为参数传给fun
        def get_function(fun):
            assert cmd not in self.cmd_dict, '命令已被注册'
            self.cmd_dict[cmd] = fun
            return fun

        return get_function

    def init_cmd_dict(self):
        @self.add_cmd('help')
        def help_():
            for cmd, fun in self.cmd_dict.items():
                print(cmd, inspect.getfullargspec(fun).args)

        @self.add_cmd('debug')
        def debug(client_name, text):
            self.server.send_to(client_name, debug_msg.build(text))

        @self.add_cmd('exit')
        def exit_():
            raise ActiveExitException('主动退出')

        @self.add_cmd('send')
        def send(client_name, user_id, text):
            self.server.send_to(client_name, chat_msg.build(
                user_id=int(user_id),
                group_id=0,
                text=text,
            ))
