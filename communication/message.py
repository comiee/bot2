"""定义组件中通信的消息格式"""
import json
from comiee import overload


class Message:
    message_dict = {}  # 存储命令字对应的消息对象

    @staticmethod
    def add_message(cmd: str, message: 'Message'):
        if cmd in Message.message_dict:
            raise Exception('消息命令字重复：' + cmd)
        Message.message_dict[cmd] = message

    @staticmethod
    def get_message(cmd: str) -> 'Message':
        if cmd not in Message.message_dict:
            raise Exception('未知的消息：' + cmd)
        return Message.message_dict[cmd]

    def __init__(self, cmd: str, value_format: dict):
        """
        :arg cmd 消息的名称
        :arg value_format 消息内容的格式定义，用字典的形式表达，字典的值为消息值的类型，可嵌套，如：
        {
            "name": str,
            "ability": {
                "run": True,
                "fly": False,
            }
        }
        """
        self.cmd = cmd
        self.value_format = value_format
        self.call_back = None
        Message.add_message(cmd, self)

    def on_receive(self, function):
        """接受到消息以后的回调函数，函数的第一个发送方的sock，其余参数是解包后的msg_value"""
        self.call_back = function
        return function

    @staticmethod
    def check_format(value_format: dict | type, msg_value: dict):
        if keys := value_format.keys() - msg_value.keys():
            raise Exception(f'缺少参数{keys}')
        if keys := msg_value.keys() - value_format.keys():
            raise Exception(f'多余参数{keys}')
        for k in msg_value:
            if isinstance(value_format[k], dict):
                Message.check_format(value_format[k], msg_value[k])
            elif not isinstance(msg_value[k], value_format[k]):
                raise Exception(f'参数类型错误：期望{value_format[k]}，实际{type(msg_value[k])}')

    @overload
    def build(self, **kwargs) -> str:
        return self.build(kwargs)

    @overload
    def build(self, msg_value: dict) -> str:
        try:
            self.check_format(self.value_format, msg_value)
        except Exception as e:
            raise Exception('消息构建失败：' + e.args[0])
        msg = {'cmd': self.cmd, 'value': msg_value}
        return json.dumps(msg)

    @overload
    @staticmethod
    def parse(sock, s: str):
        """使用静态方法调用，会根据命令字找到对应的message对象进行处理"""
        msg = json.loads(s)
        cmd = msg['cmd']
        value = msg['value']
        return Message.get_message(cmd).solve(sock, value)

    @overload
    def parse(self, sock, s: str):
        """使用成员方法调用，会判断命令字是否跟自己的命令字相同"""
        msg = json.loads(s)
        cmd = msg['cmd']
        value = msg['value']
        if cmd != self.cmd:
            raise Exception(f'命令字匹配失败：收到{cmd}，目标{self.cmd}')
        return Message.get_message(cmd).solve(sock, value)

    def solve(self, sock, value: dict):
        try:
            self.check_format(self.value_format, value)
        except Exception as e:
            raise Exception('消息解析失败：' + e.args[0])

        if function := self.call_back:
            return function(sock, **value)


# 调测信息，使接受端的打印信息
debug_msg = Message('debug', {
    'string': str,  # 打印的内容
})


@debug_msg.on_receive
def _debug(_, string):
    print('调测信息：', string)


# 注册消息，每个客户端连接上服务器时先发送一条注册消息
register_msg = Message('register', {
    'name': str,  # 客户端的识别名
})
