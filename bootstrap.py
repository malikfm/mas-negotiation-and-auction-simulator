import sqlite3
from contextlib import closing

import config


def create_sqlite_tables(cursor) -> None:
    with open("ddl.sql") as f:
        create_stmt = f.read()

    cursor.executescript(create_stmt)


def insert_buyers_to_sqlite(cursor) -> None:
    insert_stmt = f"""
        DELETE FROM n_buyers;
        DELETE FROM sqlite_sequence WHERE name='n_buyers';
        INSERT INTO n_buyers (name, balance)
        VALUES
        ("Mulyono", 5000),
        ("Fufu", 3000),
        ("Fafa", 3000)
    """
    cursor.executescript(insert_stmt)


def insert_sellers_to_sqlite(cursor) -> None:
    insert_stmt = f"""
        DELETE FROM n_sellers;
        DELETE FROM sqlite_sequence WHERE name='n_sellers';
        INSERT INTO n_sellers (name)
        VALUES
        ("Kowee"),
        ("Gnarly"),
        ("Raka")
    """
    cursor.executescript(insert_stmt)

    insert_stmt = f"""
        DELETE FROM n_bicycles;
        DELETE FROM sqlite_sequence WHERE name='n_bicycles';
        INSERT INTO n_bicycles (n_seller_id, brand, type, price, is_sold)
        VALUES
        (1, "Mazda", "3-hatchback", 500, 0),
        (2, "Honda", "Civic Turbo", 495, 0),
        (3, "Yamaha", "Camel", 88, 0)
    """
    cursor.executescript(insert_stmt)

def insert_bidders_to_sqlite(cursor) -> None:
    insert_stmt = f"""
        DELETE FROM a_bidders;
        DELETE FROM sqlite_sequence WHERE name='a_bidders';
        INSERT INTO a_bidders (name, balance)
        VALUES
        ("Owi", 3000),
        ("Fufa", 1500),
        ("Fafu", 2000)
    """
    cursor.executescript(insert_stmt)


def insert_items_to_sqlite(cursor) -> None:
    insert_stmt = f"""
        DELETE FROM a_items;
        DELETE FROM sqlite_sequence WHERE name='a_items';
        INSERT INTO a_items (name, price, is_sold)
        VALUES
        ("Tongkat Diponegoro", 1000, 0),
        ("Supersemar", 1200, 0),
        ("Surat Hutang", 500, 0)
    """
    cursor.executescript(insert_stmt)

def init_db():
    with closing(sqlite3.connect(config.SQLITE_DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            print("Creating tables.")
            create_sqlite_tables(cursor)
            print("Finished.")

            print("Inserting buyers.")
            insert_buyers_to_sqlite(cursor)
            print("Finished.")

            print("Inserting sellers.")
            insert_sellers_to_sqlite(cursor)
            print("Finished.")

            print("Inserting bidders.")
            insert_bidders_to_sqlite(cursor)
            print("Finished.")

            print("Inserting items.")
            insert_items_to_sqlite(cursor)
            print("Finished.")


if __name__ == '__main__':
    init_db()
