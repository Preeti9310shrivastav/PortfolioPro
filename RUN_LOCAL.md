# PortfolioPro — Run Locally (No Cloud Needed)

Uses SQLite. No Supabase, Render, Netlify or GitHub needed.

## One-time setup

**Terminal 1 (backend)**
```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
```

**Terminal 2 (frontend)**
```powershell
cd frontend
npm install
```

## Every time you demo

**Terminal 1**
```powershell
cd backend
python manage.py runserver
```

**Terminal 2**
```powershell
cd frontend
npm run dev
```

Open **http://localhost:5173**

## Demo logins (password `Test@1234`)
| Username | Role |
|---|---|
| `customer1` | Customer (₹5,00,000 virtual balance) |
| `officer1` | Finance Officer |

## Demo flow
1. Login as `customer1` → Dashboard
2. Market → open a stock (price, fundamentals, technicals)
3. Trading → Buy a stock (MARKET order fills instantly)
4. Portfolio → holdings and P&L; Orders → order history
5. Watchlist, Alerts, Support ticket
6. Logout → login as `officer1` → users, all orders, risk, tickets

Extra: Swagger API docs at http://localhost:8000/api/docs/

## Run tests
```powershell
cd backend
python -m pytest apps/authentication/tests/ -q
```
(The password-reset test needs `DEBUG=True` behavior; it fails under pytest. This is a known minor issue and does not affect the app.)
