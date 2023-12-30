from public.message import draw_msg
from public.error_code import ErrorCode
from public.currency import Currency
from masterServer.comm.sql_cmd import sql, query_currency, increase_currency
import random


@draw_msg.on_receive
def draw(user_id, count):
    if count <= 0:
        return ErrorCode.invalid_input, []
    if not sql.check_connect():
        return ErrorCode.sql_disconnected, []
    if count > query_currency(user_id, Currency.coin):
        return ErrorCode.insufficient_coin, []
    if count > query_currency(user_id, Currency.stamina):
        return ErrorCode.insufficient_stamina, []

    result = random.choices([4, 2, 1, 0], [0.1, 0.2, 0.3, 0.4], k=count)

    increase_currency(user_id, Currency.coin, -count)
    increase_currency(user_id, Currency.stamina, -count)
    increase_currency(user_id, Currency.coin, sum(result))

    return 0, result
