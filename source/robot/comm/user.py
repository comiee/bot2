from public.config import get_config
from public.currency import Currency
from public.message import query_currency_msg, increase_currency_msg
from robot.botClient import get_bot_client


class User(int):
    def is_super_user(self):
        return self in get_config('admin', 'super_user')

    def query(self, currency: Currency) -> int:
        """查询用户的currency货币的数量"""
        return get_bot_client().send(query_currency_msg.build(user_id=int(self), currency=currency.name))

    def gain(self, num: int, currency: Currency) -> None:
        """给用户num个currency货币"""
        get_bot_client().send(increase_currency_msg.build(user_id=int(self), currency=currency.name, num=num))
