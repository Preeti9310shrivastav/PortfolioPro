# PortfolioPro — Master User Stories Register

This document preserves every User Story specified in the official HCLTech curriculum workbook (`guide2HCL.pdf`). All IDs, roles, priorities, story points, sprints, and acceptance criteria are faithfully documented with zero alterations, marked with an implementation status of **Pending**.

## Summary Statistics

- **Total Epics**: 12 (`P15-E01` to `P15-E12`)
- **Total User Stories**: 37 (`P15-US01` to `P15-US37`)
- **Total Story Points**: 97 Points (Fibonacci scale: 2, 3)
- **Sprint Distribution**:
  - **Sprint 0**: 4 stories | 10 story points
  - **Sprint 1**: 12 stories | 32 story points
  - **Sprint 2**: 9 stories | 24 story points
  - **Sprint 3**: 12 stories | 31 story points
- **Priority Breakdown**:
  - **Must Have**: 25 stories (69 story points)
  - **Should Have**: 12 stories (28 story points)

---

## Sprint 0: Foundation, Architecture & Design (6 Hours | 10 Points)

### Epic P15-E01: Project Setup, Git Workflow and Design (Priority: Must)

#### [P15-US01] Git Repository and Branching Setup
- **Epic**: `P15-E01`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 0
- **Target Branch**: `feature/P15-US01-repo-setup`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to create the Git repository with README, .gitignore, develop branch and the agreed folder layout so that the team can collaborate safely from day one.
- **Acceptance Criteria**:
  1. Repository exists on GitHub (`mca2-fsdpython-portfoliopro`).
  2. Both `main` and `develop` branches are created and present.
  3. Trainer / collaborators are added to the repository.
  4. `.gitignore` properly covers `venv/`, `__pycache__/`, `*.pyc`, `.env`, `node_modules/`, `dist/`, and local databases.

---

#### [P15-US02] Relational Schema Design & DDL Scripts
- **Epic**: `P15-E01`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 0
- **Target Branch**: `feature/P15-US02-database-design`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to design the ER diagram and create the database scripts for MySQL 8.0 [Supabase PostgreSQL] so that all modules share a consistent, normalized design.
- **Acceptance Criteria**:
  1. ER diagram or comprehensive data model committed under `database/` or `docs/`.
  2. 3NF normalized schema script (`database/schema.sql`) runs without errors on a clean Supabase PostgreSQL database.
  3. Master and transaction seed data script (`database/seed_data.sql`) populated with realistic Indian context data (dates 2024–2026, INR amounts).

---

#### [P15-US03] UI Wireframes & User Experience Flow
- **Epic**: `P15-E01`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 0
- **Target Branch**: `feature/P15-US03-wireframes-design`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to review wireframes of the main screens so that the team agrees on the user flow before coding.
- **Acceptance Criteria**:
  1. Wireframes for login, trading dashboard, and the primary initial module are created and committed under `docs/wireframes/`.
  2. User journey and interaction flows are documented and approved by the trainer.

---

#### [P15-US04] Project Skeleton & Role-Based Navigation
- **Epic**: `P15-E01`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 0
- **Target Branch**: `feature/P15-US04-project-skeleton`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to set up the project skeleton with login and role-based navigation so that later modules can be built on a working base.
- **Acceptance Criteria**:
  1. Backend runs successfully with `python manage.py runserver`.
  2. Frontend runs successfully with `npm run dev`.
  3. Working login flow verifies credentials and renders role-based navigation for two distinct roles (`Customer` and `Finance Officer`).
  4. Git tag `v0.1.0` is created and pushed.

---

## Sprint 1: Core Transactional Engine (28 Hours | 32 Points)

### Epic P15-E02: User Authentication (Priority: Must)

#### [P15-US05] Customer Authentication Operations
- **Epic**: `P15-E02`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US05-customer-auth-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for user Authentication so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Create (Register), Read (Profile), Update (Edit Profile), and Search operations work seamlessly from the UI.
  2. Mandatory-field, email syntax, phone format, and password complexity validations displayed on UI.
  3. User authentication records safely persisted in PostgreSQL.

---

#### [P15-US06] Finance Officer Authentication Audit & Tracking
- **Epic**: `P15-E02`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US06-fo-auth-tracking`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track user Authentication information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views of platform users available with search, status filters (active, inactive), and role badges.
  2. Access restricted by role (`Finance Officer` / `Admin` only).
  3. Displayed data matches underlying database state accurately.

---

#### [P15-US07] Authentication REST APIs & Automated Unit Tests
- **Epic**: `P15-E02`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US07-auth-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for user Authentication so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Authentication endpoints (`/api/auth/register/`, `/api/auth/login/`, `/api/auth/profile/`, `/api/auth/token/refresh/`) fully documented.
  2. Input validation and standard error response formatting implemented.
  3. Pytest with `pytest-django` unit tests pass with zero failures.
  4. Pull request approved and merged to `develop`.

---

### Epic P15-E03: Account Management (Priority: Must)

#### [P15-US08] Customer Account & Balance Management UI
- **Epic**: `P15-E03`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US08-customer-account-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for account Management so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can view trading account balance, add funds (deposit), request withdrawal, and search transaction records from UI.
  2. Validation enforces non-negative inputs and prevents withdrawal of funds exceeding available balance.
  3. Account records and financial transactions safely persisted in PostgreSQL.

---

#### [P15-US09] Finance Officer Account Monitoring & Verification
- **Epic**: `P15-E03`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US09-fo-account-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track account Management information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available to track customer trading accounts, KYC statuses, and ledger transactions.
  2. Status filters (KYC verified, pending, rejected; deposits approved/pending) available.
  3. Access strictly restricted by role. Data strictly synchronized with database.

---

#### [P15-US10] Account Management APIs & Test Suite
- **Epic**: `P15-E03`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US10-account-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for account Management so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Account management API endpoints (`/api/accounts/`, `/api/accounts/transactions/`, `/api/accounts/kyc/`) documented.
  2. Comprehensive validations and exception handling for financial ledger entries.
  3. Pytest automated test cases written and passing.
  4. Pull request reviewed and approved.

---

### Epic P15-E04: Market Data (Priority: Must)

#### [P15-US11] Customer Market Data & Watchlist Interface
- **Epic**: `P15-E04`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US11-customer-market-data`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for market Data so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can search listed equities by ticker symbol or company name, view live quotes (LTP, OHLC, volume), and manage watchlists.
  2. Format and mandatory field validations shown on search/filter controls.
  3. Market data changes and user watchlists persisted in PostgreSQL.

---

#### [P15-US12] Finance Officer Market Data Oversight
- **Epic**: `P15-E04`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US12-fo-market-data-oversight`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track market Data information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available for all securities, sector groupings, and daily price feeds.
  2. Filters available by exchange (NSE/BSE), sector, market cap, and trading status.
  3. Data strictly matches database records.

---

#### [P15-US13] Market Data REST APIs & Test Suite
- **Epic**: `P15-E04`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US13-market-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for market Data so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Market data endpoints (`/api/market/stocks/`, `/api/market/quotes/<symbol>/`, `/api/market/history/<symbol>/`) documented.
  2. Input validation, ticker symbol sanitization, and error handling for missing quotes.
  3. Pytest with pytest-django tests pass.
  4. Pull request approved.

---

### Epic P15-E05: Trading Engine (Priority: Must)

#### [P15-US14] Customer Order Placement & Execution UI
- **Epic**: `P15-E05`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US14-customer-trading-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for trading Engine so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can place BUY/SELL orders (Market/Limit), view order book, cancel pending orders, and search historical trades from UI.
  2. Validation checks: quantity > 0, price > 0, sufficient cash balance for buy orders, sufficient holdings for sell orders.
  3. Trade executions and order states persisted in PostgreSQL.

---

#### [P15-US15] Finance Officer Trade Audit & Transaction Monitor
- **Epic**: `P15-E05`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US15-fo-trading-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track trading Engine information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. Complete platform order book and execution audit trail available.
  2. Filters by date range, customer ID, ticker symbol, transaction type (Buy/Sell), and execution status (`FILLED`, `REJECTED`, `CANCELLED`).
  3. Data matches database state accurately.

---

#### [P15-US16] Trading Engine Atomic APIs & Execution Engine Tests
- **Epic**: `P15-E05`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 1
- **Target Branch**: `feature/P15-US16-trading-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for trading Engine so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Trading APIs (`/api/trading/orders/`, `/api/trading/orders/<id>/cancel/`, `/api/trading/executions/`) documented.
  2. Atomic trade execution logic wrapped in `@transaction.atomic` with balance locks and rollback guarantees.
  3. Pytest test suite validates order placement, balance deduction, holding updates, and edge cases.
  4. Pull request approved.

---

## Sprint 2: Portfolio & Risk Analytics (28 Hours | 24 Points)

### Epic P15-E06: Portfolio Management (Priority: Must)

#### [P15-US17] Customer Portfolio Holdings & P&L UI
- **Epic**: `P15-E06`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US17-customer-portfolio-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for portfolio Management so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can view all active equity positions, unrealized P&L, realized P&L, asset allocation, and search holdings.
  2. P&L figures update dynamically based on latest market prices.
  3. Portfolio holdings and valuation snapshots persisted in PostgreSQL.

---

#### [P15-US18] Finance Officer Portfolio Audit & Wealth Tracking
- **Epic**: `P15-E06`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US18-fo-portfolio-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track portfolio Management information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available for customer portfolios, aggregate platform equity under management (AUM), and sector exposures.
  2. Status and value filters available; access restricted by role.
  3. Data matches database accurately.

---

#### [P15-US19] Portfolio Management REST APIs & Tests
- **Epic**: `P15-E06`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US19-portfolio-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for portfolio Management so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Portfolio endpoints (`/api/portfolio/holdings/`, `/api/portfolio/summary/`, `/api/portfolio/history/`) documented.
  2. Validation and calculation tests for FIFO/average cost accounting and P&L formulas.
  3. Pytest with pytest-django tests pass.
  4. Pull request approved.

---

### Epic P15-E07: Risk Management (Priority: Must)

#### [P15-US20] Customer Risk Assessment & Concentration UI
- **Epic**: `P15-E07`
- **Role**: Customer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US20-customer-risk-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for risk Management so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can view risk metrics (Portfolio Beta, Sharpe Ratio, Value at Risk / VaR, and Sector Concentration warning flags).
  2. Interactive risk gauge and threshold indicators shown on UI.
  3. Risk parameters and calculation snapshots persisted in PostgreSQL.

---

#### [P15-US21] Finance Officer Risk Oversight Dashboard
- **Epic**: `P15-E07`
- **Role**: Finance Officer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US21-fo-risk-dashboard`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track risk Management information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. Dashboard displaying accounts with high risk scores, concentration breaches (>25% single stock), or extreme drawdown.
  2. Filter by risk tier (Low, Moderate, High, Severe); access restricted by role.
  3. Data matches database records.

---

#### [P15-US22] Risk Management Computation Engine & Tests
- **Epic**: `P15-E07`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US22-risk-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for risk Management so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Risk API endpoints (`/api/risk/metrics/`, `/api/risk/concentration/`, `/api/risk/stress-test/`) documented.
  2. Mathematical verification of Beta, Sharpe Ratio, and parametric VaR (95% confidence).
  3. Pytest automated tests pass.
  4. Pull request approved.

---

### Epic P15-E08: Technical Analysis (Priority: Should)

#### [P15-US23] Customer Technical Indicators & Charting UI
- **Epic**: `P15-E08`
- **Role**: Customer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US23-customer-technical-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for technical Analysis so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can view candlestick charts with overlay indicators (SMA 20/50, EMA 20) and oscillator sub-charts (RSI 14, MACD).
  2. Indicator parameters customizable; technical summary badge (`Buy`/`Neutral`/`Sell`) displayed.
  3. Custom indicator preferences and chart notes persisted in PostgreSQL.

---

#### [P15-US24] Finance Officer Technical Analysis Audit
- **Epic**: `P15-E08`
- **Role**: Finance Officer
- **Priority**: Should
- **Story Points**: 2
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US24-fo-technical-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track technical Analysis information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. Filter and view market technical indicators across tracked equities; audit technical signals.
  2. Data matches database records.

---

#### [P15-US25] Technical Analysis Algorithms & Test Suite
- **Epic**: `P15-E08`
- **Role**: Developer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 2
- **Target Branch**: `feature/P15-US25-technical-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for technical Analysis so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Technical endpoints (`/api/analysis/technical/<symbol>/`, `/api/analysis/indicators/`) documented.
  2. Mathematical validation of RSI, MACD, and SMA formulas with edge tests (zero volume, short history).
  3. Pytest unit tests pass.
  4. Pull request approved.

---

## Sprint 3: Advanced Insights, Support & Final Release (28 Hours | 31 Points)

### Epic P15-E09: Fundamental Analysis (Priority: Should)

#### [P15-US26] Customer Fundamental Valuation & Ratios UI
- **Epic**: `P15-E09`
- **Role**: Customer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US26-customer-fundamental-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for fundamental Analysis so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can inspect stock fundamental valuation metrics (P/E, P/B, EPS, Dividend Yield, Debt-to-Equity, ROE) and peer comparison tables.
  2. Search and filter stocks by fundamental criteria (e.g. Low P/E, High Dividend).
  3. Fundamental data records persisted in PostgreSQL.

---

#### [P15-US27] Finance Officer Fundamental Data Audit & Verification
- **Epic**: `P15-E09`
- **Role**: Finance Officer
- **Priority**: Should
- **Story Points**: 2
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US27-fo-fundamental-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track fundamental Analysis information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available for corporate financial statements, earnings reports, and financial ratios.
  2. Filter by sector, market cap tier, and profitability status.
  3. Data matches database records.

---

#### [P15-US28] Fundamental Analysis APIs & Unit Tests
- **Epic**: `P15-E09`
- **Role**: Developer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US28-fundamental-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for fundamental Analysis so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Fundamental endpoints (`/api/analysis/fundamental/<symbol>/`, `/api/analysis/screener/`) documented.
  2. Validations handle division-by-zero (e.g., zero earnings for P/E) safely.
  3. Pytest with pytest-django tests pass.
  4. Pull request approved.

---

### Epic P15-E10: Notification and Alerts (Priority: Should)

#### [P15-US29] Customer Alerts Management & Notification Feed UI
- **Epic**: `P15-E10`
- **Role**: Customer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US29-customer-alerts-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for notification and Alerts so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can set target price alerts (Condition: Above/Below price threshold), view active alerts, and receive execution notifications in notification bell.
  2. Mandatory field validations shown for target prices and conditions.
  3. Alerts and notifications persisted in PostgreSQL.

---

#### [P15-US30] Finance Officer System Notification Monitoring
- **Epic**: `P15-E10`
- **Role**: Finance Officer
- **Priority**: Should
- **Story Points**: 2
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US30-fo-notification-audit`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track notification and Alerts information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available for platform notifications, broadcast messages, and trigger history.
  2. Filters available by notification category (Trade, System, Price Alert); access limited by role.
  3. Data matches database state.

---

#### [P15-US31] Notification Engine REST APIs & Alert Trigger Tests
- **Epic**: `P15-E10`
- **Role**: Developer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US31-notification-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for notification and Alerts so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Notification APIs (`/api/notifications/`, `/api/notifications/alerts/`, `/api/notifications/<id>/read/`) documented.
  2. Background evaluation routine evaluates price thresholds against active triggers.
  3. Pytest tests verify trigger conditions, unread counter updates, and dismissals.
  4. Pull request approved.

---

### Epic P15-E11: Customer Support (Priority: Should)

#### [P15-US32] Customer Support Helpdesk & Ticket Management UI
- **Epic**: `P15-E11`
- **Role**: Customer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US32-customer-support-ui`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Customer, I want to add, view, update and search records for customer Support so that the work can be done digitally and accurately.
- **Acceptance Criteria**:
  1. Customer can open support tickets (category, priority, subject, message), view ticket status (`OPEN`, `RESOLVED`), and append replies.
  2. Mandatory field validations shown on ticket submission.
  3. Tickets and conversation messages persisted in PostgreSQL.

---

#### [P15-US33] Finance Officer Helpdesk Resolution Dashboard
- **Epic**: `P15-E11`
- **Role**: Finance Officer
- **Priority**: Should
- **Story Points**: 2
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US33-fo-support-resolution`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Finance Officer, I want to view, filter and track customer Support information so that I can take timely decisions.
- **Acceptance Criteria**:
  1. List and detail views available for all customer tickets with category and priority filters.
  2. Finance Officer can assign, reply to, update status, and close customer tickets.
  3. Access limited by role; data matches database records.

---

#### [P15-US34] Customer Support REST APIs & Workflow Tests
- **Epic**: `P15-E11`
- **Role**: Developer
- **Priority**: Should
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US34-support-apis-tests`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to build REST APIs, validations and tests for customer Support so that the module is reliable and reusable.
- **Acceptance Criteria**:
  1. Support endpoints (`/api/support/tickets/`, `/api/support/tickets/<id>/messages/`, `/api/support/tickets/<id>/status/`) documented.
  2. Validation enforces ticket status state transitions and prevents unauthorized access to customer tickets.
  3. Pytest automated tests pass.
  4. Pull request approved.

---

### Epic P15-E12: Testing, Documentation and Release (Priority: Must)

#### [P15-US35] End-to-End QA Testing & Defect Report
- **Epic**: `P15-E12`
- **Role**: QA Reviewer
- **Priority**: Must
- **Story Points**: 3
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US35-qa-test-report`
- **Status**: `[PENDING]`
- **User Story**:
  > As a QA Reviewer, I want to run end-to-end test cases across all modules so that defects are found before the demo.
- **Acceptance Criteria**:
  1. End-to-end test cases spanning all 10 modules executed and documented in `docs/test-report`.
  2. All critical and high-priority defects resolved or logged with mitigation notes.

---

#### [P15-US36] Technical Documentation & OpenAPI Specification
- **Epic**: `P15-E12`
- **Role**: Developer
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US36-api-documentation`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Developer, I want to complete the README, API documentation and user guide so that anyone can set up and use the application.
- **Acceptance Criteria**:
  1. `README.md` contains comprehensive setup instructions, prerequisites, running commands, and UI screenshots.
  2. OpenAPI 3.0 / Swagger schema generated via `drf-spectacular` and Postman collection exported to `docs/api/`.

---

#### [P15-US37] Live Demo Presentation & v1.0.0 Release Tagging
- **Epic**: `P15-E12`
- **Role**: Team
- **Priority**: Must
- **Story Points**: 2
- **Sprint**: Sprint 3
- **Target Branch**: `feature/P15-US37-release-v1`
- **Status**: `[PENDING]`
- **User Story**:
  > As a Team, I want to present a live demo and merge develop to main with the v1.0.0 tag so that the project is formally released.
- **Acceptance Criteria**:
  1. Live demonstration successfully presented to the trainer.
  2. Final pull request from `develop` into `main` reviewed and approved.
  3. Release tag `v1.0.0` pushed with complete release notes.
