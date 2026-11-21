# PortfolioPro — Database Architecture & Supabase PostgreSQL Documentation

## 1. Overview & Data Architecture

This directory houses the complete relational database design, DDL scripts, entity-relationship models, and Indian-market seed data for **PortfolioPro - Advanced Stock Trading and Portfolio Management Application** (Project Code: `P15`).

The database is designed according to **Third Normal Form (3NF)** principles and engineered specifically for **Supabase Managed PostgreSQL 15+**.

```
database/
├── schema.sql         # Idempotent 3NF PostgreSQL DDL script creating all 24 tables, constraints, indexes & triggers
├── seed_data.sql      # Indian financial seed data (15 securities, 15 users, 60+ orders, 60+ ledger transactions)
├── er_diagram.mmd     # Valid Mermaid ER diagram illustrating all entities, cardinality & relationships
└── README.md          # Database setup, architecture specifications & execution guide
```

---

## 2. Technology Choices & Precision Standards

### 2.1 Currency & Precision Standards
- **Monetary Values**: All cash balances, order prices, executed prices, brokerage fees, portfolio valuations, and transaction amounts utilize `NUMERIC(18, 4)`. Floating-point numbers are strictly prohibited to prevent financial rounding errors.
- **Ratios & Percentages**: Volatility, Beta, Sharpe, RSI, and percentage returns utilize `NUMERIC(8, 4)`.
- **Market Capitalization & Statements**: High-magnitude corporate valuations utilize `NUMERIC(20, 4)`.

### 2.2 Primary Keys & Identification
- All tables utilize **UUIDv4** primary keys (`UUID DEFAULT gen_random_uuid()`) to guarantee distributed uniqueness and prevent sequential ID enumeration attacks.
- High-frequency domain identifiers utilize human-readable unique business formats:
  - Account Number: `PPRO-100001`
  - Ticket Number: `TICK-2024-1001`
  - Stock Symbol: `RELIANCE`, `TCS`, `INFY`
  - ISIN: `INE002A01018`

### 2.3 Timezone & Audit Standard
- All timestamps use `TIMESTAMPTZ` (Timezone-Aware Timestamp) defaulting to `CURRENT_TIMESTAMP` (stored in UTC, rendered as Indian Standard Time IST / UTC+05:30 on the UI).
- Every mutable table possesses a PostgreSQL trigger (`trg_<table_name>_updated_at`) invoking `update_updated_at_column()` to automatically persist update timestamps.

---

## 3. Entity Catalog by Domain Module

| Module | Table Name | Purpose | Key Constraints & Relations |
| :--- | :--- | :--- | :--- |
| **01. Auth** | `users` | Core identity & RBAC | `email` UNIQUE, `username` UNIQUE, Role CHECK (`CUSTOMER`, `FINANCE_OFFICER`, `ADMIN`) |
| **01. Auth** | `user_profiles` | Personal details & geography | 1:1 with `users` (`user_id` UNIQUE FK) |
| **02. Accounts** | `trading_accounts` | Virtual INR ledger balances | 1:1 with `users`, `cash_balance >= 0`, `account_number` UNIQUE |
| **02. Accounts** | `account_transactions`| Immutable financial audit trail | FK -> `trading_accounts`, `balance_after >= 0` |
| **02. Accounts** | `kyc_records` | Compliance PAN/Aadhaar/Bank | 1:1 with `users`, `verified_by` FK -> `users` |
| **03. Market** | `securities` | NSE/BSE security master | `symbol` UNIQUE, `isin_code` UNIQUE, `lot_size > 0` |
| **03. Market** | `market_quotes` | Live ticker quotes & LTP | 1:1 with `securities`, `ltp > 0`, `high >= low` |
| **03. Market** | `historical_prices` | Daily OHLCV candle bars | FK -> `securities`, UNIQUE on `(security_id, trade_date)` |
| **03. Market** | `watchlists` | User-defined ticker lists | FK -> `users`, UNIQUE on `(user_id, name)` |
| **03. Market** | `watchlist_items` | Tickers pinned in watchlist | FK -> `watchlists`, FK -> `securities`, UNIQUE on `(watchlist_id, security_id)` |
| **04. Trading** | `trade_orders` | Equity order submissions | FK -> `users`, FK -> `securities`, FK -> `trading_accounts`, `quantity > 0` |
| **04. Trading** | `trade_executions`| Executed trade contract notes | FK -> `trade_orders`, FK -> `securities`, FK -> `users` |
| **05. Portfolio**| `portfolios` | High-level portfolio grouping | FK -> `users`, UNIQUE on `(user_id, name)` |
| **05. Portfolio**| `portfolio_holdings`| Aggregated stock positions | FK -> `portfolios`, FK -> `securities`, UNIQUE on `(portfolio_id, security_id)` |
| **05. Portfolio**| `portfolio_snapshots`| Daily equity curve snapshots | FK -> `portfolios`, UNIQUE on `(portfolio_id, snapshot_date)` |
| **06. Risk** | `risk_assessments` | Beta, Sharpe, VaR 95% scores | FK -> `portfolios`, `risk_score` (1–100), Category CHECK |
| **06. Risk** | `risk_thresholds` | User risk tolerance limits | FK -> `users`, `max_single_stock_pct` |
| **07. Technical**| `technical_indicators`| RSI 14, MACD, SMA 20/50/200 | FK -> `securities`, UNIQUE on `(security_id, calculation_date)` |
| **07. Technical**| `user_chart_preferences`| Indicator & chart settings | FK -> `users`, JSONB config storage |
| **08. Fundamental**| `fundamental_metrics`| P/E, EPS, ROE, Health score | 1:1 with `securities`, `health_score` (1–10) |
| **08. Fundamental**| `company_financials` | Balance sheets & quarterly P&L | FK -> `securities`, UNIQUE on `(security_id, period_name)` |
| **09. Alerts** | `price_alerts` | Price threshold triggers | FK -> `users`, FK -> `securities`, Condition CHECK |
| **09. Alerts** | `user_notifications` | Push notification feed | FK -> `users`, Category CHECK, `is_read` flag |
| **09. Alerts** | `system_announcements`| Platform-wide announcements | FK -> `users` (`created_by`), Priority CHECK |
| **10. Support** | `support_tickets` | Customer service helpdesk | FK -> `users`, `ticket_number` UNIQUE, Category/Priority CHECK |
| **10. Support** | `support_messages` | Threaded discussion messages | FK -> `support_tickets`, FK -> `users` (`sender_id`) |

---

## 4. Setup Guide for Supabase PostgreSQL

### 4.1 Prerequisites
1. Create a project at [supabase.com](https://supabase.com).
2. Retrieve the database credentials from **Project Settings > Database**:
   - Host: `db.[PROJECT-REF].supabase.co`
   - Direct Port (for schema migrations): `5432`
   - Pooled Port via Supavisor (for API runtime): `6543`
   - User: `postgres`
   - Password: `[YOUR-PASSWORD]`
   - Database: `postgres`

### 4.2 Applying Schema and Seed Data

#### Option A: Supabase SQL Editor (Web UI)
1. Navigate to the **SQL Editor** tab in the Supabase Dashboard.
2. Click **New Query**.
3. Copy and paste the entire contents of `database/schema.sql` and click **Run**.
4. Open a second query tab, paste `database/seed_data.sql`, and click **Run**.

#### Option B: Terminal via `psql`
```bash
# Apply Schema DDL
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" -f database/schema.sql

# Load Indian Financial Seed Data
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" -f database/seed_data.sql
```

---

## 5. Seed Data Context & Validation Edge Cases

`database/seed_data.sql` contains pre-populated records adhering to the academic specifications:
- **15 Indian Equities**: Large-cap bluechips across Energy, IT, Banking, FMCG, Automobile, and Healthcare (`RELIANCE`, `TCS`, `HDFCBANK`, `INFY`, `ICICIBANK`, `TATASTEEL`, `SBIN`, `BHARTIARTL`, `ITC`, `LT`, `HINDUNILVR`, `WIPRO`, `BAJFINANCE`, `MARUTI`, `SUNPHARMA`).
- **15 Platform Users**:
  - `admin@portfoliopro.in` (Platform Superadministrator)
  - `suresh.deshmukh@portfoliopro.in` (Senior Finance Officer)
  - `kavita.sharma@portfoliopro.in` (Risk & Compliance Finance Officer)
  - 9 Verified Customer Investors with realistic trading profiles
  - 3 Validation Edge-Case Users
- **5 Academic Validation Edge Cases**:
  1. *Maximum Field Length*: User with 150-character username and long name string.
  2. *Duplicate-Looking Names*: Two users named Aarav Sharma (retail investor vs corporate account) testing unique constraint handling.
  3. *Empty Optional Attributes*: User with empty phone number, empty bio, and empty city/state fields.
  4. *Zero Financial Balance*: Customer account with exactly `₹ 0.0000` cash balance and no positions to test pre-trade blocking.
  5. *Penny Stock / Extreme Pricing*: Microcap stock `VIRTUALPENNY` trading at `₹ 1.85` testing low-price calculations and high volatility.
