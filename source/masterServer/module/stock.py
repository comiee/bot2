from public.message import stock_msg, query_stock_price_msg
from public.error_code import ErrorCode
from public.currency import Currency
from public.scheduler import scheduler
from public.log import master_server_logger
from masterServer.comm.sql_cmd import sql, query_currency, increase_currency
import math
import random

STOCK_MULTIPLE = 4
STOCK_UNIT = 10 ** STOCK_MULTIPLE  # 股价*10000后存储在0号用户的stock列


@query_stock_price_msg.on_receive
def query_stock_price() -> float:
    return query_currency(0, Currency.stock) / STOCK_UNIT


def increase_stock_price(dif: float):
    dif = round(dif, STOCK_MULTIPLE)
    increase_currency(0, Currency.stock, int(dif * STOCK_UNIT))


@scheduler.scheduled_job('cron', hour='*', misfire_grace_time=None)
def update_price():
    if not sql.check_connect():
        master_server_logger.error('更新股价失败：数据库连接失败')

    while dif := round(random.normalvariate(0, 1), STOCK_MULTIPLE):
        if 1 < query_stock_price() + dif < 30:
            break
    master_server_logger.info(f'股价已变动，增量为{dif}')
    increase_stock_price(dif)


@stock_msg.on_receive
def stock(user_id, count):
    if not sql.check_connect():
        return ErrorCode.sql_disconnected

    price = query_stock_price()
    coin = math.ceil(price * count)

    if coin > query_currency(user_id, Currency.coin):
        return ErrorCode.insufficient_coin
    if -count > query_currency(user_id, Currency.stock):
        return ErrorCode.insufficient_stock

    increase_currency(user_id, Currency.stock, count)
    increase_currency(user_id, Currency.coin, -coin)

    return ErrorCode.success
