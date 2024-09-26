DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    vip BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_username ON users (username);
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

DROP TABLE IF EXISTS strategy;
CREATE TABLE strategy (
    id SERIAL PRIMARY KEY,
    date VARCHAR(64) NOT NULL,
    name VARCHAR(32) NOT NULL,
    username VARCHAR(32) NOT NULL,
    competition VARCHAR(32) NOT NULL,
    role VARCHAR(20) NOT NULL,
    annual_ret REAL NOT NULL,
    vol REAL NOT NULL,
    mdd REAL NOT NULL,
    annual_sr REAL NOT NULL,
    beta REAL NOT NULL,
    alpha REAL NOT NULL,
    var10 REAL NOT NULL,
    R2 REAL NOT NULL,
    gamma REAL NOT NULL,
    tw BOOLEAN DEFAULT TRUE,
    notes VARCHAR(255),
    assets TEXT[] NOT NULL,
    weight JSON NOT NULL,
    ret JSON NOT NULL,
    comments TEXT[][]
);
CREATE INDEX idx_user ON strategy (username);





