# AI-Powered Financial Analysis

The AI integration feature is the crown jewel of this financial analysis tool, enabling you to get personalized, actionable insights from your financial data using state-of-the-art Large Language Models (LLMs).

## Overview

Instead of just viewing raw numbers and charts, you can now have a conversation with your financial data. Ask questions in natural language and receive intelligent, context-aware responses that help you understand your spending patterns, identify savings opportunities, and make better financial decisions.

## Why This Feature is Powerful

### 1. **Intelligent Data Selection**
The system automatically selects only the relevant financial data based on your query intent, saving API costs and improving response quality:
- Ask about expenses → Only expense data is included
- Ask about income → Only income data is included
- Ask about net worth → Only asset/liability data is included
- Ask general questions → Comprehensive summary is included

### 2. **Multi-Provider Support**
Choose from 4 major LLM providers, each with different strengths:
- **OpenAI (GPT)**: Excellent for structured analysis and recommendations
- **Anthropic (Claude)**: Great for nuanced financial advice and reasoning
- **Google (Gemini)**: Fast and efficient for quick insights
- **Cohere**: Strong for data analysis and pattern recognition

### 3. **Easy Comparison**
Run the same query multiple times with different LLMs to compare perspectives and get diverse insights on the same financial question.

### 4. **Flexible Model Selection**
Specify exact models from any provider to balance cost, speed, and quality:
- Use `gpt-4o-mini` for quick, affordable queries
- Use `claude-3-5-sonnet` for deep analysis
- Use `gemini-1.5-flash` for fast responses

## Quick Start

### Basic Usage

```bash
# Simple query - system will auto-detect available providers
python -m backend.app ai "where can I focus on budgeting to make quick wins with savings?"

# If multiple providers detected, you'll see an interactive menu:
# 🤖 Multiple AI providers detected. Choose one:
#   1. OpenAI (env_var:OPENAI_API_KEY)
#   2. Google (env_var:GEMINI_API_KEY)
# Select provider (1-2): 
```

### Specify Provider and Model

```bash
# Use specific provider
python -m backend.app ai "analyze my spending patterns" --provider openai

# Use specific model
python -m backend.app ai "budgeting advice" --provider openai --model gpt-4o

# Use Google Gemini
python -m backend.app ai "quick spending overview" --provider google --model gemini-1.5-flash
```

### List Available Options

```bash
# See all detected providers and their sources
python -m backend.app ai --list-providers

# See available models for a provider
python -m backend.app ai --list-models --provider openai
python -m backend.app ai --list-models --provider google
```

## Setup

### 1. Install Provider Packages (Optional)

Only install the packages for providers you want to use:

```bash
# OpenAI
pip install openai

# Anthropic (Claude)
pip install anthropic

# Google (Gemini)
pip install google-generativeai

# Cohere
pip install cohere
```

### 2. Configure API Keys

The system automatically detects API keys from multiple sources (in order of priority):

#### Option A: Environment Variables (Recommended)
```bash
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIzaSy...
export ANTHROPIC_API_KEY=sk-ant-...
export COHERE_API_KEY=...
```

#### Option B: Project `.env` File
Create `.env` or `.env.local` in the project root:
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIzaSy...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...
```

#### Option C: Shell Configuration Files
Add to `~/.bashrc`, `~/.zshrc`, `~/.bashrc.local`, or `~/.zshrc.local`:
```bash
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIzaSy...
```

**Note:** The system detects commented keys too (e.g., `# export GEMINI_API_KEY=...`), so you can keep old keys commented for easy switching.

### 3. Verify Setup

```bash
# Check detected providers
python -m backend.app ai --list-providers
```

## Use Cases

### 1. Budgeting and Savings Analysis

**Query:**
```bash
python -m backend.app ai "where can I focus on budgeting to make quick wins with savings?"
```

**What it does:**
- Analyzes your expense categories
- Identifies high-spending areas
- Suggests specific, actionable ways to save
- Prioritizes recommendations by impact

**Example Response:**
- "Your restaurant spending ($130/month) could be reduced by meal prepping..."
- "Consider negotiating your bills ($519/month) - you might save 10-15%..."
- "Your grocery spending is reasonable, but buying in bulk could save $20-30/month..."

### 2. Spending Pattern Analysis

**Query:**
```bash
python -m backend.app ai "what are my biggest spending categories and how do they compare to last month?"
```

**What it does:**
- Compares current vs. previous period spending
- Identifies trends and anomalies
- Explains what's driving changes
- Provides context for unusual spending

### 3. Income Optimization

**Query:**
```bash
python -m backend.app ai "how can I optimize my income and identify additional revenue streams?"
```

**What it does:**
- Analyzes your current income sources
- Identifies gaps and opportunities
- Suggests side income ideas based on your spending patterns
- Provides actionable steps

### 4. Financial Health Check

**Query:**
```bash
python -m backend.app ai "give me a comprehensive financial health assessment"
```

**What it does:**
- Evaluates net worth trends
- Assesses cash flow health
- Reviews debt-to-income ratios
- Provides overall financial wellness score
- Suggests improvement areas

### 5. Goal-Based Planning

**Query:**
```bash
python -m backend.app ai "if I want to save $10,000 in 6 months, what changes should I make?"
```

**What it does:**
- Calculates required monthly savings
- Identifies where to cut expenses
- Suggests timeline adjustments if needed
- Provides step-by-step action plan

### 6. Category-Specific Deep Dives

**Query:**
```bash
python -m backend.app ai "analyze my restaurant spending - am I eating out too much?"
```

**What it does:**
- Breaks down restaurant spending by merchant
- Compares to grocery spending
- Calculates cost per meal
- Suggests meal prep strategies
- Provides health and financial trade-offs

### 7. Investment Portfolio Review

**Query:**
```bash
python -m backend.app ai "review my investment portfolio and suggest improvements"
```

**What it does:**
- Analyzes asset allocation
- Reviews performance vs. benchmarks
- Identifies diversification gaps
- Suggests rebalancing strategies

### 8. Tax Planning

**Query:**
```bash
python -m backend.app ai "what tax-deductible expenses am I missing?"
```

**What it does:**
- Reviews expense categories for tax implications
- Identifies potential deductions
- Suggests documentation strategies
- Provides year-end tax planning tips

## Advanced Features

### Intelligent Data Selection

The system automatically filters data based on your query:

| Query Intent | Data Included |
|-------------|---------------|
| "spending" / "expenses" | Expense transactions, categories, merchants, trends |
| "income" / "earnings" | Income transactions, paystubs, deposits, trends |
| "net worth" | Assets, liabilities, holdings, history |
| "cash flow" | Income, expenses, net flow, trends |
| "lunch" / "restaurants" | Restaurant transactions, time analysis, merchant breakdown |
| "budgeting" | Comprehensive: expenses, income, net worth, trends |
| General questions | Full financial summary |

### Full Data Export (Use with Caution)

For comprehensive analysis, you can include the entire database:

```bash
python -m backend.app ai "comprehensive financial analysis" --full-data
```

**Warning:** This sends all your financial data to the LLM, which:
- Increases API costs significantly
- May hit token limits
- Takes longer to process
- Only use when necessary for deep analysis

### Comparing LLM Responses

One of the unique features is comparing responses from different LLMs:

```bash
# First run with OpenAI
python -m backend.app ai "budgeting advice"
# Select: 1 (OpenAI)

# Second run with Google
python -m backend.app ai "budgeting advice"
# Select: 2 (Google)
```

Different LLMs provide different perspectives:
- **OpenAI**: Often more structured, actionable recommendations
- **Claude**: More nuanced, considers trade-offs
- **Gemini**: Faster, good for quick insights
- **Cohere**: Strong on data patterns and trends

## Available Models

### OpenAI Models
- `gpt-4o` - Most capable, latest model (best quality)
- `gpt-4o-mini` - Fast and affordable (recommended for most queries)
- `gpt-4-turbo` - High performance
- `gpt-4` - Previous generation
- `gpt-3.5-turbo` - Fast and cost-effective

### Anthropic Models
- `claude-3-5-sonnet-20241022` - Latest, most capable (recommended)
- `claude-3-opus-20240229` - Most powerful
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fast and efficient

### Google Models
- `gemini-1.5-pro` - Most capable, latest
- `gemini-1.5-flash` - Fast and efficient (recommended)
- `gemini-pro` - Previous generation
- `gemini-1.0-pro` - Legacy model

### Cohere Models
- `command-r-plus` - Most capable (recommended)
- `command-r` - High performance
- `command` - Balanced
- `command-light` - Fast and efficient
- `command-nightly` - Experimental

## Best Practices

### 1. Start with Specific Questions
Instead of "analyze my finances," try:
- "What are my top 3 spending categories this month?"
- "How much am I spending on restaurants vs. groceries?"
- "What's my average monthly savings rate?"

### 2. Use Appropriate Models
- Quick questions → `gpt-4o-mini` or `gemini-1.5-flash`
- Deep analysis → `gpt-4o` or `claude-3-5-sonnet`
- Budget planning → `claude-3-5-sonnet` (better reasoning)
- Pattern analysis → `command-r-plus` (strong on data)

### 3. Compare Perspectives
Run important queries with 2-3 different LLMs to get diverse insights.

### 4. Iterate on Questions
Start broad, then get specific:
1. "What are my spending patterns?"
2. "Why is my restaurant spending so high?"
3. "How can I reduce restaurant spending by 30%?"

### 5. Use Time Ranges
The system understands time references:
- "spending this month"
- "income last quarter"
- "expenses over the past 3 months"

## Cost Management

### API Costs
Different providers and models have different costs:

**Most Affordable:**
- `gpt-4o-mini` (~$0.15 per 1M input tokens)
- `gemini-1.5-flash` (~$0.075 per 1M input tokens)
- `claude-3-haiku` (~$0.25 per 1M input tokens)

**Balanced:**
- `gpt-4o` (~$2.50 per 1M input tokens)
- `claude-3-5-sonnet` (~$3.00 per 1M input tokens)
- `gemini-1.5-pro` (~$1.25 per 1M input tokens)

**Premium:**
- `gpt-4-turbo` (~$10 per 1M input tokens)
- `claude-3-opus` (~$15 per 1M input tokens)

### Reducing Costs

1. **Use intelligent data selection** (default) - only relevant data is sent
2. **Use smaller models** for routine queries
3. **Avoid `--full-data`** unless necessary
4. **Be specific** in queries to reduce context needed

## Privacy and Security

### Data Handling
- API keys are never logged or stored
- Financial data is only sent to LLM APIs you explicitly choose
- No data is stored by LLM providers beyond the API call
- All communication is encrypted (HTTPS)

### Best Practices
- Review API key permissions regularly
- Use separate API keys for different projects
- Monitor API usage in provider dashboards
- Don't share API keys in code or documentation

## Troubleshooting

### "No AI providers found"
**Solution:** Add API keys to `.env`, environment variables, or shell config files.

### "Invalid API key"
**Solution:** 
- Verify key is correct
- Check key hasn't expired
- Ensure key has proper permissions
- Try a different source (env var vs. config file)

### "Model not found"
**Solution:**
- Check model name spelling
- Verify model is available for your API key tier
- Use `--list-models` to see available options

### Wrong provider selected
**Solution:**
- Use `--provider` flag to explicitly specify
- Check `--list-providers` to see detected keys
- Verify API keys are in correct variables

### Poor quality responses
**Solution:**
- Try a different model (e.g., `gpt-4o` instead of `gpt-4o-mini`)
- Be more specific in your query
- Use `--full-data` for comprehensive analysis
- Try a different provider (Claude vs. OpenAI)

## Examples

### Example 1: Monthly Budget Review

```bash
$ python -m backend.app ai "review my spending this month and suggest a budget for next month"

🤖 Querying OpenAI...
Query: review my spending this month and suggest a budget for next month

╭──────────────────────────── AI Response (OpenAI) ────────────────────────────╮
│ Based on your spending in January 2026, here's a comprehensive budget      │
│ review and recommendations:                                                  │
│                                                                              │
│ Current Month Spending:                                                      │
│ • Total: $947.19                                                            │
│ • Bills: $519.38 (55% of spending)                                          │
│ • Groceries: $195.03 (21% of spending)                                      │
│ • Restaurants: $130.67 (14% of spending)                                    │
│                                                                              │
│ Recommended Budget for February:                                            │
│ • Bills: $500 (negotiate to reduce by ~$20)                                 │
│ • Groceries: $180 (buy in bulk, meal prep)                                 │
│ • Restaurants: $100 (reduce by 23%)                                         │
│ • Total: $780 (18% reduction)                                               │
│                                                                              │
│ Quick Wins:                                                                  │
│ 1. Review recurring bills - potential $20-30/month savings                │
│ 2. Meal prep 2x/week to reduce restaurant spending                          │
│ 3. Buy groceries in bulk for non-perishables                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Example 2: Savings Goal Planning

```bash
$ python -m backend.app ai "I want to save $5,000 in 6 months. Is this realistic and how should I do it?"

🤖 Querying Claude...
Query: I want to save $5,000 in 6 months. Is this realistic and how should I do it?

╭──────────────────────────── AI Response (Claude) ────────────────────────────╮
│ Based on your current financial situation:                                  │
│                                                                              │
│ Feasibility Analysis:                                                        │
│ • Required monthly savings: $833.33                                          │
│ • Current monthly income: ~$2,400 (based on recent data)                    │
│ • Current monthly expenses: ~$1,050                                          │
│ • Current savings capacity: ~$1,350/month                                  │
│                                                                              │
│ ✅ This goal is realistic! You have sufficient income.                     │
│                                                                              │
│ Action Plan:                                                                 │
│ 1. Set up automatic transfer of $850/month to savings                      │
│ 2. Reduce restaurant spending by $50/month (meal prep)                      │
│ 3. Negotiate bills to save $30/month                                        │
│ 4. Track progress monthly with this tool                                    │
│                                                                              │
│ Timeline:                                                                    │
│ • Month 1-2: Establish habits, save $850/month                             │
│ • Month 3-4: Optimize spending, save $900/month                            │
│ • Month 5-6: Final push, save $950/month                                    │
│                                                                              │
│ You'll reach $5,000 in ~5.5 months at this rate!                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Integration with Other Features

The AI integration works seamlessly with other tool features:

- **Natural Language Queries**: Use the same query system (`ask` command) for quick answers, then use `ai` for deep analysis
- **Data Export**: Export data first, then use it for offline analysis or with other AI tools
- **Dashboard**: Review visual data, then ask AI for insights on specific patterns
- **Smart Detection**: Lunch detection, income detection, etc. all feed into AI analysis

## Future Enhancements

Planned improvements:
- Conversation memory (follow-up questions)
- Custom prompts and templates
- Batch analysis (multiple queries at once)
- Report generation (PDF/HTML output)
- Integration with local LLMs (Ollama, etc.)

## Support

For issues or questions:
1. Check this documentation
2. Review `README.md` for general setup
3. Check provider-specific documentation
4. Review API key detection with `--list-providers`

---

**The AI integration transforms your financial data from numbers into actionable insights. Start asking questions and discover what your finances are telling you!**
