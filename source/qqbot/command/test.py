from qqbot.comm.Command import SingleCommand


@SingleCommand('测试')
@SingleCommand('test')
def test(text):
    return '测试消息：' + text
