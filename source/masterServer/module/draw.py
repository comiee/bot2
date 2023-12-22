from public.message import draw_msg
from public.currency import Currency
from masterServer.comm.sql_cmd import query_currency, increase_currency
import random


@draw_msg.on_receive
def draw(user_id, count):
    if count <= 0:
        return 1, []
    if count > query_currency(user_id, Currency.coin.name):
        return 2, []
    if count > query_currency(user_id, Currency.stamina.name):
        return 3, []

    result = random.choices([4, 2, 1, 0], [0.1, 0.2, 0.3, 0.4], k=count)

    increase_currency(user_id, Currency.coin.name, -count)
    increase_currency(user_id, Currency.stamina.name, -count)
    increase_currency(user_id, Currency.coin.name, sum(result))

    return 0, result
