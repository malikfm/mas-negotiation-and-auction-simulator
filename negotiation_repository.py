import sqlite3
from contextlib import closing
from typing import List, Tuple


class NegotiationRepository:
    def add_negotiation(self, conn: sqlite3, negotiation_id: str):
        with closing(conn.cursor()) as cursor:
            cursor.execute("INSERT INTO negotiations (id) VALUES (?)", (negotiation_id,))

        conn.commit()

    def get_negotiations(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, created_at FROM negotiations ORDER BY created_at DESC")
            return cursor.fetchall()

    def get_buyers(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT id, name FROM n_buyers")
            return cursor.fetchall()

    def get_buyers_by_ids(self, conn: sqlite3, ids: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"SELECT id, name, balance FROM n_buyers where id IN {ids}",
            )
            return cursor.fetchall()

    def get_bicycles(self, conn: sqlite3, ) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    SELECT
                        n_bicycles.id,
                        n_sellers.name seller_name,
                        brand,
                        type
                    FROM n_bicycles
                    JOIN n_sellers ON n_bicycles.n_seller_id = n_sellers.id
                """
            )
            return cursor.fetchall()

    def get_bicycles_by_ids(self, conn: sqlite3, ids: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        n_bicycles.id,
                        n_sellers.name seller_name,
                        brand,
                        type,
                        price,
                        is_sold
                    FROM n_bicycles
                    JOIN n_sellers ON n_bicycles.n_seller_id = n_sellers.id
                    WHERE n_bicycles.id IN {ids}
                """
            )
            return cursor.fetchall()

    def add_transaction(self, conn: sqlite3, transaction: Tuple):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    INSERT INTO n_transactions
                    (id, negotiation_id, n_buyer_id, n_bicycle_id, seller_price, buyer_offer, buy_status, timestamp_ns)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                transaction
            )

        conn.commit()

    def update_transaction_to_sold(self, conn: sqlite3, transaction_id: str):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    UPDATE n_transactions
                    SET buy_status = true
                    WHERE id = ?
                """,
                (transaction_id,)
            )

        conn.commit()

    def get_eligible_buyer_per_negotiation_per_item(self, conn: sqlite3, negotiation_id: str, bicycle_id: int) -> sqlite3.Row:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    WITH highest_offer AS (
                        SELECT
                            MAX(buyer_offer) buyer_offer
                        FROM n_transactions
                        WHERE negotiation_id = ?
                        AND n_bicycle_id = ?
                    )
                    SELECT
                        n_transactions.id,
                        n_buyers.name buyer_name
                    FROM n_transactions
                    JOIN n_buyers ON n_transactions.n_buyer_id = n_buyers.id
                    WHERE negotiation_id = ?
                    AND n_bicycle_id = ?
                    AND buyer_offer = (SELECT buyer_offer from highest_offer)
                    ORDER BY timestamp_ns
                """,
                (negotiation_id, bicycle_id, negotiation_id, bicycle_id)
            )
            return cursor.fetchone()

    def add_activity_log(self, conn: sqlite3, activity_log: Tuple):
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                    INSERT INTO n_activity_log
                    (id, negotiation_id, n_bicycle_id, log, timestamp_ns)
                    VALUES (?, ?, ?, ?, ?)
                """,
                activity_log
            )

        conn.commit()

    def get_bicycle_ids_in_activity_per_negotiation(self, conn: sqlite3, negotiation_id: str) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        DISTINCT n_bicycle_id
                    FROM n_activity_log
                    WHERE negotiation_id = ?
                    ORDER BY timestamp_ns
                """,
                (negotiation_id,)
            )
            return cursor.fetchall()

    def get_activity_log_per_negotiation(self, conn: sqlite3, negotiation_id: str, bicycle_id: int) -> List[sqlite3.Row]:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                f"""
                    SELECT
                        log
                    FROM n_activity_log
                    WHERE negotiation_id = ?
                    AND n_bicycle_id = ?
                    ORDER BY timestamp_ns
                """,
                (negotiation_id, bicycle_id)
            )
            return cursor.fetchall()
