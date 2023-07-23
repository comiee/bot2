import multiprocessing
import itertools
import time


def f(name):
    for i in itertools.count():
        print(name, i)
        time.sleep(1)


def main():
    multiprocessing.Process(target=f, args=('a',)).start()
    multiprocessing.Process(target=f, args=('b',)).start()
    #time.sleep(1)
    while True:
        print('c', input())


if __name__ == '__main__':
    main()
