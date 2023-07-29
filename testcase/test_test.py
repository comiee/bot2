class User:
    def query(self):
        print('query')
        return -1

    def gain(self, num):
        print('gain', num)


class Session:
    @property
    def user(self):
        print('user')
        return User()


