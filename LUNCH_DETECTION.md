# Smart Lunch Detection System

The lunch detection system uses a multi-factor confidence scoring approach to accurately identify lunch transactions while handling edge cases.

## How It Works

### Confidence Scoring (0-100%)

Each transaction is scored based on multiple factors:

#### Time-Based Scoring
- **+30 points**: Transaction between 11am-2pm (lunch hours)
- **+10 points**: Transaction between 8-10am or 3-4pm (near lunch hours)
- **-20 points**: Transaction outside lunch hours

#### Merchant-Based Scoring
- **+40 points**: Known lunch merchant (Chipotle, Firehouse Subs, Taco Bell, etc.)
- **+20 points**: Grocery store with small amount (≤$15) - likely lunch counter
- **+25 points**: Gas station with small amount (≤$15) - likely food purchase
- **-10 points**: Unknown merchant type

#### Amount-Based Scoring
- **+15 points**: Typical lunch amount (≤$20)
- **+5 points**: Moderate amount ($20-25)
- **-30 points**: Large amount (>$25) - unlikely to be lunch

#### Category-Based Scoring
- **+10 points**: Restaurant/food category
- **-20 points**: Large grocery purchase (excluded)

### Thresholds

- **≥60% confidence**: Included as lunch transaction
- **40-59% confidence**: Flagged as "uncertain" (shown separately)
- **<40% confidence**: Excluded from lunch totals

## Edge Case Handling

### 1. Grocery Store Purchases

**Problem**: Grocery stores like King Soupers, Albertsons, Safeway can be either:
- Full grocery shopping trips ($45-150)
- Quick lunch runs at the deli counter ($8-15)

**Solution**:
- **Amount threshold**: Only includes grocery store transactions ≤$15
- **Time bonus**: If during lunch hours, higher confidence
- **Exclusion**: Large grocery purchases automatically excluded

**Example**:
- King Soupers, $12.43 @ 12:48 → **100% confidence** (lunch)
- King Soupers, $87.50 @ 12:30 → **Excluded** (full shopping)

### 2. Gas Station Purchases

**Problem**: Gas stations can be either:
- Gas fill-ups ($30-65)
- Quick food/snacks ($5-15)

**Solution**:
- **Amount threshold**: Only includes gas station transactions ≤$15
- **Time bonus**: If during lunch hours, higher confidence
- **Exclusion**: Large gas purchases automatically excluded

**Example**:
- Sheetz, $10.31 @ 14:55 → **100% confidence** (lunch food)
- Shell, $45.20 @ 13:00 → **Excluded** (gas fill-up)

### 3. Non-Standard Work Schedules

**Problem**: You don't work M-F, so lunch could be any day.

**Solution**:
- **Time-based detection**: Works for any day of the week
- **Merchant matching**: Falls back to merchant recognition when time unavailable
- **Flexible**: No day-of-week restrictions

## Confidence Reasons

Each transaction shows why it received its confidence score:

**High Confidence (100%)**:
- "Lunch time (12:48), Known lunch merchant, Typical lunch amount ($12.43)"

**Medium Confidence (85%)**:
- "No time data available, Known lunch merchant, Typical lunch amount ($24.37)"

**Low Confidence (50%)**:
- "Outside lunch hours (20:02), Known lunch merchant, Large amount ($44.53) - unlikely to be lunch"

## Output Format

```
Lunch Spending
  Total: $571.29
  Transactions: 44

⚠ 26 uncertain transactions ($685.62)
These may be lunch but have lower confidence scores

By Merchant:
  Subway: $126.16 (9 transactions) (confidence: 98.9%)
  Taco Bell: $97.02 (6 transactions) (confidence: 94.2%)
  King Soupers: $41.48 (4 transactions) (confidence: 100.0%)
  Safeway: $22.08 (2 transactions) (confidence: 100.0%)
  Sheetz: $16.08 (2 transactions) (confidence: 100.0%)

Recent Lunch Transactions:
  2025-12-31T00:00:00 @ 14:57 - Albertsons: $10.46 [100%]
  2025-12-28T00:00:00 @ 12:41 - King Soupers: $10.27 [100%]
  2025-12-27T00:00:00 @ 11:37 - Safeway: $13.69 [100%]
  2025-12-21T00:00:00 @ 14:55 - Sheetz: $10.31 [100%]

Uncertain Transactions (may not be lunch):
  2026-01-04T00:00:00 @ 20:02 - McDonald's: $44.53 [50%]
    → Outside lunch hours (20:02), Known lunch merchant, Large amount ($44.53) - unlikely to be lunch
```

## Customization

### Adjusting Thresholds

Edit `backend/app/queries/intent_router.py`:

```python
LUNCH_MAX_AMOUNT = 20.0  # Typical lunch is under $20
GROCERY_LUNCH_THRESHOLD = 15.0  # Grocery store purchases > $15 are likely not lunch
GAS_FOOD_THRESHOLD = 15.0  # Gas station purchases > $15 are likely gas, not food
```

### Adding Lunch Merchants

Edit `LUNCH_MERCHANTS` list in `intent_router.py`:

```python
LUNCH_MERCHANTS = [
    "chipotle", "firehouse", "taco bell", "subway",
    "your_custom_merchant",  # Add here
]
```

### Adding Grocery Stores

Edit `GROCERY_STORES` list in `intent_router.py`:

```python
GROCERY_STORES = [
    "king soupers", "albertsons", "safeway",
    "your_grocery_store",  # Add here
]
```

## Why This Approach?

1. **Transparent**: You can see exactly why each transaction was included/excluded
2. **Flexible**: Handles edge cases without hard rules
3. **Accurate**: Multi-factor scoring reduces false positives/negatives
4. **Customizable**: Easy to adjust thresholds for your spending patterns
5. **Robust**: Works even when transaction time data is missing

## Future Enhancements

Potential improvements:
- Machine learning model trained on your historical data
- User feedback loop (mark transactions as lunch/not lunch)
- Recurring pattern detection (same merchant, same time = higher confidence)
- Location-based detection (if you have location data)
- Category learning (learn which categories you typically use for lunch)

---

**The system is designed to be conservative - it's better to exclude uncertain transactions than to inflate your lunch spending numbers. The confidence scores give you full transparency into the decision-making process.**
