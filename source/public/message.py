from communication.message import Message

# 调测信息，使接受端的打印信息
debug_msg = Message('debug', str)


@debug_msg.on_receive
def _debug(val):
    print('调测信息：', val)
    return val


# 注册消息，每个客户端连接上服务器时先发送一条注册消息，此消息不会有响应消息
register_msg = Message('register', {
    'name': str,  # 客户端的识别名
    'client_type': str,  # 客户端的类型，支持的类型有：
    # sender：发送者，要求服务器长期处于等待接收消息的状态
    # receiver：接收者，自身长期处于等待接收消息的状态
})

# 响应消息，除注册消息外，每次发送消息都会返回此消息
result_msg = Message('result', None)

# 退出消息，收到此消息后退出程序
exit_msg = Message('exit', {})

chat_msg = Message('chat', {
    'user_id': int,  # 用户id，比如QQ号
    'text': str,  # 聊天内容
    # TODO 更多形式的聊天内容
}, str)  # 返回值为聊天内容的回应

############################## sql类消息 ##############################
# 通用的sql消息
sql_msg = Message('sql', str)  # 该消息仅用于管理员命令，sql操作应该尽量在服务器完成

# 查询货币数量
query_currency_msg = Message('query_currency', {
    'user_id': int,  # 用户id，比如QQ号
    'currency': str,  # 货币类型，Currency枚举的name属性
}, int)  # 查询到的货币数量

# 增加或减少货币数量
change_currency_msg = Message('change_currency', {
    'user_id': int,  # 用户id，比如QQ号
    'currency': str,  # 货币类型，Currency枚举的name属性
    'num': int,  # 货币的增量
})

# 签到
sign_in_msg = Message('sign_in', {
    'user_id': int,  # 用户id，比如QQ号
})
