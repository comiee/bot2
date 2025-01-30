"""定义组件中通信的消息格式"""
from comiee import overload
from public.exception import MessageException
from public.log import public_logger
import json
import time

ValueFormatType = type | dict | list | None


class Message:
    __message_dict = {}  # 存储命令字对应的消息对象

    @staticmethod
    def __add_message(cmd: str, message: 'Message'):
        if cmd in Message.__message_dict:
            raise MessageException('消息命令字重复：' + cmd)
        Message.__message_dict[cmd] = message

    @staticmethod
    def __get_message(cmd: str) -> 'Message':
        if cmd not in Message.__message_dict:
            raise MessageException('未知的消息：' + cmd)
        return Message.__message_dict[cmd]

    def __init__(self, cmd: str, value_format: ValueFormatType, result_format: ValueFormatType = None):
        """
        :param cmd 消息的名称
        :param value_format 消息内容的格式定义，用字典的形式表达，字典的值为消息值的类型（None为任意类型），可嵌套，如：
        {
            "name": str,
            "ability": {
                "run": True,
                "fly": False,
            }
        }
        :param result_format 响应消息的格式，只在发送响应消息时校验，格式同value_format
        """
        self.__cmd = cmd
        self.__value_format = value_format
        self.__result_format = result_format
        self.__call_back = None
        Message.__add_message(cmd, self)

    def on_receive(self, function):
        """接受到消息以后的回调函数，函数的参数是按照value_format解包后的msg_value，返回值会作为消息的响应"""
        if self.__call_back is not None:
            raise MessageException(f'命令字<{self.__cmd}>回调函数已被注册')
        self.__call_back = function
        return function

    @staticmethod
    def __check_format(value_format: ValueFormatType, msg_value):
        if value_format is None:
            return
        elif isinstance(value_format, dict):
            if not isinstance(msg_value, dict):
                raise MessageException('参数类型错误：应为字典')
            if keys := value_format.keys() - msg_value.keys():
                raise MessageException(f'缺少参数{keys}')
            if keys := msg_value.keys() - value_format.keys():
                raise MessageException(f'多余参数{keys}')
            for k in msg_value:
                Message.__check_format(value_format[k], msg_value[k])
        elif isinstance(value_format, list):
            if not isinstance(msg_value, (list, tuple)):
                raise MessageException('参数类型错误：应为列表')
            if len(value_format) != len(msg_value):
                raise MessageException(f'列表参数长度不符合，期望{len(value_format)}，实际{len(msg_value)}：{msg_value!r}')
            for i in range(len(value_format)):
                Message.__check_format(value_format[i], msg_value[i])
        elif not isinstance(msg_value, value_format):
            raise MessageException(f'参数类型错误：期望{value_format}，实际{type(msg_value)}：{msg_value!r}')

    @overload
    def build(self, **kwargs) -> str:
        return self.build(kwargs)

    @overload
    def build(self, msg_value) -> str:
        try:
            self.__check_format(self.__value_format, msg_value)
        except MessageException as e:
            raise MessageException(f'命令字<{self.__cmd}>消息构建失败：{e.args[0]}')
        msg = {'cmd': self.__cmd, 'value': msg_value}
        return json.dumps(msg, ensure_ascii=False)

    @overload
    @staticmethod
    def parse(s: str):
        """使用静态方法调用，会根据命令字找到对应的message对象进行处理"""
        msg = json.loads(s)
        cmd = msg['cmd']
        value = msg['value']
        return Message.__get_message(cmd).__solve(value)

    @overload
    def parse(self, s: str):
        """使用成员方法调用，会判断命令字是否跟自己的命令字相同"""
        msg = json.loads(s)
        cmd = msg['cmd']
        value = msg['value']
        if cmd != self.__cmd:
            raise MessageException(f'命令字匹配失败：收到{cmd}，目标{self.__cmd}')
        return Message.__get_message(cmd).__solve(value)

    def __solve(self, value):
        try:
            self.__check_format(self.__value_format, value)
        except MessageException as e:
            raise MessageException(f'命令字<{self.__cmd}>消息解析失败：{e.args[0]}')

        if function := self.__call_back:
            start = time.time()
            if isinstance(self.__value_format, dict):
                result = function(**value)
            else:
                result = function(value)
            end = time.time()
            if end - start > 1:
                public_logger.warning(f'命令字<{self.__cmd}>执行回调函数时间过长，用时{end - start}s')
        else:
            result = None
        try:
            self.__check_format(self.__result_format, result)
        except MessageException as e:
            raise MessageException(f'命令字<{self.__cmd}>构建响应消息失败：{e.args[0]}')
        return result


# 注册消息，每个客户端连接上服务器时先发送一条注册消息，此消息不会有响应消息
register_msg = Message('register', {
    'name': str,  # 客户端的识别名
    'client_type': str,  # 客户端的类型，支持的类型有：
    # sender：发送者，要求服务器长期处于等待接收消息的状态
    # receiver：接收者，自身长期处于等待接收消息的状态
})


@register_msg.on_receive
def _register(name, client_type):
    return name, client_type


# 响应消息，除注册消息外，每次发送消息都会返回此消息
result_msg = Message('result', None)


@result_msg.on_receive
def _result(value):
    return value


# 调测信息，使接受端打印信息
debug_msg = Message('debug', str)


@debug_msg.on_receive
def _debug(val):
    print('调测信息：', val)
    return val

# 特殊消息定义在此文件，其余消息定义在public.message
