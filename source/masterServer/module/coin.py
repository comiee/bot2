from public.message import query_currency_msg


@query_currency_msg.on_receive
def query_currency(user_id: int, currency: str):
    return 233
