from public.message import query_currency_msg
from masterServer.comm.sql import sql


@query_currency_msg.on_receive
def query_currency(user_id: int, currency: str):
    return sql.query(f'select {currency} from info where qq={user_id};')
