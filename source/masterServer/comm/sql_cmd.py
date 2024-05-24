from public.currency import Currency
from masterServer.comm.sql import sql


def query_currency(user_id: int, currency: str | Currency) -> int:
    """查询货币"""
    if isinstance(currency, Currency):
        currency = currency.name
    return sql.query(f'select {currency} from info where qq={user_id};', default=0)


def increase_currency(user_id: int, currency: str | Currency, num: int):
    """增加货币"""
    if isinstance(currency, Currency):
        currency = currency.name
    sql.execute(f'insert into info(qq,{currency}) values({user_id},{num}) '
                f'on duplicate key update {currency}={currency}+{num};')


def is_ban(user_id: int) -> bool:
    """判断该用户是否在黑名单中"""
    return bool(sql.execute(f'select * from ban where qq={user_id}'))
