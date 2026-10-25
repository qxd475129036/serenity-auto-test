CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT PRIMARY KEY,
    status VARCHAR(32) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS reconciliation_summary (
    run_date VARCHAR(10) PRIMARY KEY,
    reconciled_count INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL
);
