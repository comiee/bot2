class CustomException(Exception):
    """自定义异常，用于和python原生的异常区分"""


class MessageException(CustomException):
    """处理消息时发生的异常（注册、构建、解析等过程中）"""

class InteractException(CustomException):
    """服务器与客户端交互时发生的异常（连接断开，发送、接收失败等）"""