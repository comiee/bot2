from public.log import public_logger
import pymysql


class _Sql:
    def __init__(self):
        self.__db = None

    def connect(self):
        try:
            self.__db = pymysql.connect(
                host='192.168.1.102',  # TODO 换成配置文件
                user='comiee',
                password='19980722',
                database='mei',  # TODO是否需要使用新的数据库
                autocommit=True,
            )
        except pymysql.Error as e:
            public_logger.error(f'连接数据库失败：{e!r}')
            raise

    def is_connected(self):
        return self.__db is not None and self.__db.open

    def check_connect(self):
        if self.is_connected():
            return True
        try:
            self.connect()
            return True
        except pymysql.Error:
            return False

    def cursor(self):
        if not self.is_connected():
            self.connect()
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
