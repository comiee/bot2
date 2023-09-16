from public.message import chat_msg
from public.log import bot_client_logger
from public.convert import convert_to
from robot.botClient import get_bot_client


@chat_msg.on_receive
def chat(user_id, group_id, text):
    if group_id:
        bot_client_logger.info(f'收到服务器的请求，向{group_id}@{user_id}发送：{text}')
        get_bot_client().bot_proxy.send_group(convert_to('mirai', f'[at:{user_id}' + text), group_id)
    else:
        bot_client_logger.info(f'收到服务器的请求，向{user_id}发送：{text}')
        get_bot_client().bot_proxy.send_friend(convert_to('mirai', text), user_id)
    return ''
