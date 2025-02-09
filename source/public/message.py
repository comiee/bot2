# noinspection PyUnresolvedReferences
from communication.message import Message, debug_msg

# 退出消息，收到此消息后退出程序
exit_msg = Message('exit', {})

# 聊天
chat_msg = Message('chat', {
    'user_id': int,  # 用户id，比如QQ号
    'group_id': int,  # 群号，没有就填0
    'text': str,  # 聊天内容，public.convert中定义的internal格式
}, str)  # 返回值为聊天内容的回应，如果不答复则返回空字符串

# 调教
teach_msg = Message('teach', {
    'user_id': int,  # 用户id，比如QQ号
    'group_id': int,  # 群号，没有就填0
    'question': str,  # 问题
    'answer': str,  # 回答
}, int)  # 错误码

# 洗脑
forget_msg = Message('forget', {
    'user_id': int,  # 用户id，比如QQ号
    'group_id': int,  # 群号，没有就填0
    'question': str,  # 问题
    'answer': str,  # 回答，空字符串为删除该问题的所有回答
}, int)  # 错误码

# 日记
diary_msg = Message('diary', {
    'start': int,
    'end': int,
}, list)  # #从第start次记录到第end次记录

# 显示
show_answer_msg = Message('show_answer', {
    'question': str,  # 问题
}, list)  # 回答列表

# ############################# sql类消息 start ##############################
# 通用的sql消息（该消息仅用于管理员命令，sql操作应该尽量在服务器完成）
sql_msg = Message('sql',
                  str,  # sql语句
                  str)  # 调整好打印格式的结果字符串

# 查询货币数量
query_currency_msg = Message('query_currency', {
    'user_id': int,  # 用户id，比如QQ号
    'currency': str,  # 货币类型，Currency枚举的name属性
}, int)  # 查询到的货币数量

# 增加或减少货币数量
increase_currency_msg = Message('change_currency', {
    'user_id': int,  # 用户id，比如QQ号
    'currency': str,  # 货币类型，Currency枚举的name属性
    'num': int,  # 货币的增量
})

# 查询股价
query_stock_price_msg = Message('query_stock_price', {

}, float)  # 当前的股价

# 查询权限等级
get_authority_message = Message('get_authority', {
    'user_id': int,  # 用户id，比如QQ号
    'user_type': str,  # 用户类型，私聊为"friend"，群聊为"group"
    'auth_type': str,  # 要查询的权限类型
}, [int,  # 错误码，详见error_code.py
    int,  # 用户的权限等级
    ])

# 设置权限等级
set_authority_message = Message('set_authority', {
    'user_id': int,  # 用户id，比如QQ号
    'user_type': str,  # 用户类型，私聊为"friend"，群聊为"group"
    'auth_type': str,  # 要设置的权限类型
    'level': int,  # 要设置的权限等级
}, int)  # 错误码，详见error_code.py
# ############################# sql类消息 end ##############################

# 签到
sign_in_msg = Message('sign_in', {
    'user_id': int,  # 用户id，比如QQ号
}, int)  # 错误码，详见error_code.py

# 抽奖
draw_msg = Message('draw', {
    'user_id': int,  # 用户id，比如QQ号
    'count': int,  # 抽奖的次数
}, [int,  # 错误码，详见error_code.py
    list,  # 抽奖的结果，如果失败则为空列表
    ])

# 股票
stock_msg = Message('stock', {
    'user_id': int,  # 用户id，比如QQ号
    'count': int,  # 买入的数量，如果为负数则为卖出
}, int)  # 错误码，详见error_code.py

# 翻译
translate_msg = Message('translate', {
    'from_': str,  # 源语言
    'to_': str,  # 目标语言
    'text': str,  # 要翻译的文本
}, str)  # 翻译的结果

# 24点
p24_start_msg = Message('p24_start', {
    'group_id': int,  # 不同的group题目不同
}, list)  # 题目

p24_game_msg = Message('p24_game', {
    'group_id': int,  # 不同的group题目不同
    'user_id': int,  # 玩家id，用于计分
    'answer': str,  # 答案的算式
}, [int,  # 错误码（是否答对以错误码的形式返回）
    list,  # 题目，重开或答对时更新，否则传回原来的题目
    ])

p24_over_msg = Message('p24_over', {
    'group_id': int,  # 不同的group题目不同
}, list)  # [[user, score],]的排行榜

# momo日历
momo_calendar_msg = Message('momo_calendar', {}, str)  # 返回ics文件中的内容，如果出错则返回空字符串

# 幻影坦克
phantom_msg = Message('phantom', {
    'path1': str,  # 图片1的路径
    'path2': str,  # 图片2的路径
}, str)  # 结果的路径

# 向指定qq发送内容
send_qq_text_msg = Message('send_qq_text', {
    'user_id': int,  # 用户的qq号
    'text': str,  # 发送的内容
}, bool)  # 是否发送成功
