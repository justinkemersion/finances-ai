# Transaction Data Model for Analysis

The transaction model has been enhanced with comprehensive fields to support deep analysis, categorization, and future ML/AI features.

## Core Transaction Data

### Basic Information
- **date**: Transaction date
- **transaction_datetime**: Precise timestamp from Plaid (if available)
- **name**: Transaction name/description
- **amount**: Transaction amount
- **currency_code**: Primary currency (default: USD)
- **iso_currency_code**: ISO 4217 currency code
- **unofficial_currency_code**: Non-standard currency codes

### Transaction Classification
- **type**: Primary type (buy, sell, dividend, fee, etc.)
- **subtype**: More specific subtype from Plaid
- **category**: User-defined or Plaid category
- **user_category**: User-assigned category (preserved during syncs)

### Security Information
- **security_id**: Plaid security identifier
- **ticker**: Stock ticker symbol
- **quantity**: Number of shares
- **price**: Price per share
- **fees**: Transaction fees

## Enhanced Analysis Fields

### Location Data
- **location_city**: City where transaction occurred
- **location_region**: State/province
- **location_country**: Country
- **location_address**: Street address
- **location_postal_code**: Postal/ZIP code

*Note: Investment transactions may not always have location data, but these fields are available for future use with other transaction types.*

### User-Defined Categorization
- **user_category**: Custom category assigned by user
- **tags**: JSON array of flexible tags (e.g., ["tax-2024", "dividend", "reinvest"])
- **notes**: Free-form text notes about the transaction

### Tax Planning
- **is_tax_deductible**: Boolean flag for tax-deductible transactions
- **tax_category**: Tax category (e.g., "dividend", "capital_gain", "interest")

### Recurring Transaction Detection
- **is_recurring**: Whether transaction is part of a recurring pattern
- **recurring_pattern**: Pattern type (e.g., "monthly", "quarterly", "annual")
- **confidence_score**: ML/analysis confidence score (0-100)

### Income and Deposit Classification
- **is_income**: Boolean flag indicating income transaction
- **is_deposit**: Boolean flag indicating deposit transaction
- **income_type**: Type of income (salary, dividend, interest, etc.)
- **is_paystub**: Boolean flag for payroll/paystub transactions
- **paystub_period_start**: Pay period start date (for paystubs)
- **paystub_period_end**: Pay period end date (for paystubs)

### Transaction Status
- **is_pending**: Whether transaction is pending
- **is_cancelled**: Whether transaction was cancelled
- **cancel_transaction_id**: Reference to cancellation transaction

### Raw Data Storage
- **plaid_data**: Complete JSON dump of raw Plaid transaction data
  - Preserves all original data for future analysis
  - Allows extraction of additional fields without re-syncing
  - Useful for debugging and data recovery

## Indexes for Performance

The model includes comprehensive indexes for efficient querying:

- **Date/Account queries**: `idx_transaction_account_date`, `idx_transaction_date_range`
- **Type/Category queries**: `idx_transaction_type`, `idx_transaction_subtype`, `idx_transaction_category`, `idx_transaction_user_category`
- **Security queries**: `idx_transaction_security`, `idx_transaction_ticker`
- **Status queries**: `idx_transaction_pending`, `idx_transaction_recurring`
- **Merchant queries**: `idx_transaction_merchant`

## Use Cases

### 1. Transaction Categorization
```python
# Tag transactions for easy filtering
transaction.tags = ["dividend", "reinvest", "tax-2024"]
transaction.user_category = "Income - Dividends"
transaction.notes = "Quarterly dividend from AAPL"
```

### 2. Tax Planning
```python
# Mark tax-relevant transactions
transaction.is_tax_deductible = True
transaction.tax_category = "dividend"
```

### 3. Recurring Transaction Analysis
```python
# Detect and mark recurring transactions
transaction.is_recurring = True
transaction.recurring_pattern = "quarterly"
transaction.confidence_score = 95.5
```

### 4. Location-Based Analysis
```python
# Track transaction locations (for future features)
transaction.location_country = "US"
transaction.location_region = "CA"
```

### 5. Data Mining from Raw Plaid Data
```python
# Extract additional fields from plaid_data JSON
import json
plaid_data = json.loads(transaction.plaid_data)
# Access any field that Plaid provides
```

## Future Analysis Features

With this comprehensive data model, you can build:

1. **Spending Analysis**: Categorize and analyze spending patterns
2. **Tax Reporting**: Generate tax reports from categorized transactions
3. **Recurring Transaction Detection**: ML-based detection of recurring patterns
4. **Anomaly Detection**: Identify unusual transactions
5. **Portfolio Analysis**: Track investment transactions over time
6. **Cash Flow Analysis**: Analyze income and expenses
7. **Custom Reports**: Generate reports based on tags, categories, dates, etc.

## Migration

To apply the new fields to your database:

```bash
alembic upgrade head
```

This will add all new columns while preserving existing transaction data.
