# PortfolioPro — Technology Stack & Architectural Decision Record (ADR)

## 1. Technology Ecosystem Overview

PortfolioPro is architected as a modern, decoupled, cloud-ready full-stack web application. The platform adheres strictly to modern software engineering best practices while maintaining full compliance with the MCA 2nd Year capstone curriculum (P15 / HCLTech FSD Python Track).

```mermaid
graph LR
    subgraph Client Tier ["Client Tier (Netlify CDN)"]
        ReactApp["React 18 + Vite SPA"]
        BS5["Bootstrap 5 + Icons"]
        Charts["Financial Charting (Chart.js / Recharts)"]
    end

    subgraph API Tier ["Backend API Tier (Render Cloud)"]
        Gunicorn["Gunicorn / WSGI Gateway"]
        DjangoApp["Django 5.x + DRF Core Engine"]
        JWT["SimpleJWT Authentication"]
        Swagger["OpenAPI 3.0 / drf-spectacular"]
    end

    subgraph Data Tier ["Managed Data Tier (Supabase)"]
        Postgres["Supabase PostgreSQL 15+"]
        Pooler["Connection Pooling (Supavisor / PgBouncer)"]
        SSL["SSL/TLS Encrypted Storage"]
    end

    ReactApp -->|REST API over HTTPS| Gunicorn
    Gunicorn --> DjangoApp
    DjangoApp --> JWT
    DjangoApp --> Swagger
    DjangoApp -->|psycopg / SSL connection| Pooler
    Pooler --> Postgres
```

---

## 2. Core Architectural Decision: Migration from MySQL 8.0 to Supabase PostgreSQL

### 2.1 Context & Original Curriculum Specification
In the original academic curriculum documents (`guide_portfolioHCL.pdf` Table 4 and `guide2HCL.pdf` Table 3), the database was specified as:
> *"MySQL 8.0 Community Server with MySQL Workbench (and mysqlclient or PyMySQL driver)"*

### 2.2 Decision & Justification
As directed by the project sponsor and modern cloud architecture standards, the database engine is transitioned to **Supabase PostgreSQL**.

| Evaluation Dimension | Legacy Academic Spec (MySQL 8.0 Local) | Adopted Architecture (Supabase PostgreSQL) | Rationale for Change |
| :--- | :--- | :--- | :--- |
| **Hosting & Cloud Portability** | Requires running local daemon; difficult to expose securely to cloud backends. | Managed cloud PostgreSQL instance with public endpoints and SSL certificates. | Essential for 24/7 cloud availability and zero-configuration pairing with Render backend. |
| **Connection Management** | Standard MySQL connection thread per client; prone to socket exhaustion on serverless/cloud. | Built-in Supavisor / PgBouncer connection pooling on port 6543 (transaction mode). | Ensures resilient connection handling during concurrent cloud operations on Render. |
| **Financial Data Types** | `DECIMAL(18, 4)` | `DECIMAL(18, 4)` / `NUMERIC` | Complete mathematical precision parity for Indian Rupee (`₹`) monetary accounting. |
| **Semi-Structured Data** | `JSON` type | Native `JSONB` with GIN indexing | High performance storage for technical indicator caches, user chart preferences, and audit logs. |
| **Deployment Synergy** | Incompatible with serverless cloud tiers without external DB hosting. | Seamless integration with Netlify frontend and Render backend deployments. | Production parity between local development and live cloud demonstration. |

### 2.3 Dialect & DDL Differences Handled
The schema design script (`database/schema.sql`) and Django ORM models have been adapted from MySQL syntax to PostgreSQL standards:
- **Auto-Increment**: MySQL `INT AUTO_INCREMENT` is mapped to PostgreSQL `BIGSERIAL` / `SERIAL` (or Django standard auto-incrementing `BigAutoField`).
- **Data Types**: MySQL `DATETIME` is mapped to PostgreSQL `TIMESTAMPTZ` (Timezone-Aware Timestamps) for accurate financial transaction recording across Indian Standard Time (IST / UTC+05:30).
- **Boolean Handling**: MySQL `TINYINT(1)` is mapped to native PostgreSQL `BOOLEAN` (`TRUE` / `FALSE`).
- **Text & JSON**: MySQL `JSON` is mapped to PostgreSQL `JSONB` for binary indexing.

---

## 3. Technology Stack Breakdown

### 3.1 Frontend Tier (Client Application)
- **Framework / Runtime**: **React 18.x** with ECMAScript 2022+ features.
- **Build Tooling**: **Vite 5.x** — Ultra-fast Hot Module Replacement (HMR) and optimized Rollup-based production bundling.
- **UI Styling Framework**: **Bootstrap 5.3** — Responsive CSS grid, utility classes, financial dashboard components, modals, and tooltips.
- **Iconography**: **Bootstrap Icons** / **Lucide-React** — High clarity iconography for trading actions, gain/loss indicators, and status badges.
- **Routing**: **React Router v6** — Client-side declarative routing with nested routes, role-based Protected Route wrappers, and browser history management.
- **HTTP Client**: **Axios** — Configured with interceptors for automatic JWT Bearer token attachment, 401 token refresh retry loops, and unified error handling.
- **Financial Visualization**: **Chart.js** (via `react-chartjs-2`) or **Recharts** — Responsive Candlestick, Line, and Doughnut charts for technical analysis, sector asset allocation, and net-worth equity curves.
- **Currency & Date Formatting**: Native browser `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })` and `date-fns` for IST timestamp displays.

### 3.2 Backend Tier (API Engine & Business Logic)
- **Programming Language**: **Python 3.11 / 3.13** — Utilizing modern type annotations, `dataclasses`, and `Decimal` arithmetic.
- **Web Framework**: **Django 5.x / 4.2 LTS** — Robust, enterprise-ready Python framework providing battle-tested ORM, CSRF protection, and administrative tooling.
- **REST API Framework**: **Django REST Framework (DRF) 3.15+** — Serializers with strict validation, ModelViewSets, APIView classes, and standard pagination.
- **Authentication**: **`djangorestframework-simplejwt`** — RFC 7519 compliant JSON Web Token authentication with rotating refresh tokens.
- **Database Driver / Adapter**: **`psycopg` (v3) / `psycopg2-binary`** and **`dj-database-url`** for 12-factor application database configuration via URL.
- **API Documentation**: **`drf-spectacular`** — Generates OpenAPI 3.0 schema with interactive Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`).
- **CORS Handling**: **`django-cors-headers`** — Fine-grained origin whitelist management for Netlify domains and local development.
- **Testing Framework**: **`pytest`** and **`pytest-django`** — High-speed test execution, fixtures, and database rollback test cases.

### 3.3 Database Tier (Persistence & Storage)
- **Engine**: **Supabase PostgreSQL 15+** (Cloud-hosted).
- **Normalization**: Strict **Third Normal Form (3NF)** relational model with foreign key referential integrity constraints (`ON DELETE CASCADE` / `PROTECT`).
- **Connection Modes**:
  - Direct connection (Port `5432`): Used for Django migrations and schema DDL updates.
  - Pooled connection (Port `6543`, Transaction mode): Used for high-concurrency production API web workers on Render.
- **Indexes**: Explicit B-Tree indexes on all foreign keys, composite indexes on `(user_id, security_id)`, and timestamp indexes for trade/historical quote queries.

### 3.4 Infrastructure & Hosting Architecture
- **Version Control**: **GitHub** repository (`mca2-fsdpython-portfoliopro`) utilizing Git Feature Branch Workflow (`develop` -> `feature/*` -> `main`).
- **Backend Cloud Hosting**: **Render**
  - Managed Web Service executing `gunicorn portfoliopro.wsgi:application`.
  - Automatic builds on push to `develop` or `main`.
  - Native environment variable secrets injection.
- **Frontend Cloud Hosting**: **Netlify**
  - High-performance Global CDN serving compiled Vite assets.
  - Custom `_redirects` file (`/* /index.html 200`) enabling seamless React Router SPA client-side deep linking.
  - Automatic deployment previews from GitHub pull requests.

---

## 4. Environment Variables Specification

To ensure zero leakage of credentials, all application components load secrets from `.env` files:

### Backend (`backend/.env`)
```env
# Django Core Settings
SECRET_KEY=django-insecure-example-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,portfoliopro-api.onrender.com

# Database Connection (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# CORS Whitelist
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://portfoliopro.netlify.app

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
```

### Frontend (`frontend/.env`)
```env
# API Gateway Endpoint
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

## 5. Software Requirements & Local Development Tooling

As specified in Table 4 & 5 of the academic guide, developers must maintain the following local configuration:

- **OS**: Windows 10/11 64-bit, macOS, or Linux.
- **Processor**: Intel Core i5 (8th Gen+) or AMD Ryzen 5 (4+ cores).
- **RAM**: 8 GB minimum (16 GB recommended).
- **Storage**: SSD with at least 20 GB free space.
- **Node.js**: v18 LTS or v20 LTS with npm.
- **Python**: v3.11 or later with pip and venv.
- **Git**: v2.40 or later.
- **Editor**: Visual Studio Code (with Python, Pylance, and ESLint extensions).
- **API Client**: Postman or Thunder Client / Swagger UI.
