from masterServer import server_main
from robot import bot_main
import multiprocessing
import time


def start_main(main_fun):
    multiprocessing.Process(target=main_fun).start()


def main():
    start_main(bot_main)

    time.sleep(1)  # pycharm的bug，不加sleep会卡住
    server_main()  # server_main里面有input，只能在主线程运行


if __name__ == '__main__':
    main()
