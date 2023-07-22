from communication import message
from masterServer.masterServer import get_master_server

server = get_master_server()
logger = server.logger


@message.chat_msg.on_receive
def chat(user_id, text):
    logger.info(f'{user_id}发来的聊天请求：{text}')

    ret = text
    logger.info(f'对{user_id}答复：{ret}')
    return ret
