from public.message import chat_msg
from public.config import data_path
from public.log import master_server_logger
import json
import random
import re

exec('from datetime import datetime;'
     'from public.tools import to_int,to_num;')

def get_report(user, text):
    # 处理艾特自己
    if '[at:1790218632]' in text:
        return '有什么事你倒是说啊'

    # 匹配模板
    f=lambda *args:None
    f(user,)

    with open(data_path('chat.txt'), encoding='utf-8') as f:
        for line in f.readlines():
            data = line.strip().split('\t')
            pattern, probability, *_ = *data.pop(0).split('%%'), ''
            if not probability or random.random() < eval(probability):
                if match := re.search(pattern, text, re.S):
                    master_server_logger.debug(f'匹配到：{match.group()}')
                    return eval(f"""f'''{random.choice(data)}'''""")

    # 调教内容
    with open(data_path('teach.json'), encoding='utf-8') as f:
        data = json.load(f)
        if text in data:
            return random.choice(data[text])

    return ''

@chat_msg.on_receive
def chat(user_id, text):
    master_server_logger.info(f'{user_id}发来的聊天请求：{text}')
    # TODO 其他的处理
    # TODO 分多档位
    ret = get_report(user_id, text)
    if ret:
        master_server_logger.info(f'对{user_id}答复：{ret}')
    return ret
