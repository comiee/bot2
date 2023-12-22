from masterServer.comm.sql import sql


def query_currency(user_id: int, currency: str):
    return sql.query(f'select {currency} from info where qq={user_id};', 0)


def increase_currency(user_id: int, currency: str, num: int):
    sql.execute(f'insert into info(qq,{currency}) values({user_id},{num}) '
                f'on duplicate key update {currency}={currency}+{num};')
