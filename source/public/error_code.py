# 消息使用的错误码

from enum import IntEnum


class ErrorCode(IntEnum):
    success = 0

    # 通用错误
    invalid_input = 1  # 输入非法
    wrong_message = 2  # 错误消息（此时不该收到这条消息）
    black_list_user = 3  # 此用户禁用此功能
    not_super_user = 4  # 非管理员使用管理员命令

    # 数据库相关错误
    sql_disconnected = 11  # 未连接数据库

    # 货币相关
    insufficient_coin = 21  # 金币不足
    insufficient_stamina = 22  # 体力不足
    insufficient_stock = 23  # 股份不足

    # 签到功能
    already_signed = 101  # 已签到过

    # 24点
    correct_answer = 200  # 回答正确，更新题目
    wrong_answer = 201  # 结果错误（结果不等于24）
    not_compliant_rule = 202  # 不符合规则（所有的数必须全部使用且只能使用一次）
    not_equation = 203  # 不是式子

    # 调教
    empty_str = 301  # 问题或答案为空
    conflict_with_template = 302  # 与原有模板冲突
    already_learned = 303  # 已经学会的回答
    # 洗脑
    not_remember = 311  # 没有学会的回答
