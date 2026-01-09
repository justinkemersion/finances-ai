# Finance AI Analyzer

A privacy-first, developer-controlled personal finance analyzer built on Plaid with deterministic analytics and optional AI explanations.

This project is intentionally designed to avoid AI subscriptions, avoid direct AI access to financial data, and remain compliant with modern banking security expectations.

> **Core principle:** Software computes. AI explains. Humans stay in control.

---

## ✨ Features

### 🔐 Security & Privacy
- **Secure, read-only banking access** via Plaid API
- **No screen scraping** - all data comes through official APIs
- **No AI with direct access** to bank data
- **No required AI subscription** - use local LLMs or pay-per-call
- **OAuth-based access** - user-revocable at any time

### 💰 Financial Tracking
- **Net worth tracking** with daily snapshots
- **Portfolio performance** & allocation analytics
- **Income tracking** - salary, dividends, interest, deposits
- **Expense categorization** - groceries, gas, bills, restaurants, etc.
- **Transaction analysis** - investment and banking transactions
- **Top merchants** - see where you spend the most

### 📊 Analytics & Insights
- **Deterministic calculations** - all analytics are auditable and reproducible
- **Monthly trends** - income and expense patterns over time
- **Category breakdowns** - spending by category (groceries, gas, bills, etc.)
- **Portfolio allocation** - holdings by security and account
- **Performance metrics** - returns, gains/losses, annualized performance

### 🗣️ Natural Language Interface
- **Intent-based query routing** - ask questions in plain English
- **Optional AI explanations** - get insights without giving AI direct data access
- **Query suggestions** - helpful prompts when queries aren't understood

### 🎨 Visualization
- **HTML Dashboard** - beautiful, responsive financial dashboard
- **CLI tables** - rich formatted tables in the terminal
- **Color-coded values** - green for income, red for expenses

---

## 🏗️ Architecture Overview

```
User
 ↓
Dashboard / CLI
 ↓
Intent Router (non-AI or local LLM)
 ↓
Analytics Layer (deterministic)
 ↓
Database (SQLite/PostgreSQL)
 ↓
Plaid API (read-only)
 ↓
Your Bank (Schwab, Chase, etc.)
```

**Key principle:**
- Plaid talks to banks
- Your backend talks to Plaid
- AI never talks to Plaid

---

## 📂 Project Structure

```
finances-ai/
├── backend/
│   ├── app/
│   │   ├── analytics/          # Deterministic analytics
│   │   │   ├── allocation.py    # Portfolio allocation
│   │   │   ├── expenses.py      # Expense analytics
│   │   │   ├── income.py        # Income tracking
│   │   │   ├── net_worth.py     # Net worth calculations
│   │   │   └── performance.py   # Portfolio performance
│   │   ├── api/                 # HTTP / CLI interface
│   │   │   ├── cli.py           # Command-line interface
│   │   │   ├── dashboard.py     # HTML dashboard generator
│   │   │   └── rest.py          # REST API (FastAPI)
│   │   ├── models/              # Database models
│   │   │   ├── account.py       # Account model
│   │   │   ├── holding.py       # Investment holdings
│   │   │   ├── net_worth.py     # Net worth snapshots
│   │   │   └── transaction.py   # Transactions (investment + banking)
│   │   ├── plaid/               # Plaid integration
│   │   │   ├── client.py         # Plaid API client
│   │   │   ├── sync.py          # Data synchronization
│   │   │   └── test_connection.py # Connection testing
│   │   ├── queries/             # Intent routing
│   │   │   ├── handlers.py      # Query handlers
│   │   │   └── intent_router.py # Intent detection
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   └── __main__.py          # CLI entry point
│   └── main.py                  # API server entry point
├── migrations/                  # Alembic database migrations
│   ├── versions/                # Migration files
│   ├── env.py
│   └── script.py.mako
├── frontend/                    # Optional dashboard (placeholder)
├── alembic.ini                  # Alembic configuration
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── SETUP.md                     # Setup instructions
├── PLAID_SETUP.md               # Plaid configuration guide
├── GET_TOKEN.md                 # Guide for getting Plaid tokens
└── TRANSACTION_ANALYSIS.md      # Transaction data model documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Plaid account and API credentials (see [PLAID_SETUP.md](PLAID_SETUP.md))

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd finances-ai
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the project root:
```env
DATABASE_URL=sqlite:///./finance_ai.db
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
API_HOST=0.0.0.0
API_PORT=8000
```

5. **Initialize the database:**
```bash
python -m backend.app.api.cli init-db
# Or using Alembic:
alembic upgrade head
```

6. **Get Plaid access token:**
```bash
python -m backend.app.api.cli get-token
```

7. **Sync your data:**
```bash
python -m backend.app.api.cli sync --access-token <token> --item-id <item_id>
```

---

## 📖 Usage

### CLI Commands

#### Account Management
```bash
# List all accounts
python -m backend.app.api.cli accounts
```

#### Net Worth & Portfolio
```bash
# Show current net worth
python -m backend.app.api.cli net-worth

# Show portfolio allocation
python -m backend.app.api.cli allocation --limit 10

# Show portfolio performance
python -m backend.app.api.cli performance --days 30
```

#### Income Tracking
```bash
# Show income summary (last 6 months)
python -m backend.app.api.cli income --months 6

# List paystub transactions
python -m backend.app.api.cli paystubs --limit 10

# List all deposits
python -m backend.app.api.cli deposits --limit 20
```

#### Expense Tracking
```bash
# Show expense summary and breakdown
python -m backend.app.api.cli expenses --months 3

# List expense transactions
python -m backend.app.api.cli spending --limit 20 --category groceries

# Show top merchants by spending
python -m backend.app.api.cli merchants --limit 10
```

#### Data Synchronization
```bash
# Sync data from Plaid
python -m backend.app.api.cli sync --access-token <token> --item-id <item_id>

# Sync only transactions (skip holdings)
python -m backend.app.api.cli sync --access-token <token> --item-id <item_id> --no-holdings
```

#### Natural Language Queries
```bash
# Ask questions about your finances
python -m backend.app.api.cli ask "What's my net worth?"
python -m backend.app.api.cli ask "How did my portfolio perform last month?"
python -m backend.app.api.cli ask "Show my top expenses"
```

#### Dashboard
```bash
# Generate HTML dashboard
python -m backend.app.api.cli dashboard

# Open in browser
xdg-open dashboard.html  # Linux
open dashboard.html      # macOS
```

---

## 🔌 Data Sources

### Plaid Integration

The application uses Plaid to securely connect to financial institutions:

**Supported Data:**
- Accounts (checking, savings, investment, credit cards)
- Balances (current, available, limit)
- Investment holdings (stocks, bonds, mutual funds, etc.)
- Investment transactions (buys, sells, dividends, fees)
- **Banking transactions** (purchases, deposits, transfers)
- **Transaction categories** (groceries, gas, bills, restaurants, etc.)

**Supported Institutions:**
- Charles Schwab (primary target)
- Any Plaid-supported institution (banks, brokerages, credit cards)

> Access is read-only, OAuth-based, and user-revocable at any time.

---

## 💡 Key Features Explained

### Expense Categorization

The system automatically categorizes expenses using Plaid's personal finance categories:

- **Groceries** - Supermarket purchases
- **Gas** - Gas station transactions
- **Bills** - Utilities, rent, subscriptions
- **Restaurants** - Dining out
- **Shopping** - Retail purchases
- **Transportation** - Rideshare, public transit
- **Entertainment** - Movies, events, hobbies
- And many more...

Categories are automatically assigned based on merchant information and Plaid's categorization engine.

### Income Detection

The system automatically identifies income transactions:

- **Salary/Paystubs** - Detected via keywords (payroll, paycheck, direct deposit)
- **Dividends** - Investment dividends
- **Interest** - Interest earned
- **Deposits** - General deposits and transfers

### Transaction Types

The system handles two types of transactions:

1. **Investment Transactions** - From investment accounts (401k, IRA, brokerage)
   - Buys, sells, dividends, interest, fees
   - Includes security information (ticker, quantity, price)

2. **Banking Transactions** - From checking, savings, credit cards
   - Purchases, deposits, transfers
   - Includes merchant information and location data
   - Automatically categorized by expense type

---

## 🛠️ Development

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
# Run tests (when implemented)
pytest
```

### Code Structure

- **Analytics** - All calculations are deterministic and auditable
- **Models** - SQLAlchemy models with comprehensive transaction fields
- **Sync** - Handles both investment and banking transaction syncing
- **CLI** - Rich formatted output using the `rich` library

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[PLAID_SETUP.md](PLAID_SETUP.md)** - Plaid account setup guide
- **[GET_TOKEN.md](GET_TOKEN.md)** - Getting Plaid access tokens
- **[TRANSACTION_ANALYSIS.md](TRANSACTION_ANALYSIS.md)** - Transaction data model details

---

## 🔒 Privacy & Security

- **No AI subscriptions required** - Use local LLMs or pay-per-call services
- **No direct AI access** - AI only sees aggregated, anonymized data
- **Read-only access** - Plaid connection is read-only, cannot move money
- **User control** - Revoke access at any time through Plaid
- **Local storage** - All data stored locally in your database
- **Encrypted connections** - All API calls use HTTPS

---

## 🎯 Roadmap

- [ ] Enhanced expense budgeting
- [ ] Recurring transaction detection
- [ ] Tax categorization
- [ ] Multi-currency support
- [ ] Web dashboard (optional)
- [ ] Mobile app (optional)
- [ ] Export to CSV/PDF
- [ ] Custom category rules

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

This is a simple, permissive license that allows you to use, modify, and distribute the software freely.

---

## 🙏 Acknowledgments

- Built with [Plaid](https://plaid.com) for secure financial data access
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database management
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- CLI formatting with [Rich](https://rich.readthedocs.io/)

---

**Remember:** This tool gives you control over your financial data. You own it, you control it, and you decide how to use it.
