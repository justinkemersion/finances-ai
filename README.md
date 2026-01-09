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

finance-ai/
├── backend/
│   ├── app/
│   │   ├── plaid/          # Plaid client & sync jobs
│   │   ├── models/         # DB models (accounts, holdings, txns)
│   │   ├── analytics/      # Net worth, performance, allocation
│   │   ├── queries/        # Intent routing & query handlers
│   │   └── api/            # HTTP / CLI interface
│   └── main.py
├── migrations/
├── frontend/               # Optional dashboard
└── README.md

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
