from public import messageDefine
from public.log import bot_client_logger, bot_logger
from robot.botClient import get_bot_client


@messageDefine.exit_msg.on_receive
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