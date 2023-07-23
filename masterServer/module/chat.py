from communication import message
from tools.log import master_server_logger


@message.chat_msg.on_receive
def chat(user_id, text):
    master_server_logger.info(f'{user_id}发来的聊天请求：{text}')

    ret = text
    master_server_logger.info(f'对{user_id}答复：{ret}')
    return ret
