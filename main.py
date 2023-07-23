from tools.log import main_logger
from masterServer import server_main
from robot import bot_main
import multiprocessing
import time


def run_main(main_fun):
    while True:
        try:
            main_fun()
        except Exception as e:
            main_logger.exception(f'运行{main_fun.__name__}时出错，将在10秒后重新运行：{e}')
            time.sleep(10)


def start_main(main_fun):
    multiprocessing.Process(target=run_main, args=(main_fun,)).start()


def main():
    start_main(bot_main)

    time.sleep(1)  # pycharm的bug，不加sleep会卡住
    server_main()  # server_main里面有input，只能在主线程运行


if __name__ == '__main__':
    main()
