from public.message import chat_msg
from public.config import data_path
from public.log import master_server_logger
import json
import random


@chat_msg.on_receive
def chat(user_id, text):
    master_server_logger.info(f'{user_id}发来的聊天请求：{text}')
    # TODO 其他的处理
    ret = ''
    with open(data_path('teach.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
        if text in data:
            ret = random.choice(data[text])
    if ret:
        master_server_logger.info(f'对{user_id}答复：{ret}')
    return ret
