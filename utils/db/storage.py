import psycopg2
import os
from psycopg2.extras import RealDictCursor


class DatabaseManager(object):

    def __init__(self, connection_string=None):
        if connection_string is None:
            # Default PostgreSQL connection parameters
            connection_string = {
                "host": os.getenv("DB_HOST", "localhost"),
                "database": os.getenv("DB_NAME", "shop_bot"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "port": os.getenv("DB_PORT", "5432"),
            }

        self.conn = psycopg2.connect(**connection_string)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def create_tables(self):
        sql_statements = [
            """
            CREATE TABLE IF NOT EXISTS products (
                idx VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                body VARCHAR(255) NOT NULL,
                photo VARCHAR(255) NOT NULL,
                price INTEGER NOT NULL,
                tag VARCHAR(255) NOT NULL,
                PRIMARY KEY (idx)
            );""",
            """
            CREATE TABLE IF NOT EXISTS orders (
                cid BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                address VARCHAR(255) NOT NULL,
                products VARCHAR(255) NOT NULL
            );""",
            """
            CREATE TABLE IF NOT EXISTS cart (
                cid BIGINT NOT NULL,
                idx VARCHAR(255) NOT NULL,
                quantity INTEGER NOT NULL
            );""",
            """
            CREATE TABLE IF NOT EXISTS categories (
                idx INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                PRIMARY KEY (idx)
            );""",
            """
            CREATE TABLE IF NOT EXISTS wallet (
                cid BIGINT NOT NULL,
                balance INTEGER NOT NULL,
                PRIMARY KEY (cid)
            );""",
            """
            CREATE TABLE IF NOT EXISTS questions (
                cid BIGINT NOT NULL,
                question VARCHAR(255) NOT NULL
            );""",
            """
            CREATE TABLE IF NOT EXISTS users (
                cid BIGINT NOT NULL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                balance INTEGER DEFAULT 0
            );""",
        ]
        for sql in sql_statements:
            self.query(sql)

    def query(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def add_user(self, cid, name, phone_number):
        sql = "INSERT INTO users (cid, name, phone_number) VALUES (%s, %s, %s)"
        self.query(sql, (cid, name, phone_number))

    def get_user(self, cid):
        sql = "SELECT * FROM users WHERE cid = %s"
        return self.fetchone(sql, (cid,))

    @staticmethod
    def format_args(sql, parameters: dict):
        # This method is provided in the original file but not used in the new implementation
        # It's kept here as it's mentioned in the add_user method
        return sql.format(**parameters)

    def __del__(self):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()


"""

products: idx text, title text, body text, photo blob, price int, tag text

orders: cid int, usr_name text, usr_address text, products text

cart: cid int, idx text, quantity int ==> product_idx

categories: idx text, title text

wallet: cid int, balance real

questions: cid int, question text

"""
