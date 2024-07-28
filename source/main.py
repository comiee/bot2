from masterServer.admin import CmdAdmin
from masterServer import server_main
from robot import bot_main
from webpage import web_main
from qqbot import qqbot_main
import multiprocessing
import time


def start_main(main_fun):
    multiprocessing.Process(target=main_fun).start()


def main():
    start_main(bot_main)
    start_main(web_main)
    start_main(qqbot_main)

    time.sleep(1)  # pycharm的bug，不加sleep会卡住
    server_main(CmdAdmin)  # CmdAdmin里面有input，只能在主线程运行


if __name__ == '__main__':
    main()
