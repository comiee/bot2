from public.message import chat_msg
from public.log import bot_client_logger
from robot.botClient import get_bot_client


@chat_msg.on_receive
def chat(user_id, text):
    bot_client_logger.info(f'收到服务器的请求，向{user_id}发送：{text}')
    get_bot_client().bot_proxy.send_friend(text, user_id)
    return ''
