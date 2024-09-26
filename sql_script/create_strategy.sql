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

