-- NEGOTIATION
CREATE TABLE IF NOT EXISTS negotiations (
    id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS n_buyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    balance INTEGER
);

CREATE TABLE IF NOT EXISTS n_sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS n_bicycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    n_seller_id INTEGER,
    brand VARCHAR(255),
    type VARCHAR(255),
    price INTEGER,
    is_sold BOOLEAN,
    FOREIGN KEY(n_seller_id) REFERENCES n_sellers(id)
);

CREATE TABLE IF NOT EXISTS n_transactions (
    id VARCHAR(255) PRIMARY KEY,
    negotiation_id VARCHAR(255),
    n_buyer_id INTEGER,
    n_bicycle_id INTEGER,
    seller_price INTEGER,
    buyer_offer INTEGER,
    buy_status BOOLEAN,
    timestamp_ns BIGINT,
    FOREIGN KEY(negotiation_id) REFERENCES negotiations(id),
    FOREIGN KEY(n_buyer_id) REFERENCES n_buyers(id),
    FOREIGN KEY(n_bicycle_id) REFERENCES n_bicycles(id)
);

CREATE TABLE IF NOT EXISTS n_activity_log (
    id VARCHAR(255) PRIMARY KEY,
    negotiation_id VARCHAR(255),
    n_bicycle_id INTEGER,
    log VARCHAR(255),
    timestamp_ns BIGINT,
    FOREIGN KEY(negotiation_id) REFERENCES negotiations(id),
    FOREIGN KEY(n_bicycle_id) REFERENCES n_bicycles(id)
);

-- AUCTION
CREATE TABLE IF NOT EXISTS auctions (
    id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS a_bidders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    balance INTEGER
);

CREATE TABLE IF NOT EXISTS a_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    price INTEGER,
    is_sold BOOLEAN
);

CREATE TABLE IF NOT EXISTS a_transactions (
    id VARCHAR(255) PRIMARY KEY,
    auction_id VARCHAR(255),
    a_bidder_id INTEGER,
    a_item_id INTEGER,
    bid INTEGER,
    buy_status BOOLEAN,
    timestamp_ns BIGINT,
    FOREIGN KEY(auction_id) REFERENCES auctions(id),
    FOREIGN KEY(a_bidder_id) REFERENCES a_bidders(id),
    FOREIGN KEY(a_item_id) REFERENCES a_items(id)
);

CREATE TABLE IF NOT EXISTS a_activity_log (
    id VARCHAR(255) PRIMARY KEY,
    auction_id VARCHAR(255),
    a_item_id INTEGER,
    log VARCHAR(255),
    timestamp_ns BIGINT,
    FOREIGN KEY(auction_id) REFERENCES auctions(id),
    FOREIGN KEY(a_item_id) REFERENCES a_items(id)
);
