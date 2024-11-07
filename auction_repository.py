import sqlite3
from contextlib import closing
from typing import List, Tuple

import config


class AuctionRepository:
    def add_auction(self, conn: sqlite3, negotiation_id: str):
        with closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO auctions (id) VALUES (?)", (negotiation_id,))

        conn.commit()

    def get_auctions(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, created_at FROM auctions ORDER BY created_at DESC")
            return cursor.fetchall()

    def get_bidders(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, name, balance FROM a_bidders")
            return cursor.fetchall()

    def get_bidders_by_ids(self, conn: sqlite3, ids: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"SELECT id, name, balance FROM a_bidders where id IN {ids}",
            )
            return cursor.fetchall()

    def get_items(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, name FROM a_items")
            return cursor.fetchall()

    def get_items_by_ids(self, conn: sqlite3, ids: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        id,
                        name,
                        price,
                        is_sold
                    FROM a_items
                    WHERE id IN {ids}
                """
            )
            return cursor.fetchall()

    def add_transaction(self, conn: sqlite3, transaction: Tuple):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    INSERT INTO a_transactions
                    (id, auction_id, a_bidder_id, a_item_id, bid, buy_status, timestamp_ns)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                transaction
            )

        conn.commit()

    def update_transaction_to_sold(self, conn: sqlite3, transaction_id: str):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    UPDATE a_transactions
                    SET buy_status = true
                    WHERE id = ?
                """,
                (transaction_id,)
            )

        conn.commit()

    def get_winner_per_auction_per_item(self, conn: sqlite3, auction_id: str, item_id: int) -> sqlite3.Row:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    WITH highest_bid AS (
                        SELECT
                            MAX(bid) bid
                        FROM a_transactions
                        WHERE auction_id = ?
                        AND a_item_id = ?
                    )
                    SELECT
                        a_transactions.id,
                        a_bidders.name bidder_name
                    FROM a_transactions
                    JOIN a_bidders ON a_transactions.a_bidder_id = a_bidders.id
                    WHERE auction_id = ?
                    AND a_item_id = ?
                    AND bid = (SELECT bid from highest_bid)
                    ORDER BY timestamp_ns
                """,
                (auction_id, item_id, auction_id, item_id)
            )
            return cursor.fetchone()

    def add_activity_log(self, conn: sqlite3, activity_log: Tuple):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    INSERT INTO a_activity_log
                    (id, auction_id, a_item_id, log, timestamp_ns)
                    VALUES (?, ?, ?, ?, ?)
                """,
                activity_log
            )

        conn.commit()

    def get_item_ids_in_activity_per_auction(self, conn: sqlite3, auction_id: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        DISTINCT a_item_id
                    FROM a_activity_log
                    WHERE auction_id = ?
                    ORDER BY timestamp_ns
                """,
                (auction_id,)
            )
            return cursor.fetchall()

    def get_activity_log_per_auction(self, conn: sqlite3, auction_id: str, item_id: int) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        log
                    FROM a_activity_log
                    WHERE auction_id = ?
                    AND a_item_id = ?
                    ORDER BY timestamp_ns
                """,
                (auction_id, item_id)
            )
            return cursor.fetchall()
