-- ============================================
-- TRANSACTION ANALYTICS STAR SCHEMA
-- ============================================
-- Database: transaction_analytics
-- Purpose: Credit card transaction analytics and business intelligence
-- Schema Type: Star Schema (1 Fact + 3 Dimensions)
-- ============================================

-- ============================================
-- DIMENSION TABLES (Load First)
-- ============================================

-- --------------------------------------------
-- dim_client: Customer Demographics
-- --------------------------------------------
CREATE TABLE dim_client (
    client_id BIGINT PRIMARY KEY,
    current_age INTEGER,
    retirement_age INTEGER,
    birth_year INTEGER,
    birth_month INTEGER,
    gender VARCHAR(10),
    address TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    per_capita_income DECIMAL(10,2),
    yearly_income DECIMAL(12,2),
    total_debt DECIMAL(12,2),
    credit_score INTEGER,
    num_credit_cards INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_client_credit_score ON dim_client(credit_score);
CREATE INDEX idx_client_income ON dim_client(yearly_income);
CREATE INDEX idx_client_location ON dim_client(latitude, longitude);

COMMENT ON TABLE dim_client IS 'Customer demographic and financial information';
COMMENT ON COLUMN dim_client.client_id IS 'Unique customer identifier';
COMMENT ON COLUMN dim_client.credit_score IS 'Credit score (300-850)';

-- --------------------------------------------
-- dim_card: Credit/Debit Card Information
-- --------------------------------------------
CREATE TABLE dim_card (
    card_id BIGINT PRIMARY KEY,
    client_id BIGINT NOT NULL,
    card_brand VARCHAR(50),
    card_type VARCHAR(20),
    card_number VARCHAR(20),
    expires VARCHAR(10),
    cvv VARCHAR(5),
    has_chip VARCHAR(5),
    num_cards_issued INTEGER,
    credit_limit DECIMAL(12,2),
    acct_open_date VARCHAR(10),
    year_pin_last_changed INTEGER,
    card_on_dark_web VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES dim_client(client_id)
);

CREATE INDEX idx_card_client ON dim_card(client_id);
CREATE INDEX idx_card_brand ON dim_card(card_brand);
CREATE INDEX idx_card_type ON dim_card(card_type);
CREATE INDEX idx_card_dark_web ON dim_card(card_on_dark_web);

COMMENT ON TABLE dim_card IS 'Credit and debit card details';
COMMENT ON COLUMN dim_card.card_on_dark_web IS 'Indicates if card number found on dark web';

-- --------------------------------------------
-- dim_merchant: Merchant Location & Category
-- --------------------------------------------
CREATE TABLE dim_merchant (
    merchant_id BIGINT PRIMARY KEY,
    merchant_city VARCHAR(100),
    merchant_state VARCHAR(50),
    zip VARCHAR(10),
    mcc INTEGER,
    mcc_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchant_state ON dim_merchant(merchant_state);
CREATE INDEX idx_merchant_mcc ON dim_merchant(mcc);
CREATE INDEX idx_merchant_city ON dim_merchant(merchant_city);

COMMENT ON TABLE dim_merchant IS 'Merchant location and category information';
COMMENT ON COLUMN dim_merchant.mcc IS 'Merchant Category Code';
COMMENT ON COLUMN dim_merchant.mcc_description IS 'Human-readable category description';

-- ============================================
-- FACT TABLE (Load Last)
-- ============================================

-- --------------------------------------------
-- fact_transactions: Transaction Events
-- --------------------------------------------
CREATE TABLE fact_transactions (
    transaction_id BIGINT PRIMARY KEY,
    client_id BIGINT,
    card_id BIGINT,
    merchant_id BIGINT,
    amount DECIMAL(10,2),
    timestamp TIMESTAMP,
    use_chip VARCHAR(50),
    errors TEXT,
    is_fraud BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES dim_client(client_id),
    FOREIGN KEY (card_id) REFERENCES dim_card(card_id),
    FOREIGN KEY (merchant_id) REFERENCES dim_merchant(merchant_id)
);

-- Performance indexes for analytical queries
CREATE INDEX idx_trans_client ON fact_transactions(client_id);
CREATE INDEX idx_trans_card ON fact_transactions(card_id);
CREATE INDEX idx_trans_merchant ON fact_transactions(merchant_id);
CREATE INDEX idx_trans_timestamp ON fact_transactions(timestamp);
CREATE INDEX idx_trans_fraud ON fact_transactions(is_fraud);
CREATE INDEX idx_trans_amount ON fact_transactions(amount);
CREATE INDEX idx_trans_date_fraud ON fact_transactions(timestamp, is_fraud);

COMMENT ON TABLE fact_transactions IS 'Central fact table storing all transaction events';
COMMENT ON COLUMN fact_transactions.is_fraud IS 'Fraud label from training data';
COMMENT ON COLUMN fact_transactions.errors IS 'Transaction processing errors';

-- ============================================
-- ANALYTICAL VIEWS
-- ============================================

-- Fraud summary by merchant category
CREATE VIEW vw_fraud_by_category AS
SELECT 
    m.mcc_description,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) as fraud_count,
    ROUND(100.0 * SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) as fraud_rate,
    SUM(f.amount) as total_amount,
    SUM(CASE WHEN f.is_fraud THEN f.amount ELSE 0 END) as fraud_amount
FROM fact_transactions f
JOIN dim_merchant m ON f.merchant_id = m.merchant_id
GROUP BY m.mcc_description;

-- Fraud summary by state
CREATE VIEW vw_fraud_by_state AS
SELECT 
    m.merchant_state,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) as fraud_count,
    ROUND(100.0 * SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) as fraud_rate
FROM fact_transactions f
JOIN dim_merchant m ON f.merchant_id = m.merchant_id
WHERE m.merchant_state IS NOT NULL
GROUP BY m.merchant_state;

-- Customer risk profile
CREATE VIEW vw_customer_risk AS
SELECT 
    c.client_id,
    c.credit_score,
    c.yearly_income,
    c.total_debt,
    COUNT(f.transaction_id) as transaction_count,
    SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) as fraud_count,
    SUM(f.amount) as total_spent
FROM dim_client c
LEFT JOIN fact_transactions f ON c.client_id = f.client_id
GROUP BY c.client_id, c.credit_score, c.yearly_income, c.total_debt;

COMMENT ON VIEW vw_fraud_by_category IS 'Fraud analysis by merchant category';
COMMENT ON VIEW vw_fraud_by_state IS 'Geographic fraud distribution';
COMMENT ON VIEW vw_customer_risk IS 'Customer-level fraud risk metrics';

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
GRANT SELECT ON ALL VIEWS IN SCHEMA public TO postgres;
