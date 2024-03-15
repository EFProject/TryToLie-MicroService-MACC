CREATE TABLE user_info (
    id SERIAL PRIMARY KEY,
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



CREATE TABLE matches_info (
    id SERIAL PRIMARY KEY,
    winner_id INT,
    user_one_id INT REFERENCES user_info(id),
    user_two_id INT REFERENCES user_info(id),
    user_three_id INT REFERENCES user_info(id),
    date TIMESTAMP,
    CHECK (winner_id IN (user_one_id, user_two_id, user_three_id))
);

DROP TABLE IF EXISTS public.matches_info;