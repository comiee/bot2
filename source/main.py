from masterServer.admin import CmdAdmin
from masterServer import server_main
from robot import bot_main
from webpage import web_main
import multiprocessing
import time


def start_main(main_fun, name=None):
    multiprocessing.Process(target=main_fun, name=name).start()


def main():
    start_main(bot_main, 'bot')
    start_main(web_main, 'web')

    time.sleep(1)  # pycharm的bug，不加sleep会卡住
    server_main(CmdAdmin)  # CmdAdmin里面有input，只能在主线程运行


if __name__ == '__main__':
    main()
