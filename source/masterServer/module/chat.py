from comiee import time_limit
from public.message import chat_msg
from public.config import data_path
from public.log import master_server_logger
import json
import random
import re

exec('from datetime import datetime;'
     'from public.tools import to_int,to_num;')


@time_limit(5, '匹配聊天回复超时')
def get_report(user, group, text):
    # 匹配模板
    f = lambda *args: None
    f(user, group)

    with open(data_path('chat.txt'), encoding='utf-8') as f:
        for line in f.readlines():
            data = line.strip().split('\t')
            pattern, probability, *_ = *data.pop(0).split('%%'), ''
            if not probability or random.random() < eval(probability):
                if match := re.search(pattern, text, re.S):
                    master_server_logger.debug(f'匹配到：{match.group()}')
                    try:
                        return eval(f"""f'''{random.choice(data)}'''""")
                    except Exception:
                        master_server_logger.warning(
                            f'匹配模板时发生错误：模板：{pattern!r}，原文：{text!r}',
                            exc_info=True
                        )
                        continue

    # 调教内容
    with open(data_path('teach.json'), encoding='utf-8') as f:
        data = json.load(f)
        if text in data:
            return random.choice(data[text])

    return ''


@chat_msg.on_receive
def chat(user_id, group_id, text):
    master_server_logger.info(f'{group_id}@{user_id}发来的聊天请求：{text}')
    # TODO 其他的处理
    # TODO 分多档位
    ret = get_report(user_id, group_id, text)
    if ret:
        master_server_logger.info(f'对{group_id}@{user_id}答复：{ret}')
    return ret
