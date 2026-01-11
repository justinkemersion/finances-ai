# Finance AI Analyzer

A privacy-first, developer-controlled personal finance analyzer with support for multiple financial data providers (Plaid, Teller) and deterministic analytics with optional AI explanations.

This project is intentionally designed to avoid AI subscriptions, avoid direct AI access to financial data, and remain compliant with modern banking security expectations.

> **Core principle:** Software computes. AI explains. Humans stay in control.

---

## ✨ Features

### 🤖 AI-Powered Financial Analysis ⭐ **NEW & LEADING FEATURE**
**Transform your financial data into actionable insights using state-of-the-art LLMs**

Ask questions in natural language and receive intelligent, context-aware responses that help you understand your finances and make better decisions.

**Key Capabilities:**
- **Multi-Provider Support**: Choose from OpenAI (GPT), Anthropic (Claude), Google (Gemini), or Cohere
- **Intelligent Data Selection**: Automatically includes only relevant data, saving API costs and improving quality
- **Easy Comparison**: Run the same query with different LLMs to get diverse perspectives
- **Flexible Models**: Select exact models to balance cost, speed, and quality
- **Interactive Selection**: Beautiful menu to choose from detected API keys

**Example:**
```bash
python -m backend.app ai "where can I focus on budgeting to make quick wins with savings?"
```

**Unique Use Cases:**
- 💰 **Budget optimization** - Get personalized savings recommendations
- 📊 **Spending pattern analysis** - Understand where your money goes with actionable insights
- 💵 **Income optimization** - Identify additional revenue stream opportunities
- 🏥 **Financial health assessments** - Comprehensive wellness checks
- 🎯 **Goal-based planning** - "Save $10k in 6 months" with step-by-step plans
- 🍽️ **Category deep dives** - Analyze restaurants, groceries, bills, etc.
- 📈 **Investment portfolio reviews** - Get AI-powered portfolio analysis
- 🧾 **Tax planning** - Identify deductions and optimization strategies

**📖 [Complete AI Integration Guide →](AI_INTEGRATION.md)** - Comprehensive documentation with setup, use cases, examples, and best practices

---

### 🔐 Security & Privacy
- **Secure, read-only banking access** via Plaid or Teller APIs
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
- **Smart lunch detection** - confidence scoring handles edge cases (grocery shopping, gas station food)
- **Category-specific queries** - beer, restaurants, gas, groceries, etc.
- **Merchant tracking** - track spending at specific merchants
- **Cash flow analysis** - income vs expenses
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
Provider Layer (Plaid / Teller / Future providers)
 ↓
Your Bank (Schwab, Chase, etc.)
```

**Key principle:**
- Financial providers (Plaid/Teller) talk to banks
- Your backend talks to providers
- AI never talks directly to banks or providers

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
│   │   ├── plaid/               # Plaid integration (legacy)
│   │   │   ├── client.py         # Plaid API client
│   │   │   ├── sync.py          # Data synchronization
│   │   │   └── test_connection.py # Connection testing
│   │   ├── providers/           # Provider abstraction layer
│   │   │   ├── base.py          # Abstract base classes
│   │   │   ├── factory.py       # Provider factory
│   │   │   ├── plaid_client.py  # Plaid implementation
│   │   │   ├── plaid_sync.py    # Plaid sync implementation
│   │   │   ├── teller_client.py # Teller implementation
│   │   │   └── teller_sync.py   # Teller sync implementation
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
├── TELLER_SETUP.md              # Teller configuration guide
├── PROVIDER_ARCHITECTURE.md     # Provider abstraction architecture
├── GET_TOKEN.md                 # Guide for getting Plaid tokens
└── TRANSACTION_ANALYSIS.md      # Transaction data model documentation
```

---

## 💡 Quick Tips

**Don't forget these powerful features:**

1. **Natural Language Queries**: Ask questions in plain English instead of memorizing commands
   - `python -m backend.app ask "how much did I spend on lunch?"`
   - `python -m backend.app ask "lunch spending past 2 months"`
   - See [NATURAL_QUERIES.md](NATURAL_QUERIES.md) for complete query guide

2. **Smart Lunch Detection**: Automatically handles edge cases (grocery shopping, gas station food)
   - Confidence scores show why each transaction was included/excluded
   - Customizable thresholds for your spending patterns
   - See [LUNCH_DETECTION.md](LUNCH_DETECTION.md) for details

3. **AI-Powered Analysis**: Export your data and use with ChatGPT/Claude for deeper insights
   - Get personalized savings recommendations
   - Discover spending patterns and lifestyle alternatives
   - Example: "Analyze my lunch spending and suggest meal prep alternatives"
   - See [EXPORT_GUIDE.md](EXPORT_GUIDE.md) for instructions and example prompts

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Financial data provider account:
  - **Plaid**: API credentials (see [PLAID_SETUP.md](PLAID_SETUP.md))
  - **Teller**: Application ID and certificates (see [TELLER_SETUP.md](TELLER_SETUP.md))

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

# Plaid Configuration (optional)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox

# Teller Configuration (optional)
TELLER_APPLICATION_ID=your_teller_app_id
TELLER_CERTIFICATE_PATH=/path/to/certificate.pem
TELLER_PRIVATE_KEY_PATH=/path/to/private_key.pem
TELLER_ENV=sandbox

# Default provider (plaid or teller)
DEFAULT_PROVIDER=teller

API_HOST=0.0.0.0
API_PORT=8000
```

5. **Initialize the database:**
```bash
python -m backend.app.api.cli init-db
# Or using Alembic:
alembic upgrade head
```

6. **Connect your bank account:**
```bash
# Using Teller (recommended for personal use - free tier available)
python -m backend.app.api.cli connect-bank --provider teller

# Or using Plaid
python -m backend.app.api.cli connect-bank --provider plaid
```

7. **Sync your data:**
```bash
# The connect-bank command will provide you with the access token and item ID
# Use them to sync:
python -m backend.app.api.cli sync --provider teller --access-token <token> --item-id <item_id>
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

#### Bank Account Connection
```bash
# Connect a real bank account with Plaid (opens browser, handles token exchange)
python -m backend.app.api.cli connect-bank --provider plaid

# Connect a real bank account with Teller (opens browser, handles token exchange)
python -m backend.app.api.cli connect-bank --provider teller

# Use a different port if 8080 is busy
python -m backend.app.api.cli connect-bank --provider teller --port 3000

# Create sandbox test item (Plaid only, for testing)
python -m backend.app.api.cli get-token
```

#### Data Synchronization
```bash
# Sync data from Plaid
python -m backend.app.api.cli sync --provider plaid --access-token <token> --item-id <item_id>

# Sync data from Teller
python -m backend.app.api.cli sync --provider teller --access-token <token> --item-id <item_id>

# Sync only transactions (skip holdings)
python -m backend.app.api.cli sync --provider teller --access-token <token> --item-id <item_id> --no-holdings
```

#### 🤖 AI-Powered Analysis (⭐ Recommended)
```bash
# Get personalized financial insights and recommendations
python -m backend.app ai "where can I focus on budgeting to make quick wins with savings?"

# Analyze spending patterns
python -m backend.app ai "analyze my spending patterns and suggest improvements"

# Financial health check
python -m backend.app ai "give me a comprehensive financial health assessment"

# Goal-based planning
python -m backend.app ai "if I want to save $10,000 in 6 months, what changes should I make?"

# Category-specific analysis
python -m backend.app ai "analyze my restaurant spending - am I eating out too much?"

# Use specific provider and model
python -m backend.app ai "budgeting advice" --provider openai --model gpt-4o
python -m backend.app ai "quick insights" --provider google --model gemini-1.5-flash

# List available providers and models
python -m backend.app ai --list-providers
python -m backend.app ai --list-models --provider openai
```

**See [AI_INTEGRATION.md](AI_INTEGRATION.md) for complete guide with 8+ use cases, setup instructions, and best practices!**

#### Natural Language Queries
```bash
# Ask questions about your finances
python -m backend.app ask "What's my net worth?"
python -m backend.app ask "How did my portfolio perform last month?"
python -m backend.app ask "Show my top expenses"
python -m backend.app ask "How much did I spend on beer?"
python -m backend.app ask "Restaurant spending last month"
python -m backend.app ask "How much at Starbucks?"
python -m backend.app ask "What's my income?"
```

#### Test Data Injection
```bash
# Inject realistic test data for testing queries (beer, restaurants, gas, groceries, bills, income)
python -m backend.app inject-test-data

# Generate 6 months of test data
python -m backend.app inject-test-data --months 6

# Skip income transactions
python -m backend.app inject-test-data --no-income

# Inject for specific account
python -m backend.app inject-test-data --account-id <account_id>
```

**Note**: The test data injection creates realistic spending patterns perfect for testing natural language queries. It includes:
- Beer/alcohol transactions (15+)
- Restaurant/dining transactions (25+)
- Gas/fuel transactions (8+)
- Grocery transactions (12+)
- Monthly bills (electric, internet, phone)
- Income/paystub transactions (bi-weekly)

#### Dashboard
```bash
# Generate HTML dashboard
python -m backend.app.api.cli dashboard

# Open in browser
xdg-open dashboard.html  # Linux
open dashboard.html      # macOS
```

#### Data Export (for LLM Analysis)
```bash
# Export entire database to JSON (for ChatGPT, Claude, etc.)
python -m backend.app.api.cli export

# Export specific date range
python -m backend.app.api.cli export --start-date 2024-01-01 --end-date 2024-12-31

# Export only transactions (exclude holdings, net worth)
python -m backend.app.api.cli export --no-holdings --no-net-worth

# Export only banking transactions (exclude investment transactions)
python -m backend.app.api.cli export --no-investment-txns

# Export only expenses
python -m backend.app.api.cli export --transaction-type expense

# Export to custom file
python -m backend.app.api.cli export --output my_finances.json
```

The export creates a JSON file optimized for LLM analysis with:
- **Summary statistics** - Quick overview of your finances
- **Accounts** - All account information
- **Holdings** - Investment holdings
- **Transactions** - All transactions with full details
- **Net worth snapshots** - Historical net worth data

**💡 Pro Tip**: Export your data and upload it to ChatGPT, Claude, or other AI platforms to:
- Get personalized spending analysis and savings recommendations
- Discover spending patterns you might have missed
- Get AI-powered suggestions for lifestyle alternatives (e.g., "You spend $X on lunch - here's how much you'd save by meal prepping")
- Analyze trends and get actionable financial advice
- Compare your spending to benchmarks and get optimization tips

See [EXPORT_GUIDE.md](EXPORT_GUIDE.md) for detailed instructions and example prompts!

---

## 🔌 Data Sources

### Financial Data Providers

The application supports multiple financial data providers through a flexible provider architecture:

- **Plaid** - Industry standard, supports investments and banking
- **Teller** - Free tier available, modern API, great for personal use
- **Future Providers** - Architecture supports easy addition of new providers

See [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md) for details on the provider system.

### Provider Integration

The application supports multiple financial data providers through a flexible abstraction layer:

**Plaid Integration:**
- Industry standard, comprehensive API
- Supports investments and banking
- See [PLAID_SETUP.md](PLAID_SETUP.md) for setup

**Teller Integration:**
- Modern REST API
- Free tier available for personal use
- Certificate-based authentication (mTLS)
- See [TELLER_SETUP.md](TELLER_SETUP.md) for setup

**Supported Data (both providers):**
- Accounts (checking, savings, investment, credit cards)
- Balances (current, available, limit)
- Investment holdings (stocks, bonds, mutual funds, etc.)
- Investment transactions (buys, sells, dividends, fees)
- **Banking transactions** (purchases, deposits, transfers)
- **Transaction categories** (groceries, gas, bills, restaurants, etc.)

**Supported Institutions:**
- Charles Schwab (primary target)
- Any provider-supported institution (banks, brokerages, credit cards)

> Access is read-only, OAuth-based, and user-revocable at any time.

See [PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md) for details on the provider system.

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

The project includes comprehensive test suites for core functionality:

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/test_analytics/          # Analytics tests (net worth, performance, income, expenses, allocation)
pytest tests/test_queries/            # Query processing tests (intent router, handlers, lunch detection)

# Run with coverage
pytest --cov=backend.app --cov-report=html

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_analytics/test_net_worth.py -v
```

#### Test Coverage

**Analytics Tests** (27 tests, 23+ passing):
- Net worth calculations (single/multiple accounts, holdings, snapshots, history)
- Portfolio performance (positive/negative returns, annualization, missing snapshots)
- Income analysis (transactions, summaries, monthly breakdowns, date filtering)
- Expense analysis (categories, merchants, monthly trends, filtering)
- Portfolio allocation (by security, account, type, top holdings)

**Query Processing Tests** (32 tests, 31+ passing):
- Intent router (natural language parsing for all query types)
- Time range extraction (today, yesterday, this week, last month, etc.)
- Filter extraction (account, category, merchant, amount thresholds)
- Query handlers (routing and execution for all intents)
- Lunch detection (confidence scoring, edge cases, time-based filtering)

**Test Infrastructure:**
- Database fixtures with isolated test databases
- Realistic test data generation
- Date/datetime handling for financial calculations
- Edge case coverage (empty accounts, inactive accounts, missing data)

**Current Status:**
- Core analytics: ✅ Fully tested
- Query processing: ✅ Fully tested  
- Lunch detection: ✅ Fully tested
- CLI commands: ⏳ Partial (covered via integration tests)
- API endpoints: ⏳ Pending

### Code Structure

- **Analytics** - All calculations are deterministic and auditable
- **Models** - SQLAlchemy models with comprehensive transaction fields
- **Sync** - Handles both investment and banking transaction syncing
- **CLI** - Rich formatted output using the `rich` library

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[PLAID_SETUP.md](PLAID_SETUP.md)** - Plaid account setup guide
- **[TELLER_SETUP.md](TELLER_SETUP.md)** - Teller account setup guide
- **[PROVIDER_ARCHITECTURE.md](PROVIDER_ARCHITECTURE.md)** - Provider abstraction architecture
- **[GET_TOKEN.md](GET_TOKEN.md)** - Getting Plaid access tokens
- **[TRANSACTION_ANALYSIS.md](TRANSACTION_ANALYSIS.md)** - Transaction data model details
- **[EXPORT_GUIDE.md](EXPORT_GUIDE.md)** - Guide for exporting data to use with LLMs (ChatGPT, Claude, etc.)
- **[NATURAL_QUERIES.md](NATURAL_QUERIES.md)** - Complete guide to natural language queries
- **[LUNCH_DETECTION.md](LUNCH_DETECTION.md)** - Smart lunch detection with confidence scoring
- **[AI_INTEGRATION.md](AI_INTEGRATION.md)** - Complete AI integration guide with use cases and examples

---

## 🔒 Privacy & Security

- **No AI subscriptions required** - Use local LLMs or pay-per-call services
- **No direct AI access** - AI only sees aggregated, anonymized data
- **Read-only access** - Plaid connection is read-only, cannot move money
- **User control** - Revoke access at any time through Plaid
- **Local storage** - All data stored locally in your database
- **Encrypted connections** - All API calls use HTTPS

---

## 📊 Current Project Status

### ✅ Completed
- **Core Infrastructure**: Database models, provider abstraction layer, data synchronization
- **Provider Support**: Plaid and Teller integration with unified interface
- **Bank Account Linking**: CLI commands for connecting accounts via Plaid or Teller
- **Analytics Layer**: Net worth, performance, income, expenses, allocation calculations
- **Natural Language Interface**: Intent routing, query handlers, smart lunch detection
- **AI Integration**: Multi-provider LLM support with intelligent data selection
- **CLI Interface**: Comprehensive command-line interface with rich formatting
- **Test Suite**: 59+ tests covering analytics and query processing
- **Documentation**: README, setup guides, feature documentation, provider architecture

### 🚧 In Progress
- **Teller Sync Implementation**: Complete Teller data synchronization
- **Test Refinement**: Minor test adjustments for edge cases
- **API Endpoints**: REST API implementation (FastAPI)

### 📋 Planned
- **Enhanced Categorization**: Machine learning-based transaction categorization
- **Recurring Transaction Detection**: Automatic identification of subscriptions and bills
- **Budget Tracking**: Set budgets and track against spending
- **Goal Tracking**: Savings goals, debt payoff tracking
- **Advanced Analytics**: Cash flow forecasting, spending predictions
- **Mobile App**: React Native or Flutter mobile interface

### 🎯 Next Steps
1. Complete Teller data synchronization implementation
2. Add REST API endpoints for web/mobile access
3. Enhance transaction categorization with ML
4. Implement budget and goal tracking
5. Build mobile app interface

## 🎯 Roadmap

- [x] Export to JSON for LLM analysis
- [x] Natural language queries
- [x] Smart lunch detection with confidence scoring
- [ ] Enhanced expense budgeting
- [ ] Recurring transaction detection
- [ ] Tax categorization
- [ ] Multi-currency support
- [ ] Web dashboard (optional)
- [ ] Mobile app (optional)
- [ ] Export to CSV/PDF
- [ ] Custom category rules
- [ ] User feedback loop for lunch detection (improve accuracy over time)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

This is a simple, permissive license that allows you to use, modify, and distribute the software freely.

---

## 🙏 Acknowledgments

- Built with [Plaid](https://plaid.com) and [Teller](https://teller.io) for secure financial data access
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database management
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- CLI formatting with [Rich](https://rich.readthedocs.io/)

---

**Remember:** This tool gives you control over your financial data. You own it, you control it, and you decide how to use it.
