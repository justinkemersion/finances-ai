Finance AI Analyzer

A privacy-first, developer-controlled personal finance analyzer built on Plaid (Schwab) with deterministic analytics and optional AI explanations.

This project is intentionally designed to avoid AI subscriptions, avoid direct AI access to financial data, and remain compliant with modern banking security expectations.

> Core idea: Software computes. AI explains. Humans stay in control.




---

✨ Features

🔐 Secure, read-only banking access via Plaid

📈 Net worth tracking (daily snapshots)

📊 Portfolio performance & allocation analytics

🧮 Deterministic, auditable financial calculations

🗣️ Optional natural-language explanations (local or pay-per-call AI)

🧠 Intent-based query routing ("How did my portfolio do last month?")

🚫 No screen scraping

🚫 No AI with direct access to bank data

🚫 No required AI subscription



---

🏗️ Architecture Overview

User
 ↓
Dashboard / CLI
 ↓
Intent Router (non-AI or local LLM)
 ↓
Analytics Layer (deterministic)
 ↓
Database (encrypted)
 ↓
Plaid API (Schwab, read-only)

Key principle:

Plaid talks to banks

Your backend talks to Plaid

AI never talks to Plaid



---

📂 Project Structure

```
finances-ai/
├── backend/
│   ├── app/
│   │   ├── analytics/      # Net worth, performance, allocation, income
│   │   │   ├── allocation.py
│   │   │   ├── income.py
│   │   │   ├── net_worth.py
│   │   │   └── performance.py
│   │   ├── api/            # HTTP / CLI interface
│   │   │   ├── cli.py
│   │   │   └── rest.py
│   │   ├── models/         # DB models (accounts, holdings, transactions, net_worth)
│   │   │   ├── account.py
│   │   │   ├── holding.py
│   │   │   ├── net_worth.py
│   │   │   └── transaction.py
│   │   ├── plaid/          # Plaid client & sync jobs
│   │   │   ├── client.py
│   │   │   ├── sync.py
│   │   │   └── test_connection.py
│   │   ├── queries/        # Intent routing & query handlers
│   │   │   ├── handlers.py
│   │   │   └── intent_router.py
│   │   ├── config.py       # Application configuration
│   │   ├── database.py     # Database setup
│   │   └── __main__.py     # CLI entry point
│   └── main.py             # API server entry point
├── migrations/             # Alembic database migrations
│   ├── versions/           # Migration files
│   ├── env.py
│   └── script.py.mako
├── frontend/               # Optional dashboard (placeholder)
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Python project configuration
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── SETUP.md                # Setup instructions
├── PLAID_SETUP.md          # Plaid configuration guide
├── GET_TOKEN.md            # Guide for getting Plaid tokens
└── TRANSACTION_ANALYSIS.md # Transaction data model documentation
```

This structure is Cursor-friendly and optimized for safe refactoring.


---

🔌 Data Sources

Plaid

Accounts

Balances

Investment holdings

Investment transactions


Supported Institutions

Charles Schwab (primary target)

Other Plaid-supported brokerages may work


> Access is read-only, OAuth-based, and user-revocable.




---
