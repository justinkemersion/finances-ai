"""Inject realistic test data for testing natural language queries"""

import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Account, Transaction


# Realistic test data templates
BEER_MERCHANTS = [
    "Local Bar & Grill", "The Pub", "Brewery Taproom", "Sports Bar", 
    "Craft Beer House", "Dive Bar", "Wine Bar", "Liquor Store"
]

RESTAURANT_MERCHANTS = [
    "Starbucks", "McDonald's", "Chipotle", "Olive Garden", "Pizza Hut",
    "Taco Bell", "Subway", "Burger King", "Local Diner", "Sushi Place",
    "Italian Restaurant", "Mexican Restaurant", "Thai Restaurant"
]

GAS_STATIONS = [
    "Shell", "Exxon", "BP", "Chevron", "7-Eleven", "Costco Gas",
    "Wawa", "Sheetz", "Speedway"
]

GROCERY_STORES = [
    "Walmart", "Target", "Whole Foods", "Kroger", "Safeway", "Trader Joe's",
    "Aldi", "Costco", "Publix", "Giant Eagle"
]

BILL_MERCHANTS = [
    "Electric Company", "Water Department", "Internet Provider", 
    "Phone Company", "Cable Company", "Gas Utility"
]

ENTERTAINMENT_MERCHANTS = [
    "Netflix", "Spotify", "Movie Theater", "Concert Venue", "Amazon Prime",
    "Disney+", "HBO Max", "Steam", "PlayStation Store"
]

SHOPPING_MERCHANTS = [
    "Amazon", "eBay", "Best Buy", "Home Depot", "Lowe's", "Macy's",
    "Nike", "Adidas", "Apple Store"
]

TRANSPORT_MERCHANTS = [
    "Uber", "Lyft", "Taxi Service", "Public Transit", "Parking Garage",
    "Toll Road", "Gas Station"  # Gas also counts as transport
]


def create_test_transaction(
    db: Session,
    account: Account,
    date: date,
    name: str,
    amount: Decimal,
    merchant_name: str = None,
    expense_category: str = None,
    primary_category: str = None,
    detailed_category: str = None,
    is_expense: bool = True,
    is_income: bool = False,
    is_deposit: bool = False,
    is_paystub: bool = False,
    income_type: str = None
) -> Transaction:
    """Create a test transaction"""
    transaction_id = f"test_{random.randint(100000, 999999)}_{int(datetime.now().timestamp())}"
    
    txn = Transaction(
        id=transaction_id,
        account_id=account.id,
        date=date,
        transaction_datetime=datetime.combine(date, datetime.min.time()),
        name=name,
        amount=amount,
        currency_code="USD",
        iso_currency_code="USD",
        type="expense" if is_expense else ("income" if is_income else "deposit"),
        merchant_name=merchant_name,
        expense_category=expense_category,
        primary_category=primary_category,
        detailed_category=detailed_category,
        is_expense=is_expense,
        is_income=is_income,
        is_deposit=is_deposit,
        is_paystub=is_paystub,
        income_type=income_type,
        is_pending=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(txn)
    return txn


def inject_beer_transactions(db: Session, account: Account, start_date: date, end_date: date, count: int = 15):
    """Inject beer/alcohol spending transactions"""
    current_date = start_date
    transactions = []
    
    for _ in range(count):
        if current_date > end_date:
            break
        
        merchant = random.choice(BEER_MERCHANTS)
        amount = Decimal(random.uniform(15, 75)).quantize(Decimal('0.01'))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name=f"{merchant} - Beer/Alcohol",
            amount=-amount,  # Negative for expenses
            merchant_name=merchant,
            expense_category="beer",
            primary_category="FOOD_AND_DRINK",
            detailed_category="FOOD_AND_DRINK_ALCOHOL",
            is_expense=True
        )
        transactions.append(txn)
        
        # Move to next date (random interval, but mostly weekends)
        days_offset = random.choice([1, 1, 1, 2, 2, 3, 4, 5, 6, 7])  # Bias towards weekends
        current_date += timedelta(days=days_offset)
    
    return transactions


def inject_restaurant_transactions(db: Session, account: Account, start_date: date, end_date: date, count: int = 25):
    """Inject restaurant/dining transactions"""
    current_date = start_date
    transactions = []
    
    # Lunch merchants (for lunch detection)
    lunch_merchants = ["Chipotle", "Firehouse Subs", "King Soupers", "Taco Bell", "Subway", "Panera"]
    # Dinner/other restaurants
    other_merchants = [m for m in RESTAURANT_MERCHANTS if m not in lunch_merchants]
    
    lunch_count = int(count * 0.6)  # 60% lunch, 40% other
    other_count = count - lunch_count
    
    # Generate lunch transactions (11am-2pm)
    for _ in range(lunch_count):
        if current_date > end_date:
            break
        
        merchant = random.choice(lunch_merchants)
        amount = Decimal(random.uniform(8, 18)).quantize(Decimal('0.01'))  # Lunch is typically cheaper
        
        # Random time between 11am-2pm
        lunch_hour = random.randint(11, 14)
        lunch_minute = random.randint(0, 59)
        transaction_time = datetime.combine(current_date, datetime.min.time().replace(hour=lunch_hour, minute=lunch_minute))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name=f"{merchant} - Lunch",
            amount=-amount,
            merchant_name=merchant,
            expense_category="restaurants",
            primary_category="FOOD_AND_DRINK",
            detailed_category="FOOD_AND_DRINK_RESTAURANTS",
            is_expense=True
        )
        txn.transaction_datetime = transaction_time
        transactions.append(txn)
        
        days_offset = random.choice([1, 1, 1, 2, 2, 3])  # Lunch is more frequent
        current_date += timedelta(days=days_offset)
    
    # Generate dinner/other restaurant transactions (evening times)
    for _ in range(other_count):
        if current_date > end_date:
            break
        
        merchant = random.choice(other_merchants)
        amount = Decimal(random.uniform(15, 45)).quantize(Decimal('0.01'))
        
        # Random time between 5pm-9pm (dinner)
        dinner_hour = random.randint(17, 21)
        dinner_minute = random.randint(0, 59)
        transaction_time = datetime.combine(current_date, datetime.min.time().replace(hour=dinner_hour, minute=dinner_minute))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name=f"{merchant} - Dining",
            amount=-amount,
            merchant_name=merchant,
            expense_category="restaurants",
            primary_category="FOOD_AND_DRINK",
            detailed_category="FOOD_AND_DRINK_RESTAURANTS",
            is_expense=True
        )
        txn.transaction_datetime = transaction_time
        transactions.append(txn)
        
        days_offset = random.choice([2, 3, 4, 5, 6, 7])
        current_date += timedelta(days=days_offset)
    
    return transactions


def inject_gas_transactions(db: Session, account: Account, start_date: date, end_date: date, count: int = 8):
    """Inject gas/fuel transactions"""
    current_date = start_date
    transactions = []
    
    for _ in range(count):
        if current_date > end_date:
            break
        
        merchant = random.choice(GAS_STATIONS)
        amount = Decimal(random.uniform(30, 65)).quantize(Decimal('0.01'))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name=f"{merchant} - Gas",
            amount=-amount,
            merchant_name=merchant,
            expense_category="gas",
            primary_category="GENERAL_MERCHANDISE",
            detailed_category="GENERAL_MERCHANDISE_GAS_STATIONS",
            is_expense=True
        )
        transactions.append(txn)
        
        days_offset = random.choice([3, 4, 5, 6, 7, 8, 9, 10, 14])
        current_date += timedelta(days=days_offset)
    
    return transactions


def inject_grocery_transactions(db: Session, account: Account, start_date: date, end_date: date, count: int = 12):
    """Inject grocery transactions"""
    current_date = start_date
    transactions = []
    
    for _ in range(count):
        if current_date > end_date:
            break
        
        merchant = random.choice(GROCERY_STORES)
        amount = Decimal(random.uniform(45, 150)).quantize(Decimal('0.01'))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name=f"{merchant} - Groceries",
            amount=-amount,
            merchant_name=merchant,
            expense_category="groceries",
            primary_category="FOOD_AND_DRINK",
            detailed_category="FOOD_AND_DRINK_GROCERIES",
            is_expense=True
        )
        transactions.append(txn)
        
        days_offset = random.choice([3, 4, 5, 6, 7])
        current_date += timedelta(days=days_offset)
    
    return transactions


def inject_bill_transactions(db: Session, account: Account, start_date: date, end_date: date):
    """Inject monthly bill transactions"""
    transactions = []
    current_date = start_date.replace(day=1)  # Start of month
    
    while current_date <= end_date:
        # Electric bill
        txn1 = create_test_transaction(
            db=db,
            account=account,
            date=current_date + timedelta(days=2),
            name="Electric Company - Monthly Bill",
            amount=-Decimal(random.uniform(80, 150)).quantize(Decimal('0.01')),
            merchant_name="Electric Company",
            expense_category="bills",
            primary_category="GENERAL_SERVICES",
            detailed_category="GENERAL_SERVICES_UTILITIES_ELECTRIC",
            is_expense=True
        )
        transactions.append(txn1)
        
        # Internet bill
        txn2 = create_test_transaction(
            db=db,
            account=account,
            date=current_date + timedelta(days=5),
            name="Internet Provider - Monthly Service",
            amount=-Decimal(random.uniform(50, 80)).quantize(Decimal('0.01')),
            merchant_name="Internet Provider",
            expense_category="bills",
            primary_category="GENERAL_SERVICES",
            detailed_category="GENERAL_SERVICES_INTERNET",
            is_expense=True
        )
        transactions.append(txn2)
        
        # Phone bill
        txn3 = create_test_transaction(
            db=db,
            account=account,
            date=current_date + timedelta(days=8),
            name="Phone Company - Monthly Plan",
            amount=-Decimal(random.uniform(60, 100)).quantize(Decimal('0.01')),
            merchant_name="Phone Company",
            expense_category="bills",
            primary_category="GENERAL_SERVICES",
            detailed_category="GENERAL_SERVICES_TELECOM",
            is_expense=True
        )
        transactions.append(txn3)
        
        # Move to next month
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    return transactions


def inject_income_transactions(db: Session, account: Account, start_date: date, end_date: date):
    """Inject income/paystub transactions"""
    transactions = []
    current_date = start_date
    
    # Bi-weekly paychecks
    while current_date <= end_date:
        amount = Decimal(random.uniform(2000, 3500)).quantize(Decimal('0.01'))
        
        txn = create_test_transaction(
            db=db,
            account=account,
            date=current_date,
            name="Employer - Payroll Deposit",
            amount=amount,
            merchant_name="Employer",
            expense_category=None,
            primary_category="INCOME",
            detailed_category="INCOME_WAGES",
            is_expense=False,
            is_income=True,
            is_deposit=True,
            is_paystub=True,
            income_type="salary"
        )
        transactions.append(txn)
        
        # Next paycheck in 14 days
        current_date += timedelta(days=14)
    
    return transactions


def inject_test_data(
    db: Session,
    account_id: str = None,
    months_back: int = 3,
    include_income: bool = True
):
    """
    Inject comprehensive test data for testing natural language queries
    
    Args:
        db: Database session
        account_id: Account ID to use (creates one if not provided)
        months_back: How many months of data to generate
        include_income: Whether to include income transactions
    """
    # Get or create account
    if account_id:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError(f"Account {account_id} not found")
    else:
        # Find first active account or create a test one
        account = db.query(Account).filter(Account.is_active == True).first()
        if not account:
            # Create a test account
            account = Account(
                id="test_checking_account",
                item_id="test_item",
                name="Test Checking Account",
                type="depository",
                subtype="checking",
                institution_id="test_institution",
                is_active=True
            )
            db.add(account)
            db.flush()
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=months_back * 30)
    
    print(f"Injecting test data for account: {account.name}")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    all_transactions = []
    
    # Income
    if include_income:
        print("Generating income transactions...")
        income_txns = inject_income_transactions(db, account, start_date, end_date)
        all_transactions.extend(income_txns)
        print(f"  Created {len(income_txns)} income transactions")
    
    # Beer/alcohol
    print("Generating beer/alcohol transactions...")
    beer_txns = inject_beer_transactions(db, account, start_date, end_date)
    all_transactions.extend(beer_txns)
    print(f"  Created {len(beer_txns)} beer transactions")
    
    # Restaurants
    print("Generating restaurant transactions...")
    restaurant_txns = inject_restaurant_transactions(db, account, start_date, end_date)
    all_transactions.extend(restaurant_txns)
    print(f"  Created {len(restaurant_txns)} restaurant transactions")
    
    # Gas
    print("Generating gas transactions...")
    gas_txns = inject_gas_transactions(db, account, start_date, end_date)
    all_transactions.extend(gas_txns)
    print(f"  Created {len(gas_txns)} gas transactions")
    
    # Groceries
    print("Generating grocery transactions...")
    grocery_txns = inject_grocery_transactions(db, account, start_date, end_date)
    all_transactions.extend(grocery_txns)
    print(f"  Created {len(grocery_txns)} grocery transactions")
    
    # Bills
    print("Generating bill transactions...")
    bill_txns = inject_bill_transactions(db, account, start_date, end_date)
    all_transactions.extend(bill_txns)
    print(f"  Created {len(bill_txns)} bill transactions")
    
    # Commit all transactions
    db.commit()
    
    print()
    print(f"✓ Successfully created {len(all_transactions)} test transactions")
    print()
    print("You can now test queries like:")
    print("  python -m backend.app ask 'how much did I spend on beer?'")
    print("  python -m backend.app ask 'restaurant spending last month'")
    print("  python -m backend.app ask 'what's my income?'")
    print("  python -m backend.app ask 'how much at Starbucks?'")
    
    return all_transactions


if __name__ == "__main__":
    db = SessionLocal()
    try:
        inject_test_data(db, months_back=3, include_income=True)
    finally:
        db.close()
