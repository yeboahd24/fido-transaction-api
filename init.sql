
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TYPE transaction_type AS ENUM ('credit', 'debit');


CREATE TABLE IF NOT EXISTS transactions (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,                  -- User ID associated with the transaction
    full_name VARCHAR(255) NOT NULL,                -- Full name of the user
    transaction_date TIMESTAMP NOT NULL DEFAULT NOW(), -- Transaction date and time
    transaction_amount FLOAT NOT NULL,              -- Amount involved in the transaction
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('credit', 'debit')), -- Transaction type (credit or debit)
    
    total_transactions FLOAT NOT NULL DEFAULT 0,    -- Running total count of transactions for the user
    total_credit FLOAT NOT NULL DEFAULT 0,          -- Running total for credit transactions
    total_debit FLOAT NOT NULL DEFAULT 0,           -- Running total for debit transactions
    average_transaction_value FLOAT NOT NULL DEFAULT 0, -- Average value of all transactions

    created_at TIMESTAMP DEFAULT NOW(),             -- Timestamp when transaction was created
    updated_at TIMESTAMP DEFAULT NOW()              -- Timestamp for last update, automatically set on update
);


CREATE INDEX idx_user_id ON transactions (user_id);
