# 消息使用的错误码

from enum import IntEnum


class ErrorCode(IntEnum):
    success = 0

    # 通用错误
    invalid_input = 1  # 输入非法
    # 参数不足
    # 类型错误

    # 数据库相关错误
    sql_disconnected = 11  # 未连接数据库

    # 货币相关
    insufficient_coin = 21  # 金币不足
    insufficient_stamina = 22  # 体力不足

    # 签到功能
    already_signed = 101  # 已签到过
