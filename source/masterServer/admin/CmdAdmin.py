from communication.server import Server
from communication.asyncServer import AsyncServer
from public.message import exit_msg, debug_msg, chat_msg
from public.log import admin_logger
from public.exception import ActiveExitException
from masterServer.admin.Admin import Admin
from masterServer.comm.TTLSerial import TTLSerialIR03T, bytes_hex
import inspect
import traceback
import asyncio


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
                AsyncServer().wait_close()
                return
            except Exception as e:
                admin_logger.warning(f'执行命令失败：{e}')  # TODO 优化打印

    def add_cmd(self, cmd):
        # 空格分隔后，第一项为命令字，其他的作为参数传给fun
        def get_function(fun):
            assert cmd not in self.cmd_dict, '命令已被注册'
            if asyncio.iscoroutinefunction(fun):
                self.cmd_dict[cmd] = lambda *args: asyncio.run(fun(*args))
            else:
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

        @self.add_cmd('eval')
        def eval_(*args):
            try:
                print(eval(' '.join(args)))
            except Exception:
                traceback.print_exc()

        @self.add_cmd('exec')
        def exec_(*args):
            try:
                exec(' '.join(args))
            except Exception:
                traceback.print_exc()

        @self.add_cmd('send')
        def send(client_name, user_id, text):
            self.server.send_to(client_name, chat_msg.build(
                user_id=int(user_id),
                group_id=0,
                text=text,
            ))

        @self.add_cmd('ttl_learn')
        async def ttl_learn(index):
            index = int(index)
            with TTLSerialIR03T() as ser:
                try:
                    await ser.learn_cmd(index)
                    data = await ser.read_cmd(index)
                    print(bytes_hex(data))
                except Exception as e:
                    print(e)

        @self.add_cmd('ttl_run')
        async def ttl_run(index):
            index = int(index)
            with TTLSerialIR03T() as ser:
                try:
                    await ser.run_cmd(index)
                    data = await ser.read_cmd(index)
                    print(bytes_hex(data))
                except Exception as e:
                    print(e)

        @self.add_cmd('ttl_remove')
        async def ttl_remove(index):
            index = int(index)
            with TTLSerialIR03T() as ser:
                try:
                    await ser.remove_cmd(index)
                    data = await ser.read_cmd(index)
                    print(bytes_hex(data))
                except Exception as e:
                    print(e)
