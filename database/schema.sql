-- =============================================================================
-- PortfolioPro (Project Code: P15) - Advanced Stock Trading & Portfolio Management
-- Database Definition Script (DDL) — Supabase PostgreSQL 15+
-- Normalization: Third Normal Form (3NF)
-- Financial Precision: NUMERIC(18, 4) for Currency, NUMERIC(8, 4) for Percentages
-- Timezone Standard: UTC / TIMESTAMPTZ (Mapped to IST UTC+05:30 on Presentation)
-- =============================================================================

-- Enable required cryptographic and UUID generation extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Clean teardown of existing schema objects (Reverse dependency order)
DROP TABLE IF EXISTS support_messages CASCADE;
DROP TABLE IF EXISTS support_tickets CASCADE;
DROP TABLE IF EXISTS system_announcements CASCADE;
DROP TABLE IF EXISTS user_notifications CASCADE;
DROP TABLE IF EXISTS price_alerts CASCADE;
DROP TABLE IF EXISTS company_financials CASCADE;
DROP TABLE IF EXISTS fundamental_metrics CASCADE;
DROP TABLE IF EXISTS user_chart_preferences CASCADE;
DROP TABLE IF EXISTS technical_indicators CASCADE;
DROP TABLE IF EXISTS risk_thresholds CASCADE;
DROP TABLE IF EXISTS risk_assessments CASCADE;
DROP TABLE IF EXISTS portfolio_snapshots CASCADE;
DROP TABLE IF EXISTS portfolio_holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS trade_executions CASCADE;
DROP TABLE IF EXISTS trade_orders CASCADE;
DROP TABLE IF EXISTS watchlist_items CASCADE;
DROP TABLE IF EXISTS watchlists CASCADE;
DROP TABLE IF EXISTS historical_prices CASCADE;
DROP TABLE IF EXISTS market_quotes CASCADE;
DROP TABLE IF EXISTS securities CASCADE;
DROP TABLE IF EXISTS kyc_records CASCADE;
DROP TABLE IF EXISTS account_transactions CASCADE;
DROP TABLE IF EXISTS trading_accounts CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop trigger function if exists
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;

-- =============================================================================
-- Shared Automation Functions
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MODULE 01: User Authentication & Role Management (P15-E02)
-- =============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'CUSTOMER' 
        CHECK (role IN ('CUSTOMER', 'FINANCE_OFFICER', 'ADMIN')),
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    phone_number VARCHAR(20) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    avatar_url VARCHAR(500) NOT NULL DEFAULT '',
    bio TEXT NOT NULL DEFAULT '',
    city VARCHAR(100) NOT NULL DEFAULT '',
    state VARCHAR(100) NOT NULL DEFAULT '',
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    pincode VARCHAR(20) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

CREATE TRIGGER trg_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- MODULE 02: Account Management & KYC Compliance (P15-E03)
-- =============================================================================

CREATE TABLE trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_number VARCHAR(32) UNIQUE NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    cash_balance NUMERIC(18, 4) NOT NULL DEFAULT 500000.0000 
        CHECK (cash_balance >= 0),
    margin_used NUMERIC(18, 4) NOT NULL DEFAULT 0.0000 
        CHECK (margin_used >= 0),
    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' 
        CHECK (account_status IN ('ACTIVE', 'FROZEN', 'SUSPENDED', 'CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trading_accounts_user ON trading_accounts(user_id);
CREATE INDEX idx_trading_accounts_status ON trading_accounts(account_status);

CREATE TRIGGER trg_trading_accounts_updated_at
BEFORE UPDATE ON trading_accounts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE account_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES trading_accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL 
        CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRADE_DEBIT', 'TRADE_CREDIT', 'FEE_DEBIT')),
    amount NUMERIC(18, 4) NOT NULL 
        CHECK (amount > 0),
    balance_after NUMERIC(18, 4) NOT NULL 
        CHECK (balance_after >= 0),
    reference_note TEXT NOT NULL DEFAULT '',
    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED' 
        CHECK (status IN ('PENDING', 'COMPLETED', 'REJECTED', 'CANCELLED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acct_tx_account ON account_transactions(account_id);
CREATE INDEX idx_acct_tx_type ON account_transactions(transaction_type);
CREATE INDEX idx_acct_tx_status ON account_transactions(status);
CREATE INDEX idx_acct_tx_created ON account_transactions(created_at DESC);

CREATE TRIGGER trg_account_transactions_updated_at
BEFORE UPDATE ON account_transactions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE kyc_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pan_number VARCHAR(10) NOT NULL,
    aadhaar_masked VARCHAR(12) NOT NULL,
    bank_account_number VARCHAR(30) NOT NULL,
    bank_ifsc VARCHAR(11) NOT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' 
        CHECK (verification_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    rejection_reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_user ON kyc_records(user_id);
CREATE INDEX idx_kyc_status ON kyc_records(verification_status);

CREATE TRIGGER trg_kyc_records_updated_at
BEFORE UPDATE ON kyc_records
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- MODULE 03: Market Data & Watchlists (P15-E04)
-- =============================================================================

CREATE TABLE securities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    exchange VARCHAR(10) NOT NULL DEFAULT 'NSE' 
        CHECK (exchange IN ('NSE', 'BSE')),
    sector VARCHAR(100) NOT NULL,
    industry VARCHAR(100) NOT NULL DEFAULT '',
    lot_size INTEGER NOT NULL DEFAULT 1 
        CHECK (lot_size > 0),
    isin_code VARCHAR(12) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_securities_symbol ON securities(symbol);
CREATE INDEX idx_securities_sector ON securities(sector);
CREATE INDEX idx_securities_exchange ON securities(exchange);

CREATE TRIGGER trg_securities_updated_at
BEFORE UPDATE ON securities
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE market_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id UUID UNIQUE NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    ltp NUMERIC(18, 4) NOT NULL CHECK (ltp > 0),
    open_price NUMERIC(18, 4) NOT NULL CHECK (open_price > 0),
    high_price NUMERIC(18, 4) NOT NULL CHECK (high_price >= low_price),
    low_price NUMERIC(18, 4) NOT NULL CHECK (low_price > 0),
    close_price NUMERIC(18, 4) NOT NULL CHECK (close_price > 0),
    volume BIGINT NOT NULL DEFAULT 0 CHECK (volume >= 0),
    change_amount NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    change_percent NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    week_52_high NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    week_52_low NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_market_quotes_security ON market_quotes(security_id);
CREATE INDEX idx_market_quotes_ltp ON market_quotes(ltp);

CREATE TRIGGER trg_market_quotes_updated_at
BEFORE UPDATE ON market_quotes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE historical_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    open NUMERIC(18, 4) NOT NULL CHECK (open > 0),
    high NUMERIC(18, 4) NOT NULL CHECK (high >= low),
    low NUMERIC(18, 4) NOT NULL CHECK (low > 0),
    close NUMERIC(18, 4) NOT NULL CHECK (close > 0),
    volume BIGINT NOT NULL DEFAULT 0 CHECK (volume >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_historical_price_security_date UNIQUE (security_id, trade_date)
);

CREATE INDEX idx_historical_prices_sec_date ON historical_prices(security_id, trade_date DESC);

CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_watchlist_user_name UNIQUE (user_id, name)
);

CREATE INDEX idx_watchlists_user ON watchlists(user_id);

CREATE TRIGGER trg_watchlists_updated_at
BEFORE UPDATE ON watchlists
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE watchlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_watchlist_security UNIQUE (watchlist_id, security_id)
);

CREATE INDEX idx_watchlist_items_wl ON watchlist_items(watchlist_id);

-- =============================================================================
-- MODULE 04: Trading Engine (P15-E05)
-- =============================================================================

CREATE TABLE trade_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES trading_accounts(id) ON DELETE CASCADE,
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    order_type VARCHAR(10) NOT NULL 
        CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP_LOSS')),
    transaction_type VARCHAR(10) NOT NULL 
        CHECK (transaction_type IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    filled_quantity INTEGER NOT NULL DEFAULT 0 
        CHECK (filled_quantity >= 0 AND filled_quantity <= quantity),
    limit_price NUMERIC(18, 4) CHECK (limit_price IS NULL OR limit_price > 0),
    executed_price NUMERIC(18, 4) CHECK (executed_price IS NULL OR executed_price > 0),
    order_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' 
        CHECK (order_status IN ('PENDING', 'FILLED', 'PARTIALLY_FILLED', 'CANCELLED', 'REJECTED')),
    rejection_reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trade_orders_user ON trade_orders(user_id);
CREATE INDEX idx_trade_orders_security ON trade_orders(security_id);
CREATE INDEX idx_trade_orders_status ON trade_orders(order_status);
CREATE INDEX idx_trade_orders_created ON trade_orders(created_at DESC);

CREATE TRIGGER trg_trade_orders_updated_at
BEFORE UPDATE ON trade_orders
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE trade_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES trade_orders(id) ON DELETE CASCADE,
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    execution_price NUMERIC(18, 4) NOT NULL CHECK (execution_price > 0),
    brokerage_fee NUMERIC(18, 4) NOT NULL DEFAULT 0.0000 CHECK (brokerage_fee >= 0),
    net_amount NUMERIC(18, 4) NOT NULL CHECK (net_amount > 0),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trade_exec_order ON trade_executions(order_id);
CREATE INDEX idx_trade_exec_user ON trade_executions(user_id);
CREATE INDEX idx_trade_exec_security ON trade_executions(security_id);
CREATE INDEX idx_trade_exec_date ON trade_executions(executed_at DESC);

-- =============================================================================
-- MODULE 05: Portfolio Management (P15-E06)
-- =============================================================================

CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'Primary Portfolio',
    is_default BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_portfolio_user_name UNIQUE (user_id, name)
);

CREATE INDEX idx_portfolios_user ON portfolios(user_id);

CREATE TRIGGER trg_portfolios_updated_at
BEFORE UPDATE ON portfolios
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    average_buy_price NUMERIC(18, 4) NOT NULL CHECK (average_buy_price >= 0),
    total_invested NUMERIC(18, 4) NOT NULL DEFAULT 0.0000 CHECK (total_invested >= 0),
    realized_pnl NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_portfolio_security UNIQUE (portfolio_id, security_id)
);

CREATE INDEX idx_portfolio_holdings_port ON portfolio_holdings(portfolio_id);
CREATE INDEX idx_portfolio_holdings_sec ON portfolio_holdings(security_id);

CREATE TRIGGER trg_portfolio_holdings_updated_at
BEFORE UPDATE ON portfolio_holdings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    total_equity_value NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    total_cash_value NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    total_portfolio_value NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    day_pnl NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    day_pnl_percent NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_portfolio_snapshot_date UNIQUE (portfolio_id, snapshot_date)
);

CREATE INDEX idx_portfolio_snapshots_date ON portfolio_snapshots(portfolio_id, snapshot_date DESC);

-- =============================================================================
-- MODULE 06: Risk Management (P15-E07)
-- =============================================================================

CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    portfolio_beta NUMERIC(8, 4) NOT NULL DEFAULT 1.0000,
    sharpe_ratio NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    var_95_daily NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    concentration_index NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    risk_score INTEGER NOT NULL DEFAULT 50 
        CHECK (risk_score >= 1 AND risk_score <= 100),
    risk_category VARCHAR(20) NOT NULL DEFAULT 'MODERATE' 
        CHECK (risk_category IN ('CONSERVATIVE', 'MODERATE', 'AGGRESSIVE', 'HIGH_RISK')),
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_assessments_portfolio ON risk_assessments(portfolio_id);
CREATE INDEX idx_risk_assessments_score ON risk_assessments(risk_score);

CREATE TRIGGER trg_risk_assessments_updated_at
BEFORE UPDATE ON risk_assessments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE risk_thresholds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    max_drawdown_limit NUMERIC(8, 4) NOT NULL DEFAULT 20.0000,
    max_single_stock_pct NUMERIC(8, 4) NOT NULL DEFAULT 25.0000,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_thresholds_user ON risk_thresholds(user_id);

CREATE TRIGGER trg_risk_thresholds_updated_at
BEFORE UPDATE ON risk_thresholds
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- MODULE 07: Technical Analysis (P15-E08)
-- =============================================================================

CREATE TABLE technical_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL,
    rsi_14 NUMERIC(8, 4) NOT NULL CHECK (rsi_14 >= 0 AND rsi_14 <= 100),
    macd_line NUMERIC(12, 4) NOT NULL DEFAULT 0.0000,
    macd_signal NUMERIC(12, 4) NOT NULL DEFAULT 0.0000,
    macd_hist NUMERIC(12, 4) NOT NULL DEFAULT 0.0000,
    sma_20 NUMERIC(18, 4) NOT NULL CHECK (sma_20 > 0),
    sma_50 NUMERIC(18, 4) NOT NULL CHECK (sma_50 > 0),
    sma_200 NUMERIC(18, 4) NOT NULL CHECK (sma_200 > 0),
    ema_20 NUMERIC(18, 4) NOT NULL CHECK (ema_20 > 0),
    overall_signal VARCHAR(20) NOT NULL DEFAULT 'NEUTRAL' 
        CHECK (overall_signal IN ('STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL')),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_technical_security_date UNIQUE (security_id, calculation_date)
);

CREATE INDEX idx_technical_indicators_sec ON technical_indicators(security_id, calculation_date DESC);
CREATE INDEX idx_technical_indicators_signal ON technical_indicators(overall_signal);

CREATE TRIGGER trg_technical_indicators_updated_at
BEFORE UPDATE ON technical_indicators
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE user_chart_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chart_type VARCHAR(20) NOT NULL DEFAULT 'CANDLESTICK' 
        CHECK (chart_type IN ('CANDLESTICK', 'LINE', 'AREA')),
    timeframe VARCHAR(10) NOT NULL DEFAULT '1D' 
        CHECK (timeframe IN ('1D', '1W', '1M', '1Y')),
    default_indicators JSONB NOT NULL DEFAULT '{"sma_20": true, "rsi_14": true, "macd": true}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chart_pref_user ON user_chart_preferences(user_id);

CREATE TRIGGER trg_user_chart_preferences_updated_at
BEFORE UPDATE ON user_chart_preferences
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- MODULE 08: Fundamental Analysis (P15-E09)
-- =============================================================================

CREATE TABLE fundamental_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id UUID UNIQUE NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    market_cap NUMERIC(20, 4) NOT NULL CHECK (market_cap > 0),
    pe_ratio NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    pb_ratio NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    eps NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    dividend_yield NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    debt_to_equity NUMERIC(10, 4) NOT NULL DEFAULT 0.0000,
    roe NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    book_value NUMERIC(18, 4) NOT NULL DEFAULT 0.0000,
    health_score INTEGER NOT NULL DEFAULT 5 
        CHECK (health_score >= 1 AND health_score <= 10),
    financial_year VARCHAR(10) NOT NULL DEFAULT '2024-25',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fundamental_security ON fundamental_metrics(security_id);
CREATE INDEX idx_fundamental_pe ON fundamental_metrics(pe_ratio);
CREATE INDEX idx_fundamental_health ON fundamental_metrics(health_score);

CREATE TRIGGER trg_fundamental_metrics_updated_at
BEFORE UPDATE ON fundamental_metrics
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE company_financials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    period_name VARCHAR(20) NOT NULL,
    revenue NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    net_profit NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    operating_margin NUMERIC(8, 4) NOT NULL DEFAULT 0.0000,
    ebitda NUMERIC(20, 4) NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_company_financial_period UNIQUE (security_id, period_name)
);

CREATE INDEX idx_company_financials_sec ON company_financials(security_id);

-- =============================================================================
-- MODULE 09: Notification and Alerts (P15-E10)
-- =============================================================================

CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    security_id UUID NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    condition VARCHAR(20) NOT NULL 
        CHECK (condition IN ('ABOVE', 'BELOW', 'PCT_CHANGE')),
    target_value NUMERIC(18, 4) NOT NULL CHECK (target_value > 0),
    is_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_alerts_user ON price_alerts(user_id);
CREATE INDEX idx_price_alerts_active ON price_alerts(security_id, is_active, is_triggered);

CREATE TRIGGER trg_price_alerts_updated_at
BEFORE UPDATE ON price_alerts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE user_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    category VARCHAR(30) NOT NULL DEFAULT 'SYSTEM' 
        CHECK (category IN ('TRADE', 'PRICE_ALERT', 'ACCOUNT', 'SYSTEM', 'SUPPORT')),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    link_url VARCHAR(500) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_notif_user_read ON user_notifications(user_id, is_read);
CREATE INDEX idx_user_notif_created ON user_notifications(created_at DESC);

CREATE TABLE system_announcements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'NORMAL' 
        CHECK (priority IN ('NORMAL', 'URGENT')),
    valid_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_announcements_created ON system_announcements(created_at DESC);

-- =============================================================================
-- MODULE 10: Customer Support Helpdesk (P15-E11)
-- =============================================================================

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_number VARCHAR(32) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(30) NOT NULL 
        CHECK (category IN ('TRADE_DISPUTE', 'DEPOSIT_WITHDRAWAL', 'KYC_ACCOUNT', 'TECHNICAL', 'GENERAL')),
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' 
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    status VARCHAR(30) NOT NULL DEFAULT 'OPEN' 
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'PENDING_CUSTOMER', 'RESOLVED', 'CLOSED')),
    subject VARCHAR(255) NOT NULL,
    related_order_id UUID REFERENCES trade_orders(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_assigned ON support_tickets(assigned_to);

CREATE TRIGGER trg_support_tickets_updated_at
BEFORE UPDATE ON support_tickets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    is_internal_note BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_support_messages_ticket ON support_messages(ticket_id, created_at ASC);
