from communication.message import Message

# 调测信息，使接受端打印信息
debug_msg = Message('debug', str)


@debug_msg.on_receive
def _debug(val):
    print('调测信息：', val)
    return val


# 退出消息，收到此消息后退出程序
exit_msg = Message('exit', {})

chat_msg = Message('chat', {
    'user_id': int,  # 用户id，比如QQ号
    'group_id': int,  # 群号，没有就填0
    'text': str,  # 聊天内容，public.convert中定义的internal格式
}, str)  # 返回值为聊天内容的回应，如果不答复则返回空字符串

############################## sql类消息 start ##############################
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
############################## sql类消息 end ##############################

# 签到
sign_in_msg = Message('sign_in', {
    'user_id': int,  # 用户id，比如QQ号
}, int)  # 错误码：0 成功；1 已签到过；2 数据库未连接

# 抽奖
draw_msg = Message('draw', {
    'user_id': int,  # 用户id，比如QQ号
    'count': int,  # 抽奖的次数
}, [int,  # 错误码：0 成功；1输入非法；2金币不足；3体力不足
    list,  # 抽奖的结果，如果失败则为空列表
    ])

# 色图  色图的扣钱在客户端执行
h_pic_msg = Message('h_pic', {
    'post_json': dict,  # 请求json
}, [str,  # 错误信息，没有发生错误则为空字符串
    list,  # 查找到的url列表
    ])

# 翻译
translate_msg = Message('translate', {
    'from_': str,  # 源语言
    'to_': str,  # 目标语言
    'text': str,  # 要翻译的文本
}, str)  # 翻译的结果
