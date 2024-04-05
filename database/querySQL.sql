#POSTGRES Queries


CREATE TABLE user_info (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) NOT NULL,
    email_verified BOOLEAN NOT NULL,
    provider VARCHAR(50) NOT NULL,
    matches_played INT,
    matches_won INT,
    country VARCHAR(50),
    signup_date TIMESTAMP
);

DROP TABLE IF EXISTS public.user_info;
