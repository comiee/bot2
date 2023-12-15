from public.message import sql_msg, query_currency_msg, increase_currency_msg
from masterServer.comm.sql import sql


@sql_msg.on_receive
def sql_(s):
    try:
        with sql.cursor() as cur:
            cur.execute(s)
    except Exception as e:
        return str(e)
    else:
        return '\t'.join(next(zip(*cur.description))) + '\n' + \
            '\n'.join('\t'.join(map(str, i)) for i in cur.fetchall())


@query_currency_msg.on_receive
def query_currency(user_id: int, currency: str):
    return sql.query(f'select {currency} from info where qq={user_id};', 0)


@increase_currency_msg.on_receive
def increase_currency(user_id: int, currency: str, num: int):
    sql.execute(f'insert into info(qq,{currency}) values({user_id},{num}) '
                f'on duplicate key update {currency}={currency}+{num};')
