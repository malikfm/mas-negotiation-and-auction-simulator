import sqlite3

import config


def new():
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn
