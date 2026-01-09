"""Generate HTML dashboard from database"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models import Account, Holding, Transaction, NetWorthSnapshot
from ..analytics import NetWorthAnalyzer, IncomeAnalyzer, AllocationAnalyzer, ExpenseAnalyzer


def generate_dashboard_html() -> str:
    """Generate HTML dashboard with current financial data"""
    
    db = SessionLocal()
    
    try:
        # Get net worth
        net_worth_data = NetWorthAnalyzer.calculate_current_net_worth(db)
        
        # Get income summary
        income_summary = IncomeAnalyzer.calculate_income_summary(db)
        
        # Get allocation
        allocation = AllocationAnalyzer.calculate_allocation(db)
        
        # Get accounts
        accounts = db.query(Account).filter(Account.is_active == True).all()
        
        # Get transaction categories
        txn_categories = db.query(
            Transaction.type,
            Transaction.subtype,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).group_by(Transaction.type, Transaction.subtype).all()
        
        # Get recent transactions
        recent_txns = db.query(Transaction).order_by(Transaction.date.desc()).limit(20).all()
        
        # Get income transactions
        income_txns = db.query(Transaction).filter(
            Transaction.is_income == True
        ).order_by(Transaction.date.desc()).limit(10).all()
        
        # Get holdings
        holdings = db.query(Holding).order_by(Holding.value.desc()).limit(15).all()
        
        # Transaction type summary
        txn_type_summary = db.query(
            Transaction.type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).group_by(Transaction.type).all()
        
        # Income by type
        income_by_type = db.query(
            Transaction.income_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_income == True
        ).group_by(Transaction.income_type).all()
        
    finally:
        db.close()
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance AI Analyzer - Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #666;
            font-weight: 500;
        }}
        
        .metric-value {{
            color: #333;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .metric-value.positive {{
            color: #10b981;
        }}
        
        .metric-value.negative {{
            color: #ef4444;
        }}
        
        .table-container {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #667eea;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.income {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge.deposit {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .badge.expense {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        .timestamp {{
            text-align: center;
            color: #999;
            margin-top: 30px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Finance AI Analyzer</h1>
            <p>Privacy-first Personal Finance Dashboard</p>
        </div>
        
        <div class="grid">
            <!-- Net Worth Card -->
            <div class="card">
                <h2>📈 Net Worth</h2>
                <div class="metric">
                    <span class="metric-label">Total Assets</span>
                    <span class="metric-value">${net_worth_data['total_assets']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Liabilities</span>
                    <span class="metric-value">${net_worth_data['total_liabilities']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Net Worth</span>
                    <span class="metric-value {'positive' if net_worth_data['net_worth'] >= 0 else 'negative'}">${net_worth_data['net_worth']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Investment Value</span>
                    <span class="metric-value">${net_worth_data['investment_value']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cash Value</span>
                    <span class="metric-value">${net_worth_data['cash_value']:,.2f}</span>
                </div>
            </div>
            
            <!-- Income Card -->
            <div class="card">
                <h2>💵 Income Summary</h2>
                <div class="metric">
                    <span class="metric-label">Total Income</span>
                    <span class="metric-value {'positive' if income_summary['total_income'] >= 0 else 'negative'}">${income_summary['total_income']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Paystubs</span>
                    <span class="metric-value">{income_summary['paystub_count']} (${income_summary['paystub_total']:,.2f})</span>
                </div>
                {''.join([f'''
                <div class="metric">
                    <span class="metric-label">{item['type'].title() if item['type'] else 'Unknown'}</span>
                    <span class="metric-value">{item['count']} transactions (${item['total']:,.2f})</span>
                </div>''' for item in income_summary['by_type']])}
            </div>
            
            <!-- Portfolio Value Card -->
            <div class="card">
                <h2>💼 Portfolio</h2>
                <div class="metric">
                    <span class="metric-label">Total Value</span>
                    <span class="metric-value">${allocation['total_value']:,.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Accounts</span>
                    <span class="metric-value">{len(accounts)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Holdings</span>
                    <span class="metric-value">{len(allocation['by_security'])}</span>
                </div>
            </div>
        </div>
        
        <!-- Transaction Categories -->
        <div class="card full-width">
            <h2>📊 Transaction Categories</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Subtype</th>
                            <th>Count</th>
                            <th>Total Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td><strong>{cat[0]}</strong></td>
                            <td>{cat[1] or 'N/A'}</td>
                            <td>{cat[2]}</td>
                            <td class="{'positive' if (cat[3] or 0) >= 0 else 'negative'}">${float(cat[3] or 0):,.2f}</td>
                        </tr>''' for cat in sorted(txn_categories, key=lambda x: abs(x[3] or 0), reverse=True)])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Transaction Types Summary -->
        <div class="card full-width">
            <h2>💰 Transaction Types Summary</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Count</th>
                            <th>Total Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td><strong>{txn_type[0]}</strong></td>
                            <td>{txn_type[1]}</td>
                            <td class="{'positive' if (txn_type[2] or 0) >= 0 else 'negative'}">${float(txn_type[2] or 0):,.2f}</td>
                        </tr>''' for txn_type in sorted(txn_type_summary, key=lambda x: abs(x[2] or 0), reverse=True)])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Top Holdings -->
        <div class="card full-width">
            <h2>🏆 Top Holdings</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Name</th>
                            <th>Quantity</th>
                            <th>Value</th>
                            <th>Allocation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td><strong>{holding.get('ticker', 'N/A')}</strong></td>
                            <td>{holding.get('name', 'Unknown')[:50]}</td>
                            <td>{holding.get('quantity', 0):,.4f}</td>
                            <td>${holding['value']:,.2f}</td>
                            <td>{holding['allocation_percent']:.2f}%</td>
                        </tr>''' for holding in allocation['by_security'][:15]])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Recent Transactions -->
        <div class="card full-width">
            <h2>📋 Recent Transactions</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Amount</th>
                            <th>Category</th>
                            <th>Tags</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td>{txn.date.strftime('%Y-%m-%d')}</td>
                            <td>{txn.name[:40]}</td>
                            <td>{txn.type}</td>
                            <td class="{'positive' if float(txn.amount) >= 0 else 'negative'}">${float(txn.amount):,.2f}</td>
                            <td>{txn.category or txn.subtype or 'N/A'}</td>
                            <td>{'<span class="badge income">Income</span>' if txn.is_income else ''}{'<span class="badge deposit">Deposit</span>' if txn.is_deposit else ''}</td>
                        </tr>''' for txn in recent_txns])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Income Transactions -->
        <div class="card full-width">
            <h2>💵 Income Transactions</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Amount</th>
                            <th>Income Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td>{txn.date.strftime('%Y-%m-%d')}</td>
                            <td>{txn.name[:50]}</td>
                            <td>{txn.type}</td>
                            <td class="positive">${float(txn.amount):,.2f}</td>
                            <td><span class="badge income">{txn.income_type or 'N/A'}</span></td>
                        </tr>''' for txn in income_txns])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Expense Summary -->
        <div class="card full-width">
            <h2>💸 Expense Summary</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Total Spent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td><strong>{item['category'].title() if item['category'] else 'Uncategorized'}</strong></td>
                            <td>{item['count']}</td>
                            <td class="negative">${item['total']:,.2f}</td>
                        </tr>''' for item in expense_summary['by_category'][:20]])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Top Merchants -->
        <div class="card full-width">
            <h2>🏪 Top Merchants</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Merchant</th>
                            <th>Transactions</th>
                            <th>Total Spent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td><strong>{merchant['merchant'] or 'Unknown'}</strong></td>
                            <td>{merchant['count']}</td>
                            <td class="negative">${merchant['total']:,.2f}</td>
                        </tr>''' for merchant in top_merchants])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Expense Transactions -->
        <div class="card full-width">
            <h2>💸 Recent Expenses</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Merchant</th>
                            <th>Amount</th>
                            <th>Category</th>
                            <th>Account</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td>{txn.date.strftime('%Y-%m-%d')}</td>
                            <td>{(txn.merchant_name or txn.name)[:40]}</td>
                            <td class="negative">${abs(float(txn.amount)):,.2f}</td>
                            <td><span class="badge expense">{txn.expense_category or txn.primary_category or 'uncategorized'}</span></td>
                            <td>{txn.account.name if txn.account else 'N/A'}</td>
                        </tr>''' for txn in expense_txns])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="timestamp">
            Generated on {date.today().strftime('%B %d, %Y')} at {date.today().strftime('%H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    return html


def save_dashboard(output_path: str = "dashboard.html"):
    """Generate and save dashboard HTML file"""
    html = generate_dashboard_html()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path
