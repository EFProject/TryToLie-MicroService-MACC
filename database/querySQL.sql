#POSTGRES Queries


CREATE TABLE user_info (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    emailVerified BOOLEAN NOT NULL,
    provider VARCHAR(50) NOT NULL,
    matchesPlayed INT,
    matchesWon INT,
    signupDate VARCHAR(50)
);

DROP TABLE IF EXISTS public.user_info;
