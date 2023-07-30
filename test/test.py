class CommandMeta(type):
    def __init__(cls, name, bases, attrs):  # 定义新类的时候执行
        super().__init__(name, bases, attrs)
        print('class', CommandMeta, cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):  # 新类实例化时执行
        obj = super().__call__(*args, **kwargs)
        print('new', CommandMeta, cls, obj, args, kwargs)
        return obj

class Command(metaclass=CommandMeta):
    def __init__(self):
        print(Command)

class SuperCommand(Command):
    def __init__(self):
        super().__init__()
        print(SuperCommand)


def main():
    cmd=SuperCommand()
    print(type(cmd))


if __name__ == '__main__':
    main()
