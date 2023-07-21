from masterServer import server_main


def main():
    server_main() # TODO 在不同的进程中启动服务器和客户端，每个进程在运行出错时都记录日志并重启


if __name__ == '__main__':
    main()
