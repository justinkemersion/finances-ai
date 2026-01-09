# Export Guide - Using Your Financial Data with LLMs

This guide explains how to export your financial data and use it with ChatGPT, Claude, or other LLMs for analysis and insights.

## Quick Start

### 1. Export Your Data

```bash
# Export everything
python -m backend.app.api.cli export

# Export specific time period
python -m backend.app.api.cli export --start-date 2024-01-01 --end-date 2024-12-31

# Export only expenses
python -m backend.app.api.cli export --transaction-type expense --no-holdings --no-net-worth
```

### 2. Upload to LLM

**ChatGPT:**
1. Go to chat.openai.com
2. Click the paperclip icon (📎) or drag and drop the JSON file
3. Ask questions like:
   - "Analyze my spending patterns"
   - "What are my top expense categories?"
   - "How has my net worth changed over time?"

**Claude (Anthropic):**
1. Go to claude.ai
2. Click the attachment icon or drag and drop the JSON file
3. Ask similar questions about your finances

## Export Options

### Basic Exports

```bash
# Full database export
python -m backend.app.api.cli export --output full_export.json

# Last 3 months only
python -m backend.app.api.cli export --start-date 2024-10-01 --output last_quarter.json

# Specific account only
python -m backend.app.api.cli export --account-id <account_id> --output account_only.json
```

### Selective Exports

```bash
# Only transactions (no holdings, no net worth)
python -m backend.app.api.cli export --no-holdings --no-net-worth --output transactions.json

# Only investment data
python -m backend.app.api.cli export --no-banking-txns --output investments.json

# Only banking/expense data
python -m backend.app.api.cli export --no-investment-txns --output expenses.json

# Only summary statistics (quick overview)
python -m backend.app.api.cli export --no-accounts --no-holdings --no-transactions --no-net-worth --output summary.json
```

### Filtered Exports

```bash
# Only expenses
python -m backend.app.api.cli export --transaction-type expense

# Only income
python -m backend.app.api.cli export --transaction-type income

# Exclude pending transactions
python -m backend.app.api.cli export --no-pending
```

## JSON Structure

The exported JSON file has the following structure:

```json
{
  "metadata": {
    "export_date": "2024-01-09T08:30:27",
    "export_version": "1.0",
    "filters": { ... }
  },
  "summary": {
    "net_worth": { ... },
    "income": { ... },
    "expenses": { ... },
    "portfolio": { ... }
  },
  "accounts": [ ... ],
  "holdings": [ ... ],
  "transactions": [ ... ],
  "net_worth_snapshots": [ ... ]
}
```

### Summary Section

The `summary` section provides a quick overview perfect for LLM context:
- Net worth breakdown
- Income totals by type
- Top expense categories
- Portfolio allocation

### Transactions

Each transaction includes:
- Date and amount
- Merchant/location information
- Categories (primary and detailed)
- Income/expense classification
- Tags and notes (if any)

## Example LLM Prompts

Once you've uploaded your export file, try these prompts:

### Spending Analysis
```
"Analyze my spending patterns. What are my top expense categories? 
Are there any unusual spending patterns I should be aware of?"
```

### Income Tracking
```
"Review my income over the past year. How consistent is it? 
What are the main sources of income?"
```

### Budget Planning
```
"Based on my spending history, help me create a monthly budget. 
What categories should I focus on reducing?"
```

### Financial Health
```
"Assess my overall financial health. What are my strengths and 
areas for improvement based on this data?"
```

### Investment Analysis
```
"Analyze my investment portfolio. What's my asset allocation? 
Are there any diversification concerns?"
```

### Trend Analysis
```
"Show me trends in my net worth over time. What factors are 
driving changes?"
```

## Privacy Considerations

⚠️ **Important:** The exported JSON file contains your financial data. 

- **Never commit** export files to git (they're in `.gitignore`)
- **Delete** export files after use if they contain sensitive data
- **Be cautious** when uploading to LLMs - they may use your data for training
- Consider using **local LLMs** (Ollama, LM Studio) for maximum privacy

## Tips for Better LLM Analysis

1. **Use summary exports** for quick questions - they're smaller and faster
2. **Export specific time periods** for focused analysis
3. **Include context** in your prompts - mention the time period, account types, etc.
4. **Ask follow-up questions** - LLMs can reference the uploaded data in conversation
5. **Use structured prompts** - Be specific about what you want analyzed

## File Size Considerations

- **Full exports** can be large (100KB+)
- **Summary-only exports** are much smaller (~5KB)
- **Date-filtered exports** reduce file size significantly
- Most LLMs have file size limits (ChatGPT: ~512MB, Claude: varies)

If your export is too large:
- Use date filters to reduce scope
- Export only specific data types (e.g., just transactions)
- Use the summary export for overview questions

## Troubleshooting

**Export fails:**
- Check that the database exists and is initialized
- Ensure you have write permissions for the output directory

**LLM can't read the file:**
- Verify the JSON is valid (try opening it in a text editor)
- Check file size limits
- Try exporting a smaller subset

**Missing data:**
- Check your filters - you might have excluded the data you need
- Verify your sync has run and populated the database

---

**Remember:** You control your data. Export only what you need, and delete exports when done.
