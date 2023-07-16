from alicebot import Bot
import os


def run_bot():
    os.chdir(os.path.dirname(__file__))
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    run_bot()
