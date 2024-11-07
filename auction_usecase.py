import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from sqlite3 import Row
from typing import List

import sqlite_client
from auction_repository import AuctionRepository


class AuctionUsecase:
    def __init__(self, negotiation_repository: AuctionRepository):
        self.auction_repository = negotiation_repository

    def show_all_auctions(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.auction_repository.get_auctions(conn)
        conn.close()

        return rows

    def show_activity_log_per_auction(self, auction_id: str) -> List[List[str]]:
        # Construct activity log chronologically.
        activity_log = []
        conn = sqlite_client.new()
        item_ids = self.auction_repository.get_item_ids_in_activity_per_auction(conn, auction_id)

        for item_id in item_ids:
            activity_log_per_item = self.auction_repository.get_activity_log_per_auction(
                conn, auction_id, item_id["a_item_id"]
            )
            activity_log_per_item = [activity["log"] for activity in activity_log_per_item]
            activity_log.append(activity_log_per_item)

        conn.close()

        return activity_log

    def get_all_bidders(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.auction_repository.get_bidders(conn)
        conn.close()

        return rows

    def get_all_items(self) -> List[Row]:
        conn = sqlite_client.new()
        rows = self.auction_repository.get_items(conn)
        conn.close()

        return rows

    def item_auction(self, auction_id: str, item: Row, bidders_rows: List[Row]):
        latest_bid = item["price"]
        latest_bidder = ""

        conn = sqlite_client.new()
        self.auction_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), auction_id, item["id"], f"Auction for {item["name"]}", time.time_ns())
        )
        self.auction_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), auction_id, item["id"], f"Started from: {item["price"]}", time.time_ns())
        )

        participants = [
            {"id": bidder["id"], "name": bidder["name"], "balance": bidder["balance"]} for bidder in bidders_rows
        ]

        while len(participants) > 1:
            bidders_pool = deepcopy(participants)
            for i in range(len(participants)):
                bidder = random.choice(bidders_pool)
                while latest_bidder == bidder["name"]:
                    bidder = random.choice(bidders_pool)
                    latest_bidder = bidder["name"]

                bidders_pool.remove(bidder)

                if latest_bid > bidder["balance"]:
                    timestamp_ns = time.time_ns()
                    timestamp_s = timestamp_ns / 1_000_000_000
                    datetime_object = datetime.fromtimestamp(timestamp_s)
                    formatted_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f")

                    self.auction_repository.add_activity_log(
                        conn,
                        (str(uuid.uuid4()), auction_id, item["id"], f"{bidder["name"]} left. | Time: {formatted_datetime}", time.time_ns())
                    )

                    participants.remove(bidder)
                    continue

                bid = int(latest_bid * random.uniform(1.1, 2.0))
                if bid > bidder["balance"]:
                    bid = bidder["balance"]

                timestamp_ns = time.time_ns()
                timestamp_s = timestamp_ns / 1_000_000_000
                datetime_object = datetime.fromtimestamp(timestamp_s)
                formatted_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S.%f")

                self.auction_repository.add_activity_log(
                    conn,
                    (str(uuid.uuid4()), auction_id, item["id"], f"{bidder["name"]} placed a bid {bid}. | Time: {formatted_datetime}", time.time_ns())
                )

                latest_bid = bid

                timestamp_ns = time.time_ns()
                transaction_tuple = (
                    str(uuid.uuid4()),
                    auction_id,
                    bidder["id"],
                    item["id"],
                    bid,
                    False,
                    timestamp_ns
                )
                self.auction_repository.add_transaction(conn, transaction_tuple)

        # Get the winner.
        winner_transaction = self.auction_repository.get_winner_per_auction_per_item(conn, auction_id, item["id"])

        self.auction_repository.add_activity_log(
            conn,
            (str(uuid.uuid4()), auction_id, item["id"], f"{item["name"]} sold to {winner_transaction["bidder_name"]}.", time.time_ns())
        )

        self.auction_repository.update_transaction_to_sold(conn, winner_transaction["id"])

        conn.close()

    def simulate_auctions(self, bidder_ids: List[int], item_ids: List[int]) -> str:
        max_threads = len(item_ids) if len(item_ids) < 8 else 8
        conn = sqlite_client.new()

        bidders_rows = self.auction_repository.get_bidders_by_ids(
            conn, "(" + ",".join([str(id) for id in bidder_ids]) + ")"
        )
        item_rows = self.auction_repository.get_items_by_ids(
            conn, "(" + ",".join([str(id) for id in item_ids]) + ")"
        )

        auction_id = str(uuid.uuid4())

        self.auction_repository.add_auction(conn, auction_id)
        conn.close()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for item in item_rows:
                futures.append(executor.submit(self.item_auction, auction_id, item, bidders_rows))

            for future in futures:
                future.result()

        # Construct activity log chronologically.
        self.show_activity_log_per_auction(auction_id)

        return auction_id
