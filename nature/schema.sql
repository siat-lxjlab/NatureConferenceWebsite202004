DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS invoice;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    name TEXT NOT NULL,
    workplace TEXT NOT NULL,
    -- 职称
    title TEXT NOT NULL
);



CREATE TABLE invoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);