import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from sqlite3 import Row
from typing import List

import sqlite_client
from negotiation_repository import NegotiationRepository


class NegotiationUsecase:
    def __init__(self, negotiation_repository: NegotiationRepository):
        self.negotiation_repository = negotiation_repository

    def show_all_negotiations(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.negotiation_repository.get_negotiations(conn)
        conn.close()

        return rows

    def show_activity_log_per_negotiation(self, negotiation_id: str) -> List[List[str]]:
        # Construct activity log chronologically.
        activity_log = []
        conn = sqlite_client.new()
        bicycle_ids = self.negotiation_repository.get_bicycle_ids_in_activity_per_negotiation(conn, negotiation_id)

        for bicycle_id in bicycle_ids:
            activity_log_per_item = self.negotiation_repository.get_activity_log_per_negotiation(
                conn, negotiation_id, bicycle_id["n_bicycle_id"]
            )
            activity_log_per_item = [activity["log"] for activity in activity_log_per_item]
            activity_log.append(activity_log_per_item)

        conn.close()

        return activity_log

    def get_all_buyers(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.negotiation_repository.get_buyers(conn)
        conn.close()

        return rows

    def get_all_bicycles(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.negotiation_repository.get_bicycles(conn)
        conn.close()

        return rows

    def negotiate_bicycle_per_round(
            self,
            negotiation_id: str,
            bicycle: Row,
            buyer: Row,
            min_offer_scale: float,
            max_offer_scale: float,
            seller_price: int,

    ):
        # Random sleep.
        time.sleep(random.uniform(0.1, 0.5))

        # Buyer make offer.
        buyer_offer = int(bicycle["price"] * 0.5 * random.uniform(min_offer_scale, max_offer_scale))

        # Buyer offer can't exceed buyer's balance. If so, offer = balance.
        if buyer_offer > buyer["balance"]:
            buyer_offer = buyer["balance"]

        # It doesn't make sense a buyer makes offer higher than the price.
        if buyer_offer > seller_price:
            buyer_offer = seller_price

        timestamp_ns = time.time_ns()
        transaction = {
            "id": str(uuid.uuid4()),
            "negotiation_id": negotiation_id,
            "buyer_id": buyer["id"],
            "buyer_name": buyer["name"],
            "bicycle_id": bicycle["id"],
            "seller_price": seller_price,
            "buyer_offer": buyer_offer,
            "buy_status": False,
            "timestamp_ns": timestamp_ns
        }

        transaction_tuple = (
            str(uuid.uuid4()),
            negotiation_id,
            buyer["id"],
            bicycle["id"],
            seller_price,
            buyer_offer,
            False,
            timestamp_ns
        )

        timestamp_s = timestamp_ns / 1_000_000_000
        datetime_object = datetime.fromtimestamp(timestamp_s)
        formatted_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f")

        conn = sqlite_client.new()
        self.negotiation_repository.add_transaction(conn, transaction_tuple)
        self.negotiation_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Buyer {buyer["name"]} made an offer {buyer_offer}. | Time: {formatted_datetime}", timestamp_ns)
        )
        conn.close()

        return transaction

    def negotiate_bicycle(self, negotiation_id: str, bicycle: Row, buyers_rows: List[Row]):
        min_offer_scale = 1.0
        max_offer_scale = 1.1
        prev_highest_offer = 0
        highest_offer = 0

        seller_price = bicycle["price"]
        prev_seller_price = 0
        minimum_seller_price = int(seller_price * random.uniform(0.5, 0.7))

        max_threads = len(buyers_rows) if len(buyers_rows) < 8 else 8
        transaction_log = []

        conn = sqlite_client.new()
        self.negotiation_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Negotiation for Bicycle {bicycle["brand"]} {bicycle["type"]}.", time.time_ns())
        )
        self.negotiation_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Initial price: {seller_price}.", time.time_ns())
        )
        conn.close()

        while True:
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                futures = []
                for buyer in buyers_rows:
                    futures.append(executor.submit(
                        self.negotiate_bicycle_per_round,
                        negotiation_id,
                        bicycle,
                        buyer,
                        min_offer_scale,
                        max_offer_scale,
                        seller_price
                    ))

                round_transactions = []
                for future in futures:
                    round_transactions.append(future.result())

                round_transactions = sorted(round_transactions, key=lambda x: x["timestamp_ns"])

                for trx in round_transactions:
                    timestamp_s = trx["timestamp_ns"] / 1_000_000_000
                    datetime_object = datetime.fromtimestamp(timestamp_s)
                    formatted_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f")

                    # activity = f"Buyer {trx["buyer_name"]} makes an offer {trx["buyer_offer"]} | Time: {formatted_datetime}"
                    if highest_offer < trx["buyer_offer"]:
                        prev_highest_offer = highest_offer
                        highest_offer = trx["buyer_offer"]

                    # activity_log.append(activity)

                transaction_log.extend(round_transactions)

            def choose_eligible_transaction() -> Row:
                conn = sqlite_client.new()
                first_transaction = self.negotiation_repository.get_eligible_buyer_per_negotiation_per_item(
                    conn, negotiation_id, bicycle["id"]
                )
                self.negotiation_repository.update_transaction_to_sold(conn, first_transaction["id"])
                conn.close()

                return first_transaction

            # If the highest offer >= demanded price,
            #   the negotiation is over and the first highest offer will be chosen.
            if highest_offer >= seller_price:
                first_transaction = choose_eligible_transaction()
                conn = sqlite_client.new()
                self.negotiation_repository.add_activity_log(
                    conn,
                    (
                    str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Negotiation ends. Bicycle {bicycle["brand"]} {bicycle["type"]} sold to {first_transaction["buyer_name"]}.", time.time_ns())
                )
                conn.close()

                break

            # No improvement = no deal.
            if prev_highest_offer == highest_offer:
                # activity_log.append("Negotiation ends. No deal.")

                conn = sqlite_client.new()
                self.negotiation_repository.add_activity_log(
                    conn,
                    (
                        str(uuid.uuid4()), negotiation_id, bicycle["id"], "Negotiation ends. No deal.", time.time_ns())
                )
                conn.close()

                break

            # Update offer scale so the buyers offer will be higher than prev.
            min_offer_scale += 0.1
            max_offer_scale += 0.1

            # Seller update the price.
            prev_seller_price = seller_price
            seller_price = int(seller_price * random.uniform(0.8, 0.95))

            # The price can't go lower than minimum seller price
            if seller_price < minimum_seller_price:
                seller_price = minimum_seller_price

            formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            # If the highest offer >= demanded price after price reduction,
            #   the negotiation is over and the first highest offer will be chosen.
            if highest_offer >= seller_price:
                first_transaction = choose_eligible_transaction()
                conn = sqlite_client.new()
                self.negotiation_repository.add_activity_log(
                    conn,
                    (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Seller {bicycle["seller_name"]} updated the price to {highest_offer}. | Time: {formatted_datetime}", time.time_ns())
                )
                self.negotiation_repository.add_activity_log(
                    conn,
                    (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Negotiation ends. Bicycle {bicycle["brand"]} {bicycle["type"]} sold to {first_transaction["buyer_name"]}.", time.time_ns())
                )
                conn.close()

                break

            conn = sqlite_client.new()
            if seller_price == prev_seller_price:
                self.negotiation_repository.add_activity_log(
                    conn,
                    (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Seller {bicycle["seller_name"]} kept the price at {seller_price}. | Time: {formatted_datetime}", time.time_ns())
                )
            else:
                self.negotiation_repository.add_activity_log(
                    conn,
                    (str(uuid.uuid4()), negotiation_id, bicycle["id"], f"Seller {bicycle["seller_name"]} updated the price to {seller_price} | Time: {formatted_datetime}", time.time_ns())
                )
            conn.close()

        # return activity_log

    def simulate_negotiations(self, buyer_ids: List[int], bicycle_ids: List[int]) -> str:
        max_threads = len(bicycle_ids) if len(bicycle_ids) < 8 else 8
        conn = sqlite_client.new()

        buyers_rows = self.negotiation_repository.get_buyers_by_ids(
            conn, "(" + ",".join([str(id) for id in buyer_ids]) + ")"
        )
        bicycles_rows = self.negotiation_repository.get_bicycles_by_ids(
            conn, "(" + ",".join([str(id) for id in bicycle_ids]) + ")"
        )

        negotiation_id = str(uuid.uuid4())

        self.negotiation_repository.add_negotiation(conn, negotiation_id)
        conn.close()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for bicycle in bicycles_rows:
                futures.append(executor.submit(self.negotiate_bicycle, negotiation_id, bicycle, buyers_rows))

            for future in futures:
                # negotiation_history.append(future.result())
                future.result()

        # Construct activity log chronologically.
        self.show_activity_log_per_negotiation(negotiation_id)

        return negotiation_id
