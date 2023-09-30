from public.log import public_logger
import pymysql


class _Sql:
    def __init__(self):
        self.__db = self.__connect()

    def __connect(self):
        return pymysql.connect(
            host='localhost',
            user='comiee',
            password='19980722',
            database='mei',  # TODO是否需要使用新的数据库
            autocommit=True,
        )

    def cursor(self):
        if not self.__db.open:
            self.__db = self.__connect()
        return self.__db.cursor()

    def execute(self, query):
        try:
            with self.cursor() as cur:
                return cur.execute(query)
        except pymysql.Error as e:
            public_logger.error(f'sql执行execute出错：{e!r}')

    def query(self, query, default=None):
        try:
            with self.cursor() as cur:
                if cur.execute(query):
                    res = cur.fetchone()
                    if len(res) == 1:
                        return res[0]
                    else:
                        return res
                else:
                    return default
        except pymysql.Error as e:
            public_logger.error(f'sql执行query出错：{e!r}')
            return default

    def query_all(self, query):
        try:
            with self.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except pymysql.Error as e:
            public_logger.error(f'sql执行query_all出错：{e!r}')
            return []


sql = _Sql()
