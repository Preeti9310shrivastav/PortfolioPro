# PortfolioPro — Comprehensive Module Feature Checklist

This document details the functional specifications, database models, REST API contracts, UI views, and testing requirements across all 10 core functional modules and the 2 lifecycle epics. Every feature item is currently marked as **Pending** `[ ]`.

---

## Module Index

- [Module 00: Project Setup, Git Workflow & Architecture](#module-00-project-setup-git-workflow--architecture-p15-e01)
- [Module 01: User Authentication](#module-01-user-authentication-p15-e02)
- [Module 02: Account Management](#module-02-account-management-p15-e03)
- [Module 03: Market Data](#module-03-market-data-p15-e04)
- [Module 04: Trading Engine](#module-04-trading-engine-p15-e05)
- [Module 05: Portfolio Management](#module-05-portfolio-management-p15-e06)
- [Module 06: Risk Management](#module-06-risk-management-p15-e07)
- [Module 07: Technical Analysis](#module-07-technical-analysis-p15-e08)
- [Module 08: Fundamental Analysis](#module-08-fundamental-analysis-p15-e09)
- [Module 09: Notification and Alerts](#module-09-notification-and-alerts-p15-e10)
- [Module 10: Customer Support](#module-10-customer-support-p15-e11)
- [Module 11: Testing, Documentation and Release](#module-11-testing-documentation-and-release-p15-e12)

---

## Module 00: Project Setup, Git Workflow & Architecture (`P15-E01`)
*Sprint 0 | 6 Hours | 10 Story Points | Priority: Must | Tag: v0.1.0*

### Checklist
- [ ] **Repository Architecture**: Establish Git repository `mca2-fsdpython-portfoliopro` with `main` and `develop` branches.
- [ ] **Folder Structure**: Configure root layout with `backend/`, `frontend/`, `database/`, and `docs/`.
- [ ] **Environment Configuration**: Create `.gitignore` and `.env.example` templates covering Python, Node, and database secrets.
- [ ] **Database Design**: Create 3NF relational schema DDL in `database/schema.sql` targeting Supabase PostgreSQL.
- [ ] **Dataset Generation**: Create Indian-context mock dataset in `database/seed_data.sql` with dates 2024–2026, INR amounts.
- [ ] **Wireframing**: Produce UI wireframes for Authentication, Dashboard, and Order Placement in `docs/wireframes/`.
- [ ] **Backend Skeleton**: Initialize Django 5.x project with modular apps, DRF configuration, and CORS middleware.
- [ ] **Frontend Skeleton**: Initialize React 18 with Vite, Bootstrap 5, React Router v6, and Axios client.
- [ ] **RBAC Navigation Base**: Implement authentication state provider and role-differentiated navigation layout.

---

## Module 01: User Authentication (`P15-E02`)
*Sprint 1 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D04*

### Scope & Business Purpose
Provides secure registration, PBKDF2 password hashing, JWT token issuance, session maintenance, and role-based permissions (`Customer` vs `Finance Officer`).

### Database Entities
- `custom_user`: `id` (UUID/BigSerial), `username`, `email` (UNIQUE), `password_hash`, `role` (`CUSTOMER`, `FINANCE_OFFICER`, `ADMIN`), `first_name`, `last_name`, `phone_number`, `is_active`, `is_staff`, `date_joined`, `last_login`.
- `user_profile`: `id`, `user_id` (FK -> `custom_user`), `avatar_url`, `bio`, `city`, `state`, `country`, `pincode`, `created_at`, `updated_at`.

### REST API Endpoints
- `POST /api/auth/register/` — Register new user with input validation.
- `POST /api/auth/login/` — Authenticate credentials; return JWT access & refresh tokens with user role.
- `POST /api/auth/token/refresh/` — Refresh expired access token.
- `GET /api/auth/profile/` — Fetch authenticated user profile.
- `PUT/PATCH /api/auth/profile/` — Update user profile details.
- `GET /api/auth/users/` — Finance Officer endpoint: List all platform users with role/status filters.
- `PATCH /api/auth/users/<id>/status/` — Finance Officer endpoint: Toggle user active/inactive status.

### UI Views & Components
- `RegisterView.jsx`: Responsive sign-up form with instant field validations.
- `LoginView.jsx`: Secure sign-in form with "Remember Me" and demo credentials autofill.
- `ProfileView.jsx`: Customer profile management and contact details editor.
- `UserManagementView.jsx`: Finance Officer table view with user search, status filter, and audit logs.

### Feature Checklist
- [ ] **User Registration API**: Validate unique email, valid phone format, and strong password.
- [ ] **JWT Authentication**: Issue standard JWT claims (user ID, role, username) with auto-refresh mechanism.
- [ ] **Role Protection Middleware**: Enforce DRF `IsAuthenticated` and custom `IsCustomer` / `IsFinanceOfficer` permissions.
- [ ] **Frontend Route Guards**: Restrict `/portal/*` routes to Customers and `/admin-fo/*` routes to Finance Officers.
- [ ] **Profile Management**: Enable editing of contact details with immediate UI feedback.
- [ ] **Supervisory User Audit**: Enable Finance Officers to filter users by role and toggle account access.
- [ ] **Pytest Unit Tests**: Test user registration, token generation, invalid credentials, and role permission boundaries.

---

## Module 02: Account Management (`P15-E03`)
*Sprint 1 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D05*

### Scope & Business Purpose
Manages customer virtual trading accounts, cash ledger balances, fund deposits/withdrawals, and KYC compliance records.

### Database Entities
- `trading_account`: `id`, `user_id` (FK -> `custom_user`, UNIQUE), `account_number` (UNIQUE, e.g. `PPRO-100234`), `currency` (`INR`), `cash_balance` (`DECIMAL(18, 4)`), `margin_used` (`DECIMAL(18, 4)`), `account_status` (`ACTIVE`, `FROZEN`, `SUSPENDED`), `created_at`.
- `account_transaction`: `id`, `account_id` (FK -> `trading_account`), `transaction_type` (`DEPOSIT`, `WITHDRAWAL`, `TRADE_DEBIT`, `TRADE_CREDIT`), `amount` (`DECIMAL(18, 4)`), `balance_after` (`DECIMAL(18, 4)`), `reference_note`, `status` (`COMPLETED`, `PENDING`, `REJECTED`), `created_at`.
- `kyc_record`: `id`, `user_id` (FK -> `custom_user`), `pan_number`, `aadhaar_masked`, `bank_account_number`, `bank_ifsc`, `verification_status` (`PENDING`, `VERIFIED`, `REJECTED`), `verified_by` (FK -> `custom_user`), `verified_at`.

### REST API Endpoints
- `GET /api/accounts/summary/` — Retrieve trading account balance, cash, and account number.
- `POST /api/accounts/deposit/` — Simulate instant virtual fund deposit.
- `POST /api/accounts/withdraw/` — Submit fund withdrawal request (validates against available unencumbered balance).
- `GET /api/accounts/transactions/` — List paginated cash ledger transactions for authenticated user.
- `POST /api/accounts/kyc/` — Submit KYC verification details.
- `GET /api/accounts/admin/all/` — Finance Officer: List all customer trading accounts, balances, and KYC states.
- `PATCH /api/accounts/admin/kyc/<id>/verify/` — Finance Officer: Approve or reject customer KYC.

### UI Views & Components
- `AccountDashboardView.jsx`: Balance card, cash vs margin meter, recent transaction ledger.
- `DepositWithdrawModal.jsx`: Modal for fund management with validation against over-withdrawal.
- `KYCSubmissionView.jsx`: Structured KYC form with Indian PAN and IFSC regex validators.
- `FOAccountAuditView.jsx`: Finance Officer supervisory grid with balance filters and KYC action buttons.

### Feature Checklist
- [ ] **Auto Account Provisioning**: Automatically create a `trading_account` upon customer registration with default seed balance (e.g. ₹ 5,00,000 virtual INR).
- [ ] **Fund Deposit Engine**: Atomic balance credit and ledger transaction generation.
- [ ] **Fund Withdrawal Engine**: Pre-check ensuring withdrawal amount <= available unencumbered cash.
- [ ] **KYC Data Pipeline**: Captures PAN (formatted `[A-Z]{5}[0-9]{4}[A-Z]{1}`), IFSC, and bank details.
- [ ] **Finance Officer KYC Review**: Workflow allowing Finance Officers to review and approve/reject customer KYC.
- [ ] **Transaction Export**: Ability to filter and view ledger entries by date and transaction type.
- [ ] **Pytest Unit Tests**: Test concurrent deposit/withdrawal, negative amount rejection, and KYC transitions.

---

## Module 03: Market Data (`P15-E04`)
*Sprint 1 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D06*

### Scope & Business Purpose
Provides equity security masters, live quotes, daily price bars (OHLCV), sector indices, and customer customizable watchlists.

### Database Entities
- `security`: `id`, `symbol` (UNIQUE, e.g. `RELIANCE`), `company_name`, `exchange` (`NSE`, `BSE`), `sector` (e.g. `Energy`, `IT`, `Banking`), `lot_size`, `is_active`, `isin_code`.
- `market_quote`: `id`, `security_id` (FK -> `security`, UNIQUE), `ltp` (`DECIMAL(12, 2)`), `open_price`, `high_price`, `low_price`, `close_price` (previous close), `volume` (BigInt), `change_amount`, `change_percent`, `updated_at`.
- `historical_price`: `id`, `security_id` (FK -> `security`), `trade_date`, `open`, `high`, `low`, `close`, `volume`.
- `watchlist_item`: `id`, `user_id` (FK -> `custom_user`), `security_id` (FK -> `security`), `display_order`, `created_at`.

### REST API Endpoints
- `GET /api/market/stocks/` — List all active stocks with sector/exchange filters and search.
- `GET /api/market/quotes/<symbol>/` — Retrieve latest live quote and day statistics for a specific ticker.
- `GET /api/market/history/<symbol>/?timeframe=1M` — Fetch historical daily OHLCV bars.
- `GET /api/market/watchlist/` — List customer pinned watchlist items with live quote data.
- `POST /api/market/watchlist/` — Add a stock to customer watchlist.
- `DELETE /api/market/watchlist/<symbol>/` — Remove stock from watchlist.
- `GET /api/market/admin/feed-status/` — Finance Officer: View system market feed health, tick counts, and update timestamps.

### UI Views & Components
- `MarketOverviewView.jsx`: Stock ticker carousel, top gainers, top losers, and market indices (NIFTY 50, SENSEX).
- `StockSearchView.jsx`: Search bar with instant autocomplete, sector filters, and one-click quote access.
- `WatchlistPanel.jsx`: Compact side drawer showing pinned tickers with dynamic green/red price flashing.
- `FOMarketFeedView.jsx`: Back-office market feed status dashboard.

### Feature Checklist
- [ ] **Security Master Seed**: Populate Indian large-cap and mid-cap equities (RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, TATASTEEL, etc.).
- [ ] **Real-time Quote Simulator**: Background engine that calculates realistic random-walk price updates within circuit limits (e.g., ±5%).
- [ ] **Watchlist CRUD**: Full ability for customers to pin, view, and unpin securities.
- [ ] **Sector Grouping**: Filter and group equities by industry sector.
- [ ] **Top Gainers & Losers**: Dynamic sorting calculating highest percentage gainers and losers.
- [ ] **Historical Price Endpoints**: Deliver time-series OHLCV data formatted for charting libraries.
- [ ] **Pytest Unit Tests**: Test quote calculation, watchlist uniqueness constraints, and ticker search queries.

---

## Module 04: Trading Engine (`P15-E05`)
*Sprint 1 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D07*

### Scope & Business Purpose
Validates and executes equity orders (Market, Limit), performs pre-trade balance/holding checks, ensures ACID transactional consistency, and updates order books.

### Database Entities
- `trade_order`: `id`, `user_id` (FK -> `custom_user`), `security_id` (FK -> `security`), `order_type` (`MARKET`, `LIMIT`), `transaction_type` (`BUY`, `SELL`), `quantity` (Int), `limit_price` (`DECIMAL(12, 2)`, NULL for Market), `executed_price` (`DECIMAL(12, 2)`), `order_status` (`PENDING`, `FILLED`, `CANCELLED`, `REJECTED`), `rejection_reason`, `created_at`, `executed_at`.
- `trade_execution`: `id`, `order_id` (FK -> `trade_order`), `security_id` (FK -> `security`), `buyer_id` (FK -> `custom_user`), `seller_id` (FK -> `custom_user`, nullable for market-maker), `quantity`, `execution_price` (`DECIMAL(12, 2)`), `brokerage_fee` (`DECIMAL(10, 2)`), `executed_at`.

### REST API Endpoints
- `POST /api/trading/orders/` — Place a new Buy or Sell order (executes pre-trade validation).
- `GET /api/trading/orders/` — List authenticated user's order book (pending, completed, cancelled).
- `POST /api/trading/orders/<id>/cancel/` — Cancel a pending limit order.
- `GET /api/trading/executions/` — List trade execution confirmations and contract notes.
- `GET /api/trading/admin/orders/` — Finance Officer: List and filter all platform orders with date, status, and ticker filters.
- `POST /api/trading/admin/orders/<id>/intervene/` — Finance Officer: Cancel or freeze an anomalous order.

### UI Views & Components
- `OrderPlacementCard.jsx`: Buy/Sell tabbed widget with Market/Limit toggle, quantity stepper, estimated value, and brokerage fee preview.
- `OrderBookTable.jsx`: Tabbed view of Active Orders vs Trade History with status badges and cancellation buttons.
- `OrderConfirmationModal.jsx`: Pre-execution confirmation displaying total cost, order type, and target ticker.
- `FOOrderAuditView.jsx`: Comprehensive back-office trade audit grid with CSV export option.

### Feature Checklist
- [ ] **Atomic Order Processing**: Wrap order validation, cash deduction, and position updates in `@transaction.atomic`.
- [ ] **Pre-Trade Cash Validation**: Ensure Customer `cash_balance >= (quantity * execution_price) + brokerage` for Buy orders.
- [ ] **Pre-Trade Holding Validation**: Ensure Customer holds `>= quantity` for Sell orders.
- [ ] **Market Order Instant Fill**: Simulate immediate execution against current LTP with realistic slippage limits.
- [ ] **Limit Order Queue**: Store pending limit orders until market price satisfies the limit threshold.
- [ ] **Order Cancellation**: Release held funds/shares upon order cancellation.
- [ ] **Finance Officer Trade Audit**: Allow supervisory inspection of all transactions across all customer accounts.
- [ ] **Pytest Unit Tests**: Test insufficient balance rejection, short selling block, limit order trigger, and atomic rollback on simulated database failure.

---

## Module 05: Portfolio Management (`P15-E06`)
*Sprint 2 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D08*

### Scope & Business Purpose
Tracks customer equity holdings, average acquisition costs, unrealized/realized P&L, sector weights, and historical net-worth equity curves.

### Database Entities
- `portfolio_holding`: `id`, `user_id` (FK -> `custom_user`), `security_id` (FK -> `security`), `quantity` (Int), `average_buy_price` (`DECIMAL(12, 2)`), `total_invested` (`DECIMAL(18, 4)`), `realized_pnl` (`DECIMAL(18, 4)`), `last_updated`. UNIQUE constraint on `(user_id, security_id)`.
- `portfolio_snapshot`: `id`, `user_id` (FK -> `custom_user`), `snapshot_date`, `total_equity_value`, `total_cash_value`, `total_portfolio_value`, `day_pnl`, `day_pnl_percent`.

### REST API Endpoints
- `GET /api/portfolio/summary/` — Retrieve aggregated portfolio metrics (Current Value, Total Invested, Overall P&L, Day P&L, Cash Balance).
- `GET /api/portfolio/holdings/` — List all active stock holdings with LTP, Current Value, and Unrealized P&L.
- `GET /api/portfolio/allocation/` — Retrieve asset allocation percentages by sector and stock.
- `GET /api/portfolio/history/?period=1M` — Fetch historical portfolio net-worth snapshots for equity curve charting.
- `GET /api/portfolio/admin/overview/` — Finance Officer: Platform aggregate Assets Under Management (AUM) and wealth distribution.

### UI Views & Components
- `PortfolioOverviewView.jsx`: Top summary cards (Total Wealth, Invested Value, Total P&L, Today's Gain/Loss with dynamic green/red badges).
- `HoldingsTable.jsx`: Rich table listing stocks with Avg Price, LTP, Current Value, P&L (₹ and %), and quick "Trade" shortcuts.
- `AssetAllocationChart.jsx`: Interactive Doughnut chart showing portfolio sector diversification.
- `EquityCurveChart.jsx`: Line chart visualizing portfolio performance over 1W, 1M, 6M, 1Y, and All-Time.

### Feature Checklist
- [ ] **Average Cost Accounting**: Update weighted-average purchase price upon incremental buy orders.
- [ ] **Realized P&L Computation**: Calculate realized profit/loss upon partial or full position sale.
- [ ] **Live Unrealized Valuation**: Dynamically recalculate holdings values based on latest market quotes.
- [ ] **Sector Allocation Aggregator**: Group holdings by security sector and return percentage share.
- [ ] **Performance Snapshot Job**: Daily/on-demand routine to capture portfolio equity curves.
- [ ] **Finance Officer AUM Console**: Aggregated view of platform-wide user holdings and systemic equity exposure.
- [ ] **Pytest Unit Tests**: Test average cost calculation on multiple buys, P&L on sell orders, and zero-holding deletion.

---

## Module 06: Risk Management (`P15-E07`)
*Sprint 2 | ~8 Hours | 8 Story Points | Priority: Must | Deliverable: D09*

### Scope & Business Purpose
Computes portfolio volatility, benchmark correlation (Beta), risk-adjusted return (Sharpe Ratio), potential downside (VaR 95%), and concentration warnings.

### Database Entities
- `risk_assessment`: `id`, `user_id` (FK -> `custom_user`), `portfolio_beta` (`DECIMAL(6, 3)`), `sharpe_ratio` (`DECIMAL(6, 3)`), `var_95_daily` (`DECIMAL(12, 2)`), `concentration_index` (`DECIMAL(6, 3)`), `risk_score` (`1` to `100`), `risk_category` (`CONSERVATIVE`, `MODERATE`, `AGGRESSIVE`, `HIGH_RISK`), `calculated_at`.
- `risk_alert_threshold`: `id`, `user_id` (FK -> `custom_user`), `max_drawdown_limit` (`DECIMAL(5, 2)`), `max_single_stock_pct` (`DECIMAL(5, 2)`), `is_active`.

### REST API Endpoints
- `GET /api/risk/metrics/` — Fetch authenticated customer portfolio risk scores, Beta, Sharpe, and VaR.
- `GET /api/risk/concentration/` — Analyze single-stock and sector concentration with threshold breach flags.
- `POST /api/risk/stress-test/` — Simulate portfolio performance under market shock scenarios (e.g. -5% market crash, interest rate hike).
- `GET /api/risk/admin/platform-exposure/` — Finance Officer: Systemic risk dashboard identifying over-leveraged or high-risk accounts.

### UI Views & Components
- `RiskDashboardView.jsx`: Visual Risk Gauge (0–100 scale), Beta meter, Sharpe ratio display, and 1-day VaR estimate.
- `ConcentrationWarningCard.jsx`: Visual warning indicators highlighting holdings exceeding 25% portfolio weight.
- `StressTestSimulator.jsx`: Interactive scenario simulator slider showing projected P&L impact under market drops.
- `FORiskMonitoringView.jsx`: Supervisory heat-map table ranking users by risk exposure and drawdown.

### Feature Checklist
- [ ] **Portfolio Beta Engine**: Compute weighted covariance of portfolio stocks against NIFTY 50 benchmark returns.
- [ ] **Sharpe Ratio Engine**: Calculate excess return over Indian Sovereign Risk-Free Rate (6.5%) divided by portfolio volatility.
- [ ] **Value at Risk (VaR 95%)**: Calculate parametric 1-day maximum expected loss at 95% confidence level.
- [ ] **Concentration Breaches**: Flag individual stock allocations exceeding 25% of total portfolio value.
- [ ] **Interactive Stress Testing**: Calculate projected monetary impact of predefined index shock scenarios.
- [ ] **Finance Officer Exposure Heatmap**: Filter users with risk scores > 80 or high single-asset concentration.
- [ ] **Pytest Unit Tests**: Validate mathematical accuracy of Beta, Sharpe, and VaR calculations against reference test matrices.

---

## Module 07: Technical Analysis (`P15-E08`)
*Sprint 2 | ~8 Hours | 8 Story Points | Priority: Should | Deliverable: D10*

### Scope & Business Purpose
Generates interactive price charts, momentum oscillators (RSI), trend indicators (MACD, SMA, EMA), and automated technical consensus signals.

### Database Entities
- `technical_indicator`: `id`, `security_id` (FK -> `security`), `calculation_date`, `rsi_14` (`DECIMAL(6, 2)`), `macd_line` (`DECIMAL(8, 3)`), `macd_signal` (`DECIMAL(8, 3)`), `macd_hist` (`DECIMAL(8, 3)`), `sma_20` (`DECIMAL(12, 2)`), `sma_50` (`DECIMAL(12, 2)`), `sma_200` (`DECIMAL(12, 2)`), `ema_20` (`DECIMAL(12, 2)`), `overall_signal` (`STRONG_BUY`, `BUY`, `NEUTRAL`, `SELL`, `STRONG_SELL`).
- `user_chart_preference`: `id`, `user_id` (FK -> `custom_user`), `default_indicators` (`JSONB`), `chart_type` (`CANDLESTICK`, `LINE`, `AREA`).

### REST API Endpoints
- `GET /api/analysis/technical/<symbol>/` — Retrieve all calculated technical indicators and consensus signal for a stock.
- `GET /api/analysis/technical/screener/` — Screen stocks by technical filters (e.g. RSI < 30 Oversold, Golden Cross SMA 50 > 200).
- `GET /api/analysis/technical/admin/audit/` — Finance Officer: Review technical indicator feed consistency.

### UI Views & Components
- `TechnicalChartView.jsx`: High-performance Candlestick chart with volume sub-pane and time range selectors (1D, 1W, 1M, 1Y).
- `IndicatorOverlayControls.jsx`: Toggles for SMA (20/50/200), EMA, and Bollinger Bands.
- `RsiMacdPane.jsx`: Dual oscillator pane rendering RSI (with 30/70 thresholds) and MACD histogram.
- `SignalSummaryBadge.jsx`: Visual consensus badge (e.g. "Bullish - 7 Buy, 2 Neutral, 1 Sell").

### Feature Checklist
- [ ] **RSI 14-Period Formula**: Compute Relative Strength Index based on average gains vs average losses over 14 bars.
- [ ] **MACD (12, 26, 9) Engine**: Calculate 12-day EMA, 26-day EMA, MACD line, 9-day signal line, and divergence histogram.
- [ ] **Moving Averages (SMA & EMA)**: Compute 20-day, 50-day, and 200-day rolling averages over historical closing prices.
- [ ] **Consensus Signal Logic**: Combine indicator thresholds to produce a composite trading bias (`Buy`, `Sell`, `Neutral`).
- [ ] **Technical Stock Screener**: Filter stocks hitting oversold (RSI < 30) or breakout conditions.
- [ ] **Finance Officer Audit**: Supervise algorithm outputs and historical price data feeds.
- [ ] **Pytest Unit Tests**: Test RSI on known price series, MACD convergence/divergence points, and boundary conditions.

---

## Module 08: Fundamental Analysis (`P15-E09`)
*Sprint 3 | ~8 Hours | 8 Story Points | Priority: Should | Deliverable: D11*

### Scope & Business Purpose
Provides corporate valuation metrics (P/E, P/B, EPS, ROE, D/E, Dividend Yield), peer comparison tables, and corporate financial health grading.

### Database Entities
- `fundamental_data`: `id`, `security_id` (FK -> `security`, UNIQUE), `market_cap` (`DECIMAL(20, 2)`), `pe_ratio` (`DECIMAL(8, 2)`), `pb_ratio` (`DECIMAL(8, 2)`), `eps` (`DECIMAL(8, 2)`), `dividend_yield` (`DECIMAL(5, 2)`), `debt_to_equity` (`DECIMAL(6, 2)`), `roe` (`DECIMAL(6, 2)`), `book_value` (`DECIMAL(12, 2)`), `financial_year`, `updated_at`.
- `company_financial`: `id`, `security_id` (FK -> `security`), `period_name` (e.g., `FY 2024-25`), `revenue` (`DECIMAL(18, 2)`), `net_profit` (`DECIMAL(18, 2)`), `operating_margin` (`DECIMAL(5, 2)`), `ebitda` (`DECIMAL(18, 2)`).

### REST API Endpoints
- `GET /api/analysis/fundamental/<symbol>/` — Retrieve fundamental financial ratios, health grade, and financial statement history.
- `GET /api/analysis/fundamental/peers/<symbol>/` — Retrieve comparative peer valuation metrics within the same industry sector.
- `GET /api/analysis/fundamental/screener/` — Screen stocks by fundamental filters (e.g. P/E < 20 and ROE > 15%).
- `POST /api/analysis/fundamental/admin/update/` — Finance Officer: Update or audit corporate financial statements.

### UI Views & Components
- `FundamentalOverviewView.jsx`: Key metrics cards (P/E Ratio, P/B Ratio, EPS, Dividend Yield, Debt/Equity, ROE).
- `FinancialHealthScoreCard.jsx`: Composite health score (1 to 10 scale) based on profitability and balance sheet strength.
- `PeerComparisonTable.jsx`: Side-by-side comparison table of sector competitors.
- `FinancialStatementsChart.jsx`: Bar chart visualizing multi-year Revenue and Net Profit growth trends.

### Feature Checklist
- [ ] **Valuation Metrics Display**: Present key fundamental metrics with clear definitions and sector benchmark comparisons.
- [ ] **Peer Comparison Matrix**: Automatically query equities within the same sector and rank by valuation metrics.
- [ ] **Fundamental Health Algorithm**: Rule-based scoring evaluating debt safety, profitability, and reasonable valuation.
- [ ] **Multi-Year Financials**: Display historical revenue and profit trends in tabular and visual chart forms.
- [ ] **Fundamental Stock Screener**: Allow users to filter equities based on customizable financial ratio ranges.
- [ ] **Finance Officer Fundamental Editor**: Enable back-office verification and manual correction of financial statement inputs.
- [ ] **Pytest Unit Tests**: Test edge-case handling for negative earnings (negative P/E), zero-debt companies, and peer grouping queries.

---

## Module 09: Notification and Alerts (`P15-E10`)
*Sprint 3 | ~8 Hours | 8 Story Points | Priority: Should | Deliverable: D12*

### Scope & Business Purpose
Manages user-defined stock price alerts, trade execution notifications, account alerts, and platform-wide administrative announcements.

### Database Entities
- `price_alert`: `id`, `user_id` (FK -> `custom_user`), `security_id` (FK -> `security`), `condition` (`ABOVE`, `BELOW`, `PCT_CHANGE`), `target_value` (`DECIMAL(12, 2)`), `is_triggered` (`BOOLEAN`), `triggered_at`, `is_active` (`BOOLEAN`), `created_at`.
- `user_notification`: `id`, `user_id` (FK -> `custom_user`), `title`, `message`, `category` (`TRADE`, `PRICE_ALERT`, `ACCOUNT`, `SYSTEM`), `is_read` (`BOOLEAN`), `link_url`, `created_at`.
- `system_announcement`: `id`, `created_by` (FK -> `custom_user`), `title`, `body`, `priority` (`NORMAL`, `URGENT`), `valid_until`, `created_at`.

### REST API Endpoints
- `GET /api/notifications/` — Retrieve user notifications with unread count.
- `PATCH /api/notifications/<id>/read/` — Mark a specific notification as read.
- `POST /api/notifications/read-all/` — Mark all user notifications as read.
- `GET /api/notifications/alerts/` — List user's active and triggered price alerts.
- `POST /api/notifications/alerts/` — Create a new price alert trigger.
- `DELETE /api/notifications/alerts/<id>/` — Delete or deactivate a price alert.
- `POST /api/notifications/admin/broadcast/` — Finance Officer: Create and broadcast a system-wide announcement to all users.

### UI Views & Components
- `NotificationBellDropdown.jsx`: Navigation bar bell icon with real-time unread counter badge and scrollable preview list.
- `NotificationCenterView.jsx`: Full-page notification log with category filters (Trade, Alerts, System) and "Clear All" action.
- `PriceAlertModal.jsx`: Modal to set price threshold triggers with visual current price benchmark.
- `FOBroadcastConsole.jsx`: Finance Officer announcement composer with priority tagging.

### Feature Checklist
- [ ] **Price Alert Evaluation Worker**: Periodic routine matching current LTP against active `ABOVE` / `BELOW` conditions.
- [ ] **Trade Execution Trigger**: Automated event listener triggering notifications upon order execution or cancellation.
- [ ] **Unread Notification Badge**: Real-time reactive badge counter in the frontend navbar.
- [ ] **Mark as Read Workflow**: Individual item and bulk mark-as-read API actions.
- [ ] **System Broadcast Engine**: Finance Officer capability to send urgent platform messages to all active customers.
- [ ] **Alert Deactivation**: Automatically mark triggered one-shot alerts as `is_triggered = True` to prevent duplicate alerts.
- [ ] **Pytest Unit Tests**: Test threshold trigger math, duplicate alert prevention, and broadcast delivery logic.

---

## Module 10: Customer Support (`P15-E11`)
*Sprint 3 | ~8 Hours | 8 Story Points | Priority: Should | Deliverable: D13*

### Scope & Business Purpose
Provides a full-cycle support ticketing helpdesk for trading disputes, KYC/deposit issues, and inquiry management between Customers and Finance Officers.

### Database Entities
- `support_ticket`: `id`, `ticket_number` (UNIQUE, e.g. `TICK-8042`), `user_id` (FK -> `custom_user`), `category` (`TRADE_DISPUTE`, `DEPOSIT_WITHDRAWAL`, `KYC_ACCOUNT`, `TECHNICAL`, `GENERAL`), `priority` (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), `status` (`OPEN`, `IN_PROGRESS`, `PENDING_CUSTOMER`, `RESOLVED`, `CLOSED`), `subject`, `related_order_id` (FK -> `trade_order`, nullable), `assigned_to` (FK -> `custom_user`, nullable), `created_at`, `updated_at`, `resolved_at`.
- `ticket_message`: `id`, `ticket_id` (FK -> `support_ticket`), `sender_id` (FK -> `custom_user`), `message_text`, `is_internal_note` (`BOOLEAN`), `created_at`.

### REST API Endpoints
- `GET /api/support/tickets/` — Customer: List own support tickets. Finance Officer: List all platform tickets.
- `POST /api/support/tickets/` — Customer: Open a new support ticket.
- `GET /api/support/tickets/<id>/` — Retrieve ticket details and chronological message thread.
- `POST /api/support/tickets/<id>/reply/` — Append a reply message to the ticket conversation.
- `PATCH /api/support/tickets/<id>/status/` — Update ticket status (e.g. `IN_PROGRESS`, `RESOLVED`, `CLOSED`).
- `PATCH /api/support/admin/tickets/<id>/assign/` — Finance Officer: Assign ticket to self or teammate.

### UI Views & Components
- `CustomerSupportView.jsx`: Customer ticket overview with status filter pills and "Create New Ticket" button.
- `NewTicketModal.jsx`: Ticket creation modal with category, priority, optional order ID linking, and problem description.
- `TicketConversationView.jsx`: Chat-style chronological messaging interface with sender badges (Customer vs Support).
- `FOHelpdeskDashboardView.jsx`: Finance Officer ticketing triage grid with priority indicators, SLA timers, and bulk assignment.

### Feature Checklist
- [ ] **Ticket Generation Engine**: Create unique ticket number (`TICK-xxxx`) and link optional trade orders.
- [ ] **Chronological Message Threading**: Support back-and-forth communication between Customer and Support staff.
- [ ] **Role-Based Ticket Isolation**: Ensure Customers can strictly access only their own tickets.
- [ ] **Finance Officer Triage Console**: Comprehensive queue with status, category, and priority filtering.
- [ ] **Status Transition Workflow**: Enforce proper ticket lifecycle states (`OPEN` -> `IN_PROGRESS` -> `RESOLVED` -> `CLOSED`).
- [ ] **Internal Staff Notes**: Enable Finance Officers to append internal notes hidden from the customer view.
- [ ] **Pytest Unit Tests**: Test unauthorized ticket access prevention, message append integrity, and status transitions.

---

## Module 11: Testing, Documentation and Release (`P15-E12`)
*Sprint 3 | ~6 Hours | 7 Story Points | Priority: Must | Tag: v1.0.0 | Deliverables: D14, D15, D16, D17*

### Checklist
- [ ] **End-to-End QA Testing (`P15-US35`)**: Execute complete integration test suite across all 10 modules covering customer journey and back-office audit.
- [ ] **Test Report & Defect Log (`D14`)**: Generate structured report in `docs/test-report/` detailing test cases, execution status, and resolved defects.
- [ ] **OpenAPI / Swagger Generation (`P15-US36`)**: Configure `drf-spectacular` to automatically expose interactive Swagger UI at `/api/docs/` and Redoc at `/api/redoc/`.
- [ ] **README & Setup Guide (`D15`)**: Complete root `README.md` with installation commands, environment configuration, database seeding guide, and UI screenshots.
- [ ] **Postman Collection Export**: Export standardized Postman collection with environment variables into `docs/api/`.
- [ ] **Demo Presentation Deck (`D16`)**: Create 10-slide academic project presentation deck in `docs/presentation/`.
- [ ] **Production Deployment Preparation**: Verify Render backend deployment build scripts and Netlify SPA redirect rules (`_redirects`).
- [ ] **Final Tagged Release v1.0.0 (`P15-US37`, `D17`)**: Merge `develop` into `main`, verify all tests pass on clean checkout, generate and push Git tag `v1.0.0` with release notes.
