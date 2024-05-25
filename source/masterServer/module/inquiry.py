from public.message import sql_msg, query_currency_msg, increase_currency_msg
from masterServer.comm.sql import sql
from masterServer.comm.sql_cmd import query_currency, increase_currency


@sql_msg.on_receive
def _sql(s):
    try:
        with sql.cursor() as cur:
            cur.execute(s)
            return '\t'.join(next(zip(*cur.description))) + '\n' + \
                '\n'.join('\t'.join(map(str, i)) for i in cur.fetchall())
    except Exception as e:
        return str(e)


@query_currency_msg.on_receive
def _query_currency(user_id: int, currency: str):
    return query_currency(user_id, currency)


@increase_currency_msg.on_receive
def _increase_currency(user_id: int, currency: str, num: int):
    increase_currency(user_id, currency, num)
