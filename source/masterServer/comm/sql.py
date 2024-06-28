from public.log import public_logger
from public.config import get_config
import pymysql


class _Sql:
    def __init__(self):
        self.__db = None

    def connect(self):
        sql_config = get_config('sql')
        try:
            self.__db = pymysql.connect(**sql_config)
        except Exception as e:
            public_logger.exception(f'连接数据库失败：{e!r}')
            raise

    def is_connected(self):
        return self.__db is not None and self.__db.open

    def check_connect(self):
        if self.is_connected():
            return True
        try:
            self.connect()
            return True
        except Exception:
            return False

    def cursor(self):
        if not self.is_connected():
            self.connect()
        return self.__db.cursor()

    def execute(self, query, args=None):
        try:
            with self.cursor() as cur:
                return cur.execute(query, args)
        except Exception as e:
            public_logger.exception(f'sql执行execute出错：{e!r}')

    def query(self, query, args=None, default=None):
        try:
            with self.cursor() as cur:
                if cur.execute(query, args):
                    res = cur.fetchone()
                    if len(res) == 1:
                        return res[0]
                    else:
                        return res
                else:
                    return default
        except Exception as e:
            public_logger.exception(f'sql执行query出错：{e!r}')
            return default

    def query_all(self, query, args=None):
        try:
            with self.cursor() as cur:
                cur.execute(query, args)
                return cur.fetchall()
        except Exception as e:
            public_logger.exception(f'sql执行query_all出错：{e!r}')
            return []

    def query_col(self, query, col=0, args=None):
        arr = list(zip(*self.query_all(query, args)))
        if len(arr) <= col:
            return []
        return arr[col]


sql = _Sql()
