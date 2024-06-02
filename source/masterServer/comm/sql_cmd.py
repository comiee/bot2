from public.currency import Currency
from masterServer.comm.sql import sql


def has_column(table_name: str, column_name: str) -> bool:
    return bool(sql.query(f'select count(*) from information_schema.columns where table_schema="mei" and '
                          f'table_name = "{table_name}" and column_name="{column_name}";'))


def column_default(table_name: str, column_name: str):
    return sql.query(f'select column_default from information_schema.columns where table_schema="mei" and '
                     f'table_name = "{table_name}" and column_name="{column_name}";')


def query_currency(user_id: int, currency: str | Currency) -> int:
    """查询货币"""
    if isinstance(currency, Currency):
        currency = currency.name
    return sql.query(f'select {currency} from info where qq={user_id};', default=0)


def increase_currency(user_id: int, currency: str | Currency, num: int) -> None:
    """增加货币"""
    if isinstance(currency, Currency):
        currency = currency.name
    sql.execute(f'insert into info(qq,{currency}) values({user_id},{num}) '
                f'on duplicate key update {currency}={currency}+{num};')


def is_ban(user_id: int) -> bool:
    """判断该用户是否在黑名单中"""
    return bool(sql.execute(f'select * from ban where qq={user_id};'))  # TODO 替换为权限数据表


def get_authority(user_id: int, user_type: str, auth_type: str) -> int:
    return sql.query(f'select {auth_type} from authority where id={user_id} and type={user_type!r};',
                     default=int(column_default('authority', auth_type)))


def set_authority(user_id: int, user_type: str, auth_type: str, level: int) -> None:
    sql.execute(f'insert into authority(id,type,{auth_type}) values({user_id},{user_type!r},{level}) '
                f'on duplicate key update {auth_type}={level};')


def del_authority(user_id: int, user_type: str, auth_type: str) -> None:
    sql.execute(f'update authority set {auth_type}=default({auth_type}) where id={user_id} and type={user_type!r};')
