from public.message import exit_msg, send_qq_text_msg
from public.log import bot_client_logger, bot_logger
from robot.botClient import get_bot_client


@exit_msg.on_receive
def exit_():
    bot_client_logger.info('收到服务器的命令，即将退出程序')
    bot_client = get_bot_client()
    bot = bot_client.bot_proxy.bot

    @bot.bot_exit_hook
    async def exit_hook(_):
        bot_client.close()
        bot_client_logger.warning('程序已退出')
        bot_logger.warning('收到服务器的命令，已退出程序')

    bot.should_exit.set()


@send_qq_text_msg.on_receive
def send_qq_text(user_id, text):
    try:
        get_bot_client().bot_proxy.send_friend(text, user_id)
        return True
    except Exception as e:
        bot_client_logger.exception(f'发送QQ消息失败：{e}')
        return False
