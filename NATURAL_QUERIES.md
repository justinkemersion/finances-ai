# Natural Language Query System

The natural language query system allows you to ask questions about your finances in plain English. It uses pattern matching and intent recognition to understand your queries and route them to the appropriate analytics.

## How It Works

### Architecture

1. **Intent Router** (`intent_router.py`): Parses natural language queries and extracts:
   - **Intent**: What type of query (income, expenses, dividends, etc.)
   - **Time Range**: Date filters (last month, this year, etc.)
   - **Category**: Spending categories (beer, restaurants, gas, etc.)
   - **Merchant**: Specific merchant names
   - **Account Filter**: Specific account to query
   - **Amount Threshold**: Filters for amounts above/below thresholds

2. **Query Handlers** (`handlers.py`): Routes parsed queries to appropriate analytics functions

3. **CLI Integration**: The `ask` command provides a user-friendly interface

## Usage

### Basic Usage

```bash
# Ask any question about your finances
python -m backend.app.api.cli ask "how much did I spend last month?"

# Income queries
python -m backend.app.api.cli ask "what's my income this year?"

# Expense queries
python -m backend.app.api.cli ask "show my expenses"

# Category-specific spending
python -m backend.app.api.cli ask "how much did I spend on beer?"
python -m backend.app.api.cli ask "restaurant spending last month"

# Merchant queries
python -m backend.app.api.cli ask "how much at Starbucks?"
python -m backend.app.api.cli ask "spending at Amazon this year"

# Investment queries
python -m backend.app.api.cli ask "what are my dividends?"
python -m backend.app.api.cli ask "how did my portfolio perform?"

# Cash flow
python -m backend.app.api.cli ask "what's my cash flow?"
python -m backend.app.api.cli ask "income vs expenses this month"
```

## Supported Query Types

### 1. Income Queries
**For**: Entrepreneurs tracking revenue, employees tracking salary

**Examples**:
- "What's my income?"
- "How much did I earn last month?"
- "Show my salary"
- "What are my paystubs this year?"

**Returns**: Total income, breakdown by type, paystub information

### 2. Expense Queries
**For**: Everyone tracking spending

**Examples**:
- "How much did I spend?"
- "What are my expenses?"
- "Show my spending last month"

**Returns**: Total expenses, breakdown by category, transaction count

### 3. Category-Specific Spending
**For**: Bachelors tracking specific spending (beer, restaurants, etc.)

**Examples**:
- "How much did I spend on beer?"
- "Restaurant spending last month"
- "Gas expenses this year"
- "How much on groceries?"

**Supported Categories** (with aliases):
- **beer**: beer, alcohol, bar, brewery, pub, liquor, wine, drinks
- **restaurants**: restaurant, dining, food, eat, cafe, coffee, lunch, dinner
- **gas**: gas, fuel, gasoline, petrol, filling station
- **groceries**: grocery, supermarket, food store, grocery store
- **bills**: bill, utility, electric, water, internet, phone, cable
- **entertainment**: entertainment, movie, theater, concert, streaming
- **shopping**: shopping, retail, store, amazon, online
- **transport**: transport, uber, lyft, taxi, transit, bus, train
- **health**: health, medical, doctor, pharmacy, gym, fitness

**Returns**: Total spending for category, transaction list, merchant breakdown

### 4. Merchant Queries
**For**: Tracking spending at specific merchants

**Examples**:
- "How much at Starbucks?"
- "Spending at Amazon last month"
- "What did I spend at Target?"

**Returns**: Total spending at merchant, transaction list, category breakdown

### 4a. Lunch Queries
**For**: Tracking lunch spending specifically (takeout, fast food, etc.)

**Examples**:
- "How much did I spend on lunch?"
- "Lunch spending last month"
- "Lunch expenses past 2 months"

**Smart Detection**:
- **Time-based**: Automatically filters transactions between 11am-2:30pm
- **Merchant-based**: Recognizes common lunch places (Chipotle, Firehouse Subs, King Soupers, Taco Bell, Subway, Panera, etc.)
- **Robust**: Uses merchant matching when transaction time is unavailable
- **Combined**: Both methods work together for maximum accuracy

**Returns**: Total lunch spending, merchant breakdown, transaction list with times

**Perfect for**: Tracking takeout lunch habits vs. making your own lunch!

### 5. Dividend Queries
**For**: Investors tracking dividend income

**Examples**:
- "What are my dividends?"
- "How much dividend income this year?"
- "Show dividend payouts"

**Returns**: Total dividends, breakdown by security, transaction list

### 6. Cash Flow Queries
**For**: Entrepreneurs and everyone tracking income vs expenses

**Examples**:
- "What's my cash flow?"
- "Income vs expenses this month"
- "How much money in vs out?"

**Returns**: Total income, total expenses, net cash flow, breakdowns

### 7. Investment Queries
**For**: Investors tracking portfolio

**Examples**:
- "What's my net worth?"
- "How did my portfolio perform?"
- "What's my allocation?"
- "Show my holdings"

**Returns**: Investment metrics, performance, allocation breakdown

## Time Range Parsing

The system automatically extracts time ranges from queries:

- **"last month"** → Last 30 days
- **"this month"** → From 1st of current month to today
- **"last 3 months"** → Last 90 days
- **"last year"** → Last 365 days
- **"this year"** → From January 1st to today
- **"last 30 days"** → Last 30 days
- **"yesterday"** → Yesterday only
- **"today"** → Today only

If no time range is specified, defaults are used:
- Income/Expenses: Current month
- Dividends: Last year
- Transactions: Last 30 days

## Optimization Features

### 1. Pattern Matching Order
Patterns are checked in order of specificity:
1. Most specific (category, merchant) → Checked first
2. Specific (dividends, cash flow) → Checked second
3. General (income, expenses) → Checked last

This prevents "beer" from matching "expenses" when you ask "beer spending".

### 2. Category Aliases
Common spending categories have multiple aliases:
- "beer" matches: beer, alcohol, bar, brewery, pub, liquor, wine, drinks
- "restaurants" matches: restaurant, dining, food, eat, cafe, coffee, lunch, dinner

### 3. Merchant Extraction
Merchant names are extracted from patterns like:
- "at [merchant]"
- "from [merchant]"
- "spending at [merchant]"

### 4. Amount Thresholds
You can filter by amount:
- "spent more than $100"
- "expenses over $50"
- "transactions less than $20"

## Use Cases by Persona

### Young Entrepreneur
**Focus**: Cash flow, income tracking, business expenses

**Example Queries**:
```bash
# Track revenue
python -m backend.app.api.cli ask "what's my income this month?"

# Monitor cash flow
python -m backend.app.api.cli ask "income vs expenses last quarter"

# Business expenses
python -m backend.app.api.cli ask "how much did I spend on office supplies?"

# Revenue trends
python -m backend.app.api.cli ask "monthly income last year"
```

### Investor (Dividends & Gains Focus)
**Focus**: Portfolio performance, dividend income, allocation

**Example Queries**:
```bash
# Dividend tracking
python -m backend.app.api.cli ask "what are my dividends this year?"

# Portfolio performance
python -m backend.app.api.cli ask "how did my portfolio perform last month?"

# Allocation
python -m backend.app.api.cli ask "what's my asset allocation?"

# Gains tracking
python -m backend.app.api.cli ask "how much did I make on investments?"
```

### Bachelor (Spending Tracking)
**Focus**: Category-specific spending, merchant tracking

**Example Queries**:
```bash
# Track specific categories
python -m backend.app.api.cli ask "how much did I spend on beer?"
python -m backend.app.api.cli ask "restaurant spending last month"
python -m backend.app.api.cli ask "gas expenses"

# Merchant tracking
python -m backend.app.api.cli ask "how much at bars?"
python -m backend.app.api.cli ask "spending at restaurants"

# Overall spending
python -m backend.app.api.cli ask "how much did I spend this month?"
python -m backend.app.api.cli ask "what are my top expense categories?"
```

## Advanced Features

### Account Filtering
Filter queries to specific accounts:
```bash
python -m backend.app.api.cli ask "income in account 'Checking'"
python -m backend.app.api.cli ask "expenses from savings account"
```

### Combining Filters
The system supports multiple filters:
```bash
# Category + time range
python -m backend.app.api.cli ask "beer spending last month"

# Merchant + time range
python -m backend.app.api.cli ask "Starbucks spending this year"

# Category + amount threshold
python -m backend.app.api.cli ask "restaurant spending over $100"
```

## Extending the System

### Adding New Categories

Edit `intent_router.py` and add to `CATEGORY_ALIASES`:

```python
CATEGORY_ALIASES = {
    "your_category": ["alias1", "alias2", "alias3"],
    # ... existing categories
}
```

### Adding New Intents

1. Add to `QueryIntent` enum in `intent_router.py`
2. Add patterns to `IntentRouter` class
3. Add handler method in `handlers.py`
4. Add CLI formatting in `cli.py`

### Improving Pattern Matching

Patterns use Python regex. To improve matching:
- Use word boundaries (`\b`) for exact matches
- Order patterns by specificity
- Test with various phrasings

## API Usage

The query system is also available via REST API:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "how much did I spend on beer?"}'
```

## Tips for Best Results

1. **Be specific**: "beer spending" is better than "spending"
2. **Use time ranges**: "last month" helps narrow results
3. **Try aliases**: "alcohol" works if "beer" doesn't match
4. **Check categories**: Use `expenses` command to see available categories
5. **Combine filters**: Use time + category for precise queries

## Troubleshooting

**Query not understood?**
- Check the suggestions shown in error message
- Try rephrasing with keywords from supported patterns
- Use more specific terms (category names, merchant names)

**Wrong category matched?**
- Categories are matched by aliases - check `CATEGORY_ALIASES` in code
- Try using the exact category name from your transactions

**Time range not working?**
- Use standard phrases: "last month", "this year", etc.
- Check the date format in your database

**No results?**
- Verify you have transactions in that time range
- Check that transactions are properly categorized
- Try a broader time range

---

**The natural query system is designed to be intuitive and flexible. Experiment with different phrasings to find what works best for your use case!**
