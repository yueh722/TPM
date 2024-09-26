DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    vip BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_username ON users (username);
INSERT INTO users (username, password)
VALUES ('R10246002@ntu.edu.tw', 'pbkdf2:sha256:260000$Z5bK5pp0D8HEDAps$abb43b1b1c543ff334de8fb3aeba9c0460c37de5b5363e5210e68b00739d5e2c');