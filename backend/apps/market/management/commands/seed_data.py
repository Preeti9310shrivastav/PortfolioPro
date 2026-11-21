"""
Management command to seed initial demo data for PortfolioPro.
Creates demo users, NSE equity securities, live market quotes,
fundamental metrics, technical indicators, default watchlist, and notifications.
"""
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.authentication.models import User, UserProfile
from apps.accounts.models import TradingAccount
from apps.portfolio.models import Portfolio
from apps.market.models import Security, MarketQuote, Watchlist, WatchlistItem
from apps.fundamental.models import FundamentalMetric
from apps.technical.models import TechnicalIndicator
from apps.notifications.models import UserNotification


STOCKS_DATA = [
    {
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Ltd",
        "sector": "Energy",
        "isin_code": "INE002A01018",
        "ltp": Decimal("2485.50"),
        "change_percent": Decimal("1.25"),
    },
    {
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services Ltd",
        "sector": "Information Technology",
        "isin_code": "INE467B01029",
        "ltp": Decimal("3892.75"),
        "change_percent": Decimal("-0.45"),
    },
    {
        "symbol": "HDFCBANK",
        "company_name": "HDFC Bank Ltd",
        "sector": "Banking",
        "isin_code": "INE040A01034",
        "ltp": Decimal("1645.30"),
        "change_percent": Decimal("0.78"),
    },
    {
        "symbol": "INFY",
        "company_name": "Infosys Ltd",
        "sector": "Information Technology",
        "isin_code": "INE009A01021",
        "ltp": Decimal("1567.80"),
        "change_percent": Decimal("-1.12"),
    },
    {
        "symbol": "ICICIBANK",
        "company_name": "ICICI Bank Ltd",
        "sector": "Banking",
        "isin_code": "INE090A01021",
        "ltp": Decimal("1089.45"),
        "change_percent": Decimal("0.92"),
    },
    {
        "symbol": "HINDUNILVR",
        "company_name": "Hindustan Unilever Ltd",
        "sector": "FMCG",
        "isin_code": "INE030A01027",
        "ltp": Decimal("2534.60"),
        "change_percent": Decimal("-0.33"),
    },
    {
        "symbol": "SBIN",
        "company_name": "State Bank of India",
        "sector": "Banking",
        "isin_code": "INE062A01020",
        "ltp": Decimal("625.40"),
        "change_percent": Decimal("1.65"),
    },
    {
        "symbol": "BHARTIARTL",
        "company_name": "Bharti Airtel Ltd",
        "sector": "Telecom",
        "isin_code": "INE397D01024",
        "ltp": Decimal("1456.70"),
        "change_percent": Decimal("0.55"),
    },
    {
        "symbol": "KOTAKBANK",
        "company_name": "Kotak Mahindra Bank Ltd",
        "sector": "Banking",
        "isin_code": "INE237A01028",
        "ltp": Decimal("1823.90"),
        "change_percent": Decimal("-0.28"),
    },
    {
        "symbol": "ITC",
        "company_name": "ITC Ltd",
        "sector": "FMCG",
        "isin_code": "INE154A01025",
        "ltp": Decimal("445.20"),
        "change_percent": Decimal("0.85"),
    },
    {
        "symbol": "LT",
        "company_name": "Larsen & Toubro Ltd",
        "sector": "Infrastructure",
        "isin_code": "INE018A01030",
        "ltp": Decimal("3245.60"),
        "change_percent": Decimal("1.45"),
    },
    {
        "symbol": "AXISBANK",
        "company_name": "Axis Bank Ltd",
        "sector": "Banking",
        "isin_code": "INE238A01034",
        "ltp": Decimal("1098.75"),
        "change_percent": Decimal("-0.65"),
    },
    {
        "symbol": "WIPRO",
        "company_name": "Wipro Ltd",
        "sector": "Information Technology",
        "isin_code": "INE075A01022",
        "ltp": Decimal("467.30"),
        "change_percent": Decimal("0.42"),
    },
    {
        "symbol": "MARUTI",
        "company_name": "Maruti Suzuki India Ltd",
        "sector": "Automobile",
        "isin_code": "INE585B01010",
        "ltp": Decimal("10875.40"),
        "change_percent": Decimal("1.85"),
    },
    {
        "symbol": "HCLTECH",
        "company_name": "HCL Technologies Ltd",
        "sector": "Information Technology",
        "isin_code": "INE860A01027",
        "ltp": Decimal("1534.20"),
        "change_percent": Decimal("-0.72"),
    },
    {
        "symbol": "SUNPHARMA",
        "company_name": "Sun Pharmaceutical Industries Ltd",
        "sector": "Pharma",
        "isin_code": "INE044A01036",
        "ltp": Decimal("1245.80"),
        "change_percent": Decimal("0.95"),
    },
    {
        "symbol": "TATAMOTORS",
        "company_name": "Tata Motors Ltd",
        "sector": "Automobile",
        "isin_code": "INE155A01022",
        "ltp": Decimal("745.60"),
        "change_percent": Decimal("2.15"),
    },
    {
        "symbol": "BAJFINANCE",
        "company_name": "Bajaj Finance Ltd",
        "sector": "Financial Services",
        "isin_code": "INE296A01024",
        "ltp": Decimal("6789.30"),
        "change_percent": Decimal("-1.45"),
    },
    {
        "symbol": "TITAN",
        "company_name": "Titan Company Ltd",
        "sector": "Consumer Goods",
        "isin_code": "INE280A01028",
        "ltp": Decimal("3245.70"),
        "change_percent": Decimal("0.68"),
    },
    {
        "symbol": "ASIANPAINT",
        "company_name": "Asian Paints Ltd",
        "sector": "Consumer Goods",
        "isin_code": "INE021A01026",
        "ltp": Decimal("2890.40"),
        "change_percent": Decimal("-0.55"),
    },
    {
        "symbol": "NESTLEIND",
        "company_name": "Nestle India Ltd",
        "sector": "FMCG",
        "isin_code": "INE239A01016",
        "ltp": Decimal("2456.70"),
        "change_percent": Decimal("0.32"),
    },
    {
        "symbol": "POWERGRID",
        "company_name": "Power Grid Corporation of India Ltd",
        "sector": "Energy",
        "isin_code": "INE752E01010",
        "ltp": Decimal("285.40"),
        "change_percent": Decimal("1.75"),
    },
    {
        "symbol": "NTPC",
        "company_name": "NTPC Ltd",
        "sector": "Energy",
        "isin_code": "INE733E01010",
        "ltp": Decimal("345.60"),
        "change_percent": Decimal("1.22"),
    },
    {
        "symbol": "DRREDDY",
        "company_name": "Dr. Reddys Laboratories Ltd",
        "sector": "Pharma",
        "isin_code": "INE089A01023",
        "ltp": Decimal("5678.90"),
        "change_percent": Decimal("-0.88"),
    },
    {
        "symbol": "TECHM",
        "company_name": "Tech Mahindra Ltd",
        "sector": "Information Technology",
        "isin_code": "INE669C01036",
        "ltp": Decimal("1345.60"),
        "change_percent": Decimal("0.45"),
    },
]

WATCHLIST_SYMBOLS = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN"]


class Command(BaseCommand):
    help = "Seeds demo users, securities, market quotes, fundamentals, indicators, and watchlist."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting PortfolioPro database seeding...")
        random.seed(42)

        # 1. Create Demo Users
        users_count = self._seed_users()

        # 2. Create Securities and Market Quotes
        securities_count, quotes_count = self._seed_securities_and_quotes()

        # 3. Create Fundamental Metrics
        fundamentals_count = self._seed_fundamentals()

        # 4. Create Technical Indicators
        indicators_count = self._seed_technical_indicators()

        # 5. Create Default Watchlist for customer1
        watchlist_items_count = self._seed_watchlist()

        # 6. Create Sample Notifications for customer1
        notifications_count = self._seed_notifications()

        # 7. Summary
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("PortfolioPro Demo Data Seeded Successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"Users created/verified:       {users_count}")
        self.stdout.write(f"Securities created/verified:  {securities_count}")
        self.stdout.write(f"Market quotes created:        {quotes_count}")
        self.stdout.write(f"Fundamental metrics created:  {fundamentals_count}")
        self.stdout.write(f"Technical indicators created: {indicators_count}")
        self.stdout.write(f"Watchlist items created:      {watchlist_items_count}")
        self.stdout.write(f"Notifications created:        {notifications_count}")
        self.stdout.write(self.style.SUCCESS("=" * 60))

    def _seed_users(self):
        """Creates customer1 and officer1 with profile, account, and portfolio."""
        # customer1
        customer1 = User.objects.filter(username="customer1").first()
        if not customer1:
            customer1 = User.objects.create_user(
                username="customer1",
                email="customer1@portfoliopro.in",
                password="Test@1234",
                first_name="Aman",
                last_name="Sharma",
                role=User.ROLE_CUSTOMER,
            )
        else:
            customer1.email = "customer1@portfoliopro.in"
            customer1.first_name = "Aman"
            customer1.last_name = "Sharma"
            customer1.role = User.ROLE_CUSTOMER
            customer1.set_password("Test@1234")
            customer1.save()

        UserProfile.objects.update_or_create(
            user=customer1,
            defaults={
                "bio": "Retail investor passionate about Indian equities.",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "pincode": "400001",
            },
        )

        TradingAccount.objects.update_or_create(
            user=customer1,
            defaults={
                "account_number": "PPRO-DEMO01",
                "currency": "INR",
                "cash_balance": Decimal("500000.0000"),
                "margin_used": Decimal("0.0000"),
                "account_status": TradingAccount.STATUS_ACTIVE,
            },
        )

        Portfolio.objects.update_or_create(
            user=customer1,
            name="Primary Portfolio",
            defaults={"is_default": True},
        )

        # officer1
        officer1 = User.objects.filter(username="officer1").first()
        if not officer1:
            officer1 = User.objects.create_user(
                username="officer1",
                email="officer1@portfoliopro.in",
                password="Test@1234",
                first_name="Priya",
                last_name="Singh",
                role=User.ROLE_FINANCE_OFFICER,
            )
        else:
            officer1.email = "officer1@portfoliopro.in"
            officer1.first_name = "Priya"
            officer1.last_name = "Singh"
            officer1.role = User.ROLE_FINANCE_OFFICER
            officer1.set_password("Test@1234")
            officer1.save()

        UserProfile.objects.update_or_create(
            user=officer1,
            defaults={
                "bio": "Finance and Compliance Officer at PortfolioPro.",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "pincode": "400051",
            },
        )

        return 2

    def _seed_securities_and_quotes(self):
        """Creates 25 NSE securities with their corresponding live MarketQuotes."""
        sec_count = 0
        quote_count = 0

        for stock in STOCKS_DATA:
            security, _ = Security.objects.update_or_create(
                symbol=stock["symbol"],
                defaults={
                    "company_name": stock["company_name"],
                    "exchange": Security.EXCHANGE_NSE,
                    "sector": stock["sector"],
                    "industry": stock["sector"],
                    "lot_size": 1,
                    "isin_code": stock["isin_code"],
                    "is_active": True,
                },
            )
            sec_count += 1

            ltp = stock["ltp"]
            change_pct = stock["change_percent"]
            open_price = (ltp * Decimal("0.99")).quantize(Decimal("0.0001"))
            high_price = (ltp * Decimal("1.02")).quantize(Decimal("0.0001"))
            low_price = (ltp * Decimal("0.98")).quantize(Decimal("0.0001"))
            close_price = (ltp * (Decimal("1") - change_pct / Decimal("100"))).quantize(
                Decimal("0.0001")
            )
            volume = random.randint(100000, 5000000)
            change_amount = (ltp * change_pct / Decimal("100")).quantize(Decimal("0.0001"))
            week_52_high = (ltp * Decimal("1.15")).quantize(Decimal("0.0001"))
            week_52_low = (ltp * Decimal("0.75")).quantize(Decimal("0.0001"))

            MarketQuote.objects.update_or_create(
                security=security,
                defaults={
                    "ltp": ltp.quantize(Decimal("0.0001")),
                    "open_price": open_price,
                    "high_price": high_price,
                    "low_price": low_price,
                    "close_price": close_price,
                    "volume": volume,
                    "change_amount": change_amount,
                    "change_percent": change_pct.quantize(Decimal("0.0001")),
                    "week_52_high": week_52_high,
                    "week_52_low": week_52_low,
                },
            )
            quote_count += 1

        return sec_count, quote_count

    def _seed_fundamentals(self):
        """Creates FundamentalMetric entries for each equity security."""
        count = 0
        for stock in STOCKS_DATA:
            security = Security.objects.get(symbol=stock["symbol"])
            ltp = stock["ltp"]

            pe_ratio = Decimal(str(round(random.uniform(15.0, 45.0), 2))).quantize(
                Decimal("0.0001")
            )
            eps = (ltp / pe_ratio).quantize(Decimal("0.0001"))
            pb_ratio = Decimal(str(round(random.uniform(2.0, 8.0), 2))).quantize(
                Decimal("0.0001")
            )
            dividend_yield = Decimal(str(round(random.uniform(0.5, 3.5), 2))).quantize(
                Decimal("0.0001")
            )
            debt_to_equity = Decimal(str(round(random.uniform(0.1, 1.5), 2))).quantize(
                Decimal("0.0001")
            )
            roe = Decimal(str(round(random.uniform(10.0, 30.0), 2))).quantize(
                Decimal("0.0001")
            )
            market_cap_factor = Decimal(random.randint(1000000000, 5000000000))
            market_cap = (ltp * market_cap_factor).quantize(Decimal("0.0001"))
            book_value = (ltp / pb_ratio).quantize(Decimal("0.0001"))
            health_score = random.randint(4, 9)

            FundamentalMetric.objects.update_or_create(
                security=security,
                defaults={
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "eps": eps,
                    "dividend_yield": dividend_yield,
                    "debt_to_equity": debt_to_equity,
                    "roe": roe,
                    "book_value": book_value,
                    "health_score": health_score,
                    "financial_year": "2024-25",
                },
            )
            count += 1

        return count

    def _seed_technical_indicators(self):
        """Creates TechnicalIndicator records for each equity security."""
        today = timezone.now().date()
        count = 0

        for stock in STOCKS_DATA:
            security = Security.objects.get(symbol=stock["symbol"])
            ltp = stock["ltp"]

            rsi_float = round(random.uniform(25.0, 75.0), 2)
            rsi_14 = Decimal(str(rsi_float)).quantize(Decimal("0.0001"))

            sma_20 = (ltp * Decimal(str(round(random.uniform(0.95, 1.05), 4)))).quantize(
                Decimal("0.0001")
            )
            sma_50 = (ltp * Decimal(str(round(random.uniform(0.90, 1.10), 4)))).quantize(
                Decimal("0.0001")
            )
            sma_200 = (ltp * Decimal(str(round(random.uniform(0.85, 1.15), 4)))).quantize(
                Decimal("0.0001")
            )
            ema_20 = (ltp * Decimal(str(round(random.uniform(0.96, 1.04), 4)))).quantize(
                Decimal("0.0001")
            )

            macd_line_float = round(random.uniform(-5.0, 5.0), 4)
            macd_line = Decimal(str(macd_line_float)).quantize(Decimal("0.0001"))
            macd_signal = (macd_line * Decimal("0.8000")).quantize(Decimal("0.0001"))
            macd_hist = (macd_line - macd_signal).quantize(Decimal("0.0001"))

            if rsi_float < 30.0:
                overall_signal = TechnicalIndicator.SIGNAL_STRONG_BUY
            elif rsi_float < 45.0:
                overall_signal = TechnicalIndicator.SIGNAL_BUY
            elif rsi_float < 55.0:
                overall_signal = TechnicalIndicator.SIGNAL_NEUTRAL
            elif rsi_float < 70.0:
                overall_signal = TechnicalIndicator.SIGNAL_SELL
            else:
                overall_signal = TechnicalIndicator.SIGNAL_STRONG_SELL

            TechnicalIndicator.objects.update_or_create(
                security=security,
                calculation_date=today,
                defaults={
                    "rsi_14": rsi_14,
                    "sma_20": sma_20,
                    "sma_50": sma_50,
                    "sma_200": sma_200,
                    "ema_20": ema_20,
                    "macd_line": macd_line,
                    "macd_signal": macd_signal,
                    "macd_hist": macd_hist,
                    "overall_signal": overall_signal,
                },
            )
            count += 1

        return count

    def _seed_watchlist(self):
        """Creates a default Watchlist for customer1 with 5 key stocks."""
        customer1 = User.objects.get(username="customer1")
        watchlist, _ = Watchlist.objects.update_or_create(
            user=customer1,
            name="Default Watchlist",
            defaults={"is_default": True},
        )

        count = 0
        for order, symbol in enumerate(WATCHLIST_SYMBOLS, start=1):
            sec = Security.objects.get(symbol=symbol)
            WatchlistItem.objects.update_or_create(
                watchlist=watchlist,
                security=sec,
                defaults={"display_order": order},
            )
            count += 1

        return count

    def _seed_notifications(self):
        """Creates sample notifications for customer1."""
        customer1 = User.objects.get(username="customer1")

        sample_notifications = [
            {
                "title": "Welcome to PortfolioPro",
                "message": (
                    "Welcome aboard, Aman! Your simulated trading account is ready with "
                    "₹5,00,000 in virtual funds to begin exploring Indian equities."
                ),
                "category": UserNotification.CAT_SYSTEM,
                "is_read": True,
                "link_url": "/dashboard",
            },
            {
                "title": "Virtual Account Funded",
                "message": (
                    "Trading account PPRO-DEMO01 credited with ₹500,000.00 virtual cash. "
                    "You are now ready to place equity orders on NSE."
                ),
                "category": UserNotification.CAT_ACCOUNT,
                "is_read": True,
                "link_url": "/accounts",
            },
            {
                "title": "Price Movement: RELIANCE",
                "message": (
                    "Reliance Industries Ltd (RELIANCE) gained +1.25% today, closing at ₹2,485.50."
                ),
                "category": UserNotification.CAT_PRICE_ALERT,
                "is_read": False,
                "link_url": "/market/RELIANCE",
            },
            {
                "title": "Technical Alert: HDFCBANK",
                "message": (
                    "HDFC Bank is consolidating near its 50-day moving average. "
                    "RSI indicates a neutral consolidation zone."
                ),
                "category": UserNotification.CAT_PRICE_ALERT,
                "is_read": False,
                "link_url": "/market/HDFCBANK",
            },
            {
                "title": "Market Wrap: NSE",
                "message": (
                    "Nifty 50 settles higher led by strength in Banking and Auto sectors. "
                    "Advance-Decline ratio remained positive."
                ),
                "category": UserNotification.CAT_SYSTEM,
                "is_read": False,
                "link_url": "/market",
            },
        ]

        count = 0
        for item in sample_notifications:
            UserNotification.objects.update_or_create(
                user=customer1,
                title=item["title"],
                defaults={
                    "message": item["message"],
                    "category": item["category"],
                    "is_read": item["is_read"],
                    "link_url": item["link_url"],
                },
            )
            count += 1

        return count
