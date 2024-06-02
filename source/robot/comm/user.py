from public.config import get_config
from public.currency import Currency
from public.message import *
from public.error_code import ErrorCode
from public.exception import CustomException
from robot.botClient import get_bot_client


class User(int):
    def is_super_user(self):
        return self in get_config('admin', 'super_user')

    def query(self, currency: Currency) -> int:
        """查询用户的currency货币的数量"""
        return get_bot_client().send(query_currency_msg.build(
            user_id=int(self),
            currency=currency.name,
        ))

    def gain(self, num: int, currency: Currency) -> None:
        """给用户num个currency货币"""
        get_bot_client().send(increase_currency_msg.build(
            user_id=int(self),
            currency=currency.name,
            num=num,
        ))

    def get_authority(self, auth_type: str) -> int:
        ret, level = get_bot_client().send(get_authority_message.build(
            user_id=int(self),
            user_type='friend',
            auth_type=auth_type,
        ))
        if ret != ErrorCode.success:
            raise CustomException(f'查询权限出错：{ret}')
        return level

    def set_authority(self, auth_type: str, level: int) -> None:
        ret = get_bot_client().send(set_authority_message.build(
            user_id=int(self),
            user_type='friend',
            auth_type=auth_type,
            level=level,
        ))
        if ret != ErrorCode.success:
            raise CustomException(f'设置权限出错：{ret}')
