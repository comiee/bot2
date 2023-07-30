from public.currency import Currency


class User(int):
    def is_super_user(self):
        return self == 1440667228  # TODO 后续改成toml配置文件，并添加手动重新加载功能

    def query(self, currency: Currency) -> int:
        """查询用户的currency货币的数量"""
        assert currency == Currency.coin
        if not hasattr(self, 'coin'):
            self.coin = 233
        return self.coin  # TODO 向服务器发消息查询

    def gain(self, num: int, currency: Currency) -> None:
        """给用户num个currency货币"""
        # TODO 向服务器发消息改变货币数量
        assert currency == Currency.coin
        if not hasattr(self, 'coin'):
            self.coin = 233
        self.coin += num
