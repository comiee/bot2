class CustomException(Exception):
    """自定义异常，用于和python原生的异常区分"""


class MessageException(CustomException):
    """处理消息时发生的异常（注册、构建、解析等过程中）"""


class ActiveExitException(CustomException):
    """主动退出时使用的异常"""


class CostCurrencyFailedException(CustomException):
    """扣除货币失败异常"""
