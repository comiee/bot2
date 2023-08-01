import pymysql


class _Sql:
    def __init__(self):
        self.__db = pymysql.connect(
            host='localhost',
            user='comiee',
            password='19980722',
            database='mei',  # TODO是否需要使用新的数据库
            autocommit=True,
        )

    def cursor(self):
        return self.__db.cursor()

    def execute(self, query):
        with self.cursor() as cur:
            return cur.execute(query)

    def query(self, query, default=None):
        with self.cursor() as cur:
            if cur.execute(query):
                res = cur.fetchone()
                if len(res) == 1:
                    return res[0]
                else:
                    return res
            else:
                return default

    def query_all(self, query):
        with self.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


sql = _Sql()
