from tools.log import bot_client_logger
from robot.botClient import get_bot_client
from communication import message


@message.chat_msg.on_receive
def chat(user_id, text):
    bot_client_logger.info(f'收到服务器的请求，向{user_id}发送：{text}')
    ret = get_bot_client().bot_proxy.send_friend(text, user_id)
    bot_client_logger.info(f'服务器响应为{ret}')
