from public.currency import Currency
from public.message import query_currency_msg, change_currency_msg
from robot.botClient import get_bot_client


class User(int):
    def is_super_user(self):
        return self == 1440667228  # TODO 后续改成toml配置文件，并添加手动重新加载功能

    def query(self, currency: Currency) -> int:
        """查询用户的currency货币的数量"""
        return get_bot_client().send(query_currency_msg.build(user_id=int(self), currency=currency.name))

    def gain(self, num: int, currency: Currency) -> None:
        """给用户num个currency货币"""
        get_bot_client().send(change_currency_msg.build(user_id=int(self), currency=currency.name, num=num))
