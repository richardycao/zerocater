import psycopg2
import time
import sys

class PostgresClient:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host='postgres',
                port=5432,
                database='zerocater',
                user='user',
                password='password',
            )
            return None
        except Exception as e:
            print(e)
            sys.exit(1)

    def execute_read(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()

            return rows, None
        except:
            cur.close()
            self.conn.rollback()
            return None, str(e)

    def execute_writes(self, sql_list):
        cur = self.conn.cursor()
        try:
            for sql in sql_list:
                cur.execute(sql)
            self.conn.commit()
            cur.close()
            return None
        except Exception as e:
            cur.close()
            self.conn.rollback()
            return str(e)

    