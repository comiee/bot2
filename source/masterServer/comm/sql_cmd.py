from public.currency import Currency
from masterServer.comm.sql import sql


def query_currency(user_id: int, currency: str | Currency):
    if isinstance(currency, Currency):
        currency = currency.name
    return sql.query(f'select {currency} from info where qq={user_id};', 0)


def increase_currency(user_id: int, currency: str | Currency, num: int):
    if isinstance(currency, Currency):
        currency = currency.name
    sql.execute(f'insert into info(qq,{currency}) values({user_id},{num}) '
                f'on duplicate key update {currency}={currency}+{num};')
