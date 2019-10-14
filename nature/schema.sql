DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS invoice;
DROP TABLE IF EXISTS abstract;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 用户名
    username TEXT NOT NULL,
    -- 密码
    password TEXT NOT NULL,
    -- 性别
    gender TEXT NOT NULL,
    -- 邮箱
    email TEXT NOT NULL,
    -- 手机号
    phone TEXT NOT NULL,
    -- 姓名
    name TEXT NOT NULL,
    -- 工作单位
    workplace TEXT NOT NULL,
    -- 职称
    title INTEGER NOT NULL,
    -- 密保问题
    question TEXT NOT NULL,
    -- 答案
    answer TEXT NOT NULL,
    -- 邮寄地址(发票、邀请函)
    address TEXT NULL,
    -- 用户创建时间
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 是否缴费完成
    paid BOOLEAN NOT NULL DEFAULT FALSE,
    -- 备用1
    remark1 TEXT NULL,
    -- 备用2
    remark2 INTEGER NULL
);

CREATE TABLE abstract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 摘要文件名
    filename TEXT UNIQUE NOT NULL,
    -- 时间戳
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 状态
    state INTEGER NOT NULL,
    -- 用户Id
    user_id INTEGER NOT NULL,
    -- 外键关联用户
    FOREIGN KEY (user_id) REFERENCES user (id)
);


CREATE TABLE invoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 发票抬头
    invoice_title TEXT NOT NULL,
    -- 纳税人识别号
    serial_num TEXT NOT NULL, 
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);