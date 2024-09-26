DROP TABLE IF EXISTS stock_price;
DROP TABLE IF EXISTS stock_price_tw;


CREATE TABLE stock_price (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(32) NOT NULL,
    date DATE NOT NULL,
    price REAL NOT NULL
);
-- you need to add ()
CREATE INDEX idx_ticker ON stock_price (ticker);

CREATE TABLE stock_price_tw (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(32) NOT NULL,
    date DATE NOT NULL,
    price REAL NOT NULL
);
-- you need to add ()
CREATE INDEX idx_ticker_tw ON stock_price_tw (ticker);
