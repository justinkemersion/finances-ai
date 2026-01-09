"""CLI interface for Finance AI Analyzer"""

import click
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from ..database import SessionLocal, engine, Base
from ..models import Account
from ..plaid import PlaidClient, PlaidSync
from ..queries import QueryHandler
from ..analytics import NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer, IncomeAnalyzer, ExpenseAnalyzer, ExpenseAnalyzer

console = Console()


@click.group()
def cli():
    """Finance AI Analyzer - Privacy-first personal finance tool"""
    pass


@cli.command()
def init_db():
    """Initialize the database"""
    console.print("[bold green]Creating database tables...[/bold green]")
    Base.metadata.create_all(bind=engine)
    console.print("[bold green]✓ Database initialized[/bold green]")


@cli.command()
@click.option("--access-token", required=True, help="Plaid access token")
@click.option("--item-id", required=True, help="Plaid item ID")
@click.option("--holdings/--no-holdings", default=True, help="Sync holdings")
@click.option("--transactions/--no-transactions", default=True, help="Sync transactions")
def sync(access_token: str, item_id: str, holdings: bool, transactions: bool):
    """Sync data from Plaid"""
    console.print("[bold blue]Syncing data from Plaid...[/bold blue]")
    
    db = SessionLocal()
    try:
        sync_handler = PlaidSync()
        results = sync_handler.sync_all(
            db=db,
            access_token=access_token,
            item_id=item_id,
            sync_holdings=holdings,
            sync_transactions=transactions
        )
        
        console.print(f"[green]✓ Synced {results['accounts']} accounts[/green]")
        if holdings:
            console.print(f"[green]✓ Synced {results['holdings']} holdings[/green]")
        if transactions:
            console.print(f"[green]✓ Synced {results['transactions']} transactions[/green]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        db.close()


@cli.command()
def net_worth():
    """Show current net worth"""
    db = SessionLocal()
    try:
        net_worth_data = NetWorthAnalyzer.calculate_current_net_worth(db)
        
        table = Table(title="Net Worth", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Total Assets", f"${net_worth_data['total_assets']:,.2f}")
        table.add_row("Total Liabilities", f"${net_worth_data['total_liabilities']:,.2f}")
        table.add_row("Net Worth", f"${net_worth_data['net_worth']:,.2f}", style="bold green")
        table.add_row("Investment Value", f"${net_worth_data['investment_value']:,.2f}")
        table.add_row("Cash Value", f"${net_worth_data['cash_value']:,.2f}")
        
        console.print(table)
    finally:
        db.close()


@cli.command()
@click.option("--days", default=30, help="Number of days to show")
def performance(days: int):
    """Show portfolio performance"""
    db = SessionLocal()
    try:
        start_date = date.today() - timedelta(days=days)
        perf_data = PerformanceAnalyzer.calculate_performance(
            db,
            start_date=start_date,
            end_date=date.today()
        )
        
        table = Table(title=f"Performance ({days} days)", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Start Value", f"${perf_data['start_value']:,.2f}")
        table.add_row("End Value", f"${perf_data['end_value']:,.2f}")
        table.add_row("Absolute Return", f"${perf_data['absolute_return']:,.2f}")
        table.add_row("Percent Return", f"{perf_data['percent_return']:.2f}%")
        table.add_row("Annualized Return", f"{perf_data['annualized_return']:.2f}%")
        
        console.print(table)
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=10, help="Number of top holdings to show")
def allocation(limit: int):
    """Show portfolio allocation"""
    db = SessionLocal()
    try:
        allocation_data = AllocationAnalyzer.calculate_allocation(db)
        top_holdings = allocation_data["by_security"][:limit]
        
        table = Table(title="Top Holdings", box=box.ROUNDED)
        table.add_column("Ticker", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Value", style="green", justify="right")
        table.add_column("Allocation", style="yellow", justify="right")
        
        for holding in top_holdings:
            table.add_row(
                holding.get("ticker", "N/A"),
                holding.get("name", "Unknown"),
                f"${holding['value']:,.2f}",
                f"{holding['allocation_percent']:.2f}%"
            )
        
        console.print(table)
        
        # Show account breakdown
        account_table = Table(title="By Account", box=box.ROUNDED)
        account_table.add_column("Account", style="cyan")
        account_table.add_column("Value", style="green", justify="right")
        account_table.add_column("Allocation", style="yellow", justify="right")
        
        for account in allocation_data["by_account"]:
            account_table.add_row(
                account["account_name"],
                f"${account['value']:,.2f}",
                f"{account['allocation_percent']:.2f}%"
            )
        
        console.print(account_table)
    finally:
        db.close()


@cli.command()
@click.argument("query", nargs=-1, required=True)
def ask(query: tuple):
    """Ask a natural language question about your finances"""
    query_str = " ".join(query)
    db = SessionLocal()
    try:
        handler = QueryHandler(db)
        result = handler.handle_query(query_str)
        
        if "error" in result:
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
            if "suggestions" in result:
                console.print("\n[bold]Try asking:[/bold]")
                for suggestion in result["suggestions"]:
                    console.print(f"  • {suggestion}")
        else:
            # Format output based on intent
            intent = result.get("intent")
            data = result.get("data", {})
            
            if intent == "net_worth":
                if result.get("type") == "history":
                    console.print("[bold]Net Worth History[/bold]")
                    for entry in data:
                        console.print(
                            f"  {entry['date']}: ${entry['net_worth']:,.2f}"
                        )
                else:
                    console.print(f"[bold]Net Worth:[/bold] ${data['net_worth']:,.2f}")
            
            elif intent == "performance":
                perf = data
                console.print(f"[bold]Performance:[/bold]")
                console.print(f"  Return: ${perf['absolute_return']:,.2f} ({perf['percent_return']:.2f}%)")
                console.print(f"  Start: ${perf['start_value']:,.2f}")
                console.print(f"  End: ${perf['end_value']:,.2f}")
            
            elif intent == "allocation":
                console.print(f"[bold]Total Value:[/bold] ${data['total_value']:,.2f}")
                console.print("\n[bold]Top Holdings:[/bold]")
                for holding in data["by_security"][:5]:
                    console.print(
                        f"  {holding.get('ticker', 'N/A')}: "
                        f"${holding['value']:,.2f} ({holding['allocation_percent']:.2f}%)"
                    )
            
            elif intent == "holdings":
                console.print(f"[bold]Holdings ({data['count']}):[/bold]")
                for holding in data["holdings"][:10]:
                    console.print(
                        f"  {holding.get('ticker', 'N/A')}: "
                        f"{holding.get('quantity', 0):.4f} shares @ ${holding.get('current_value', 0):,.2f}"
                    )
            
            elif intent == "transactions":
                console.print(f"[bold]Recent Transactions ({data['count']}):[/bold]")
                for txn in data["transactions"][:10]:
                    console.print(
                        f"  {txn['date']}: {txn['name']} - "
                        f"${txn['amount']:,.2f} ({txn['type']})"
                    )
            
            elif intent == "income":
                console.print(f"[bold green]Income Summary[/bold green]")
                console.print(f"  Total Income: ${data['total_income']:,.2f}")
                console.print(f"  Paystubs: {data['paystub_count']} (${data['paystub_total']:,.2f})")
                if data.get('by_type'):
                    console.print("\n[bold]By Type:[/bold]")
                    for item in data['by_type']:
                        console.print(
                            f"  {item['type']}: ${item['total']:,.2f} ({item['count']} transactions)"
                        )
            
            elif intent == "expenses":
                console.print(f"[bold red]Expense Summary[/bold red]")
                console.print(f"  Total Expenses: ${data['total_expenses']:,.2f}")
                console.print(f"  Transactions: {data['transaction_count']}")
                if data.get('by_category'):
                    console.print("\n[bold]Top Categories:[/bold]")
                    for item in data['by_category'][:10]:
                        console.print(
                            f"  {item['category']}: ${item['total']:,.2f} ({item['count']} transactions)"
                        )
            
            elif intent == "spending_category":
                category = result.get('category', 'category')
                console.print(f"[bold yellow]Spending on {category.title()}[/bold yellow]")
                console.print(f"  Total: ${data['total']:,.2f}")
                console.print(f"  Transactions: {data['count']}")
                if data.get('transactions'):
                    console.print("\n[bold]Recent Transactions:[/bold]")
                    for txn in data['transactions'][:10]:
                        console.print(
                            f"  {txn['date']}: {txn.get('merchant', txn['name'])} - "
                            f"${txn['amount']:,.2f}"
                        )
            
            elif intent == "dividends":
                console.print(f"[bold green]Dividend Summary[/bold green]")
                console.print(f"  Total Dividends: ${data['total']:,.2f}")
                console.print(f"  Count: {data['count']}")
                if data.get('dividends'):
                    console.print("\n[bold]Recent Dividends:[/bold]")
                    for div in data['dividends'][:10]:
                        ticker = div.get('ticker', 'N/A')
                        console.print(
                            f"  {div['date']}: {ticker} - ${div['amount']:,.2f}"
                        )
            
            elif intent == "cash_flow":
                net = data['net_cash_flow']
                color = "green" if net >= 0 else "red"
                console.print(f"[bold]Cash Flow Summary[/bold]")
                console.print(f"  [green]Income:[/green] ${data['income']:,.2f}")
                console.print(f"  [red]Expenses:[/red] ${data['expenses']:,.2f}")
                console.print(f"  [bold {color}]Net Cash Flow:[/bold {color}] ${net:,.2f}")
                if data.get('income_breakdown'):
                    console.print("\n[bold]Income Breakdown:[/bold]")
                    for item in data['income_breakdown'][:5]:
                        console.print(f"  {item['type']}: ${item['total']:,.2f}")
                if data.get('expense_breakdown'):
                    console.print("\n[bold]Top Expenses:[/bold]")
                    for item in data['expense_breakdown'][:5]:
                        console.print(f"  {item['category']}: ${item['total']:,.2f}")
            
            elif intent == "merchant":
                merchant = result.get('merchant', 'merchant')
                console.print(f"[bold]Spending at {merchant.title()}[/bold]")
                console.print(f"  Total: ${data['total']:,.2f}")
                console.print(f"  Transactions: {data['count']}")
                if data.get('transactions'):
                    console.print("\n[bold]Recent Transactions:[/bold]")
                    for txn in data['transactions'][:10]:
                        console.print(
                            f"  {txn['date']}: ${txn['amount']:,.2f} "
                            f"({txn.get('category', 'uncategorized')})"
                        )
            
            elif intent == "lunch":
                console.print(f"[bold yellow]Lunch Spending[/bold yellow]")
                console.print(f"  Total: ${data['total']:,.2f}")
                console.print(f"  Transactions: {data['count']}")
                
                if data.get('uncertain_count', 0) > 0:
                    console.print(f"\n[dim yellow]⚠ {data['uncertain_count']} uncertain transactions (${data.get('uncertain_total', 0):,.2f})[/dim yellow]")
                    console.print(f"[dim]These may be lunch but have lower confidence scores[/dim]")
                
                if data.get('merchant_breakdown'):
                    console.print("\n[bold]By Merchant:[/bold]")
                    for item in data['merchant_breakdown'][:10]:
                        conf_str = f" (confidence: {item.get('confidence', 'N/A')}%)" if item.get('confidence') else ""
                        console.print(
                            f"  {item['merchant']}: ${item['total']:,.2f} ({item['count']} transactions){conf_str}"
                        )
                
                if data.get('transactions'):
                    console.print("\n[bold]Recent Lunch Transactions:[/bold]")
                    for txn in data['transactions'][:15]:
                        time_str = f" @ {txn['time']}" if txn.get('time') else ""
                        merchant_str = f" - {txn['merchant']}" if txn.get('merchant') else ""
                        conf_str = f" [{txn.get('confidence', 'N/A')}%]" if txn.get('confidence') else ""
                        console.print(
                            f"  {txn['date']}{time_str}{merchant_str}: ${txn['amount']:,.2f}{conf_str}"
                        )
                        # Show confidence reasons for lower confidence transactions
                        if txn.get('confidence', 100) < 75 and txn.get('confidence_reasons'):
                            reasons = ", ".join(txn['confidence_reasons'][:2])
                            console.print(f"    [dim]→ {reasons}[/dim]")
                
                if data.get('uncertain_transactions'):
                    console.print("\n[bold yellow]Uncertain Transactions (may not be lunch):[/bold yellow]")
                    for txn in data['uncertain_transactions'][:5]:
                        time_str = f" @ {txn['time']}" if txn.get('time') else ""
                        console.print(
                            f"  {txn['date']}{time_str} - {txn.get('merchant', txn['name'])}: "
                            f"${txn['amount']:,.2f} [{txn.get('confidence', 'N/A')}%]"
                        )
                        if txn.get('confidence_reasons'):
                            reasons = ", ".join(txn['confidence_reasons'][:3])
                            console.print(f"    [dim]→ {reasons}[/dim]")
    finally:
        db.close()


@cli.command()
def accounts():
    """List all accounts"""
    db = SessionLocal()
    try:
        accounts = db.query(Account).filter(Account.is_active == True).all()
        
        table = Table(title="Accounts", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Subtype", style="yellow")
        
        for account in accounts:
            table.add_row(
                account.id[:8] + "...",
                account.name,
                account.type,
                account.subtype or "N/A"
            )
        
        console.print(table)
    finally:
        db.close()


@cli.command()
@click.option("--months", default=12, help="Number of months to show")
@click.option("--account-id", help="Filter by account ID")
def income(months: int, account_id: str):
    """Show income summary and breakdown"""
    db = SessionLocal()
    try:
        summary = IncomeAnalyzer.calculate_income_summary(db, account_id=account_id)
        monthly = IncomeAnalyzer.get_monthly_income(db, months=months, account_id=account_id)
        
        # Summary table
        table = Table(title="Income Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Total Income", f"${summary['total_income']:,.2f}")
        table.add_row("Paystubs", f"{summary['paystub_count']} (${summary['paystub_total']:,.2f})")
        
        console.print(table)
        
        # Income by type
        if summary['by_type']:
            type_table = Table(title="Income by Type", box=box.ROUNDED)
            type_table.add_column("Type", style="cyan")
            type_table.add_column("Count", style="white", justify="right")
            type_table.add_column("Total", style="green", justify="right")
            
            for item in summary['by_type']:
                type_table.add_row(
                    item['type'].title(),
                    str(item['count']),
                    f"${item['total']:,.2f}"
                )
            
            console.print(type_table)
        
        # Monthly breakdown
        if monthly:
            monthly_table = Table(title=f"Monthly Income ({months} months)", box=box.ROUNDED)
            monthly_table.add_column("Month", style="cyan")
            monthly_table.add_column("Count", style="white", justify="right")
            monthly_table.add_column("Total", style="green", justify="right")
            
            for month_data in monthly:
                monthly_table.add_row(
                    month_data['month'],
                    str(month_data['transaction_count']),
                    f"${month_data['total_income']:,.2f}"
                )
            
            console.print(monthly_table)
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=20, help="Number of transactions to show")
@click.option("--account-id", help="Filter by account ID")
def paystubs(limit: int, account_id: str):
    """List paystub/payroll transactions"""
    db = SessionLocal()
    try:
        paystubs = IncomeAnalyzer.get_paystubs(db, account_id=account_id)
        
        table = Table(title="Paystubs", box=box.ROUNDED)
        table.add_column("Date", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Account", style="yellow")
        
        for txn in paystubs[:limit]:
            account = db.query(Account).filter(Account.id == txn.account_id).first()
            account_name = account.name if account else txn.account_id[:8]
            
            table.add_row(
                txn.date.strftime("%Y-%m-%d"),
                txn.name,
                f"${float(txn.amount):,.2f}",
                account_name
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {min(limit, len(paystubs))} of {len(paystubs)} paystubs[/dim]")
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=20, help="Number of transactions to show")
@click.option("--account-id", help="Filter by account ID")
@click.option("--income-type", help="Filter by income type")
def deposits(limit: int, account_id: str, income_type: str):
    """List deposit transactions"""
    db = SessionLocal()
    try:
        deposits_list = IncomeAnalyzer.get_deposits(db, account_id=account_id)
        
        table = Table(title="Deposits", box=box.ROUNDED)
        table.add_column("Date", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Type", style="yellow")
        table.add_column("Account", style="yellow")
        
        for txn in deposits_list[:limit]:
            account = db.query(Account).filter(Account.id == txn.account_id).first()
            account_name = account.name if account else txn.account_id[:8]
            
            table.add_row(
                txn.date.strftime("%Y-%m-%d"),
                txn.name,
                f"${float(txn.amount):,.2f}",
                txn.income_type or "deposit",
                account_name
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {min(limit, len(deposits_list))} of {len(deposits_list)} deposits[/dim]")
    finally:
        db.close()


@cli.command()
@click.option("--institution-id", default="ins_109508", help="Institution ID for sandbox (default: test bank)")
def get_token(institution_id: str):
    """Test Plaid connection and create a sandbox item to get access token"""
    from ..plaid.test_connection import test_plaid_connection, create_sandbox_item
    
    console.print("[bold blue]Testing Plaid connection...[/bold blue]")
    
    success, client = test_plaid_connection()
    if not success:
        console.print("[bold red]❌ Failed to connect to Plaid. Check your credentials in .env[/bold red]")
        return
    
    console.print("\n[bold blue]Creating sandbox test item...[/bold blue]")
    access_token, item_id = create_sandbox_item(client, institution_id)
    
    if access_token and item_id:
        console.print("\n[bold green]✓ Success![/bold green]")
        console.print(f"\n[bold]Access Token:[/bold] {access_token}")
        console.print(f"[bold]Item ID:[/bold] {item_id}")
        console.print("\n[bold]Next step:[/bold] Run sync command with these credentials")


@cli.command()
@click.option("--months", default=1, help="Number of months to show")
@click.option("--account-id", help="Filter by account ID")
@click.option("--category", help="Filter by expense category")
def expenses(months: int, account_id: str, category: str):
    """Show expense summary and breakdown"""
    db = SessionLocal()
    try:
        summary = ExpenseAnalyzer.calculate_expense_summary(db, account_id=account_id)
        monthly = ExpenseAnalyzer.get_monthly_expenses(db, months=months, account_id=account_id)
        
        # Summary table
        table = Table(title="Expense Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="red", justify="right")
        
        table.add_row("Total Expenses", f"${summary['total_expenses']:,.2f}")
        table.add_row("Transaction Count", str(summary['transaction_count']))
        
        console.print(table)
        
        # Expenses by category
        if summary['by_category']:
            cat_table = Table(title="Expenses by Category", box=box.ROUNDED)
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count", style="white", justify="right")
            cat_table.add_column("Total", style="red", justify="right")
            
            for item in summary['by_category'][:15]:
                cat_table.add_row(
                    item['category'].title() if item['category'] else "Uncategorized",
                    str(item['count']),
                    f"${item['total']:,.2f}"
                )
            
            console.print(cat_table)
        
        # Monthly breakdown
        if monthly:
            monthly_table = Table(title=f"Monthly Expenses ({months} months)", box=box.ROUNDED)
            monthly_table.add_column("Month", style="cyan")
            monthly_table.add_column("Count", style="white", justify="right")
            monthly_table.add_column("Total", style="red", justify="right")
            
            for month_data in monthly:
                monthly_table.add_row(
                    month_data['month'],
                    str(month_data['transaction_count']),
                    f"${month_data['total_expenses']:,.2f}"
                )
            
            console.print(monthly_table)
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=20, help="Number of transactions to show")
@click.option("--account-id", help="Filter by account ID")
@click.option("--category", help="Filter by expense category")
def spending(limit: int, account_id: str, category: str):
    """List expense transactions"""
    db = SessionLocal()
    try:
        expenses_list = ExpenseAnalyzer.get_expenses(db, account_id=account_id, expense_category=category)
        
        table = Table(title="Expenses", box=box.ROUNDED)
        table.add_column("Date", style="cyan")
        table.add_column("Merchant", style="white")
        table.add_column("Amount", style="red", justify="right")
        table.add_column("Category", style="yellow")
        table.add_column("Account", style="yellow")
        
        for txn in expenses_list[:limit]:
            account = db.query(Account).filter(Account.id == txn.account_id).first()
            account_name = account.name if account else txn.account_id[:8]
            
            table.add_row(
                txn.date.strftime("%Y-%m-%d"),
                (txn.merchant_name or txn.name)[:30],
                f"${abs(float(txn.amount)):,.2f}",
                txn.expense_category or txn.primary_category or "uncategorized",
                account_name
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {min(limit, len(expenses_list))} of {len(expenses_list)} expenses[/dim]")
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=10, help="Number of merchants to show")
def merchants(limit: int):
    """Show top merchants by spending"""
    db = SessionLocal()
    try:
        top_merchants = ExpenseAnalyzer.get_top_merchants(db, limit=limit)
        
        table = Table(title="Top Merchants", box=box.ROUNDED)
        table.add_column("Merchant", style="cyan")
        table.add_column("Transactions", style="white", justify="right")
        table.add_column("Total Spent", style="red", justify="right")
        
        for merchant in top_merchants:
            table.add_row(
                merchant['merchant'] or "Unknown",
                str(merchant['count']),
                f"${merchant['total']:,.2f}"
            )
        
        console.print(table)
    finally:
        db.close()


@cli.command()
@click.option("--output", default="dashboard.html", help="Output file path")
def dashboard(output: str):
    """Generate HTML dashboard with financial data"""
    from .dashboard import save_dashboard
    
    console.print("[bold blue]Generating dashboard...[/bold blue]")
    try:
        output_path = save_dashboard(output)
        console.print(f"[bold green]✓ Dashboard generated:[/bold green] {output_path}")
        console.print(f"\n[bold]Open in browser:[/bold] file://{os.path.abspath(output_path)}")
    except Exception as e:
        console.print(f"[bold red]❌ Error generating dashboard:[/bold red] {str(e)}")


@cli.command()
@click.option("--output", default="finance_export.json", help="Output JSON file path")
@click.option("--start-date", help="Start date for transactions (YYYY-MM-DD)")
@click.option("--end-date", help="End date for transactions (YYYY-MM-DD)")
@click.option("--account-id", help="Filter by account ID")
@click.option("--transaction-type", help="Filter by transaction type")
@click.option("--no-accounts", is_flag=True, help="Exclude accounts from export")
@click.option("--no-holdings", is_flag=True, help="Exclude holdings from export")
@click.option("--no-transactions", is_flag=True, help="Exclude transactions from export")
@click.option("--no-net-worth", is_flag=True, help="Exclude net worth snapshots from export")
@click.option("--no-summary", is_flag=True, help="Exclude summary statistics from export")
@click.option("--no-investment-txns", is_flag=True, help="Exclude investment transactions")
@click.option("--no-banking-txns", is_flag=True, help="Exclude banking transactions")
@click.option("--no-pending", is_flag=True, help="Exclude pending transactions")
@click.option("--include-inactive", is_flag=True, help="Include inactive accounts")
def export(
    output: str,
    start_date: str,
    end_date: str,
    account_id: str,
    transaction_type: str,
    no_accounts: bool,
    no_holdings: bool,
    no_transactions: bool,
    no_net_worth: bool,
    no_summary: bool,
    no_investment_txns: bool,
    no_banking_txns: bool,
    no_pending: bool,
    include_inactive: bool
):
    """Export database to JSON format for LLM analysis (ChatGPT, Claude, etc.)"""
    from .export import export_to_json
    from datetime import datetime
    
    console.print("[bold blue]Exporting database to JSON...[/bold blue]")
    
    try:
        # Parse dates
        start_date_obj = None
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        end_date_obj = None
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        output_path = export_to_json(
            output_path=output,
            include_accounts=not no_accounts,
            include_holdings=not no_holdings,
            include_transactions=not no_transactions,
            include_net_worth=not no_net_worth,
            include_summary=not no_summary,
            start_date=start_date_obj,
            end_date=end_date_obj,
            account_id=account_id,
            transaction_type=transaction_type,
            include_investment_txns=not no_investment_txns,
            include_banking_txns=not no_banking_txns,
            include_pending=not no_pending,
            include_inactive_accounts=include_inactive
        )
        
        console.print(f"[bold green]✓ Export completed:[/bold green] {output_path}")
        console.print(f"\n[bold]File size:[/bold] {os.path.getsize(output_path) / 1024:.2f} KB")
        console.print(f"\n[bold]You can now upload this file to ChatGPT, Claude, or other LLMs for analysis.[/bold]")
        console.print(f"\n[dim]Tip: Use --start-date and --end-date to export specific time periods[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error exporting data:[/bold red] {str(e)}")


@cli.command()
@click.option("--account-id", help="Account ID to inject data for (creates test account if not provided)")
@click.option("--months", default=3, help="Number of months of data to generate")
@click.option("--no-income", is_flag=True, help="Skip income transactions")
def inject_test_data(account_id: str, months: int, no_income: bool):
    """Inject realistic test data for testing natural language queries"""
    from ..utils.inject_test_data import inject_test_data as inject_data
    
    db = SessionLocal()
    try:
        console.print("[bold blue]Injecting test data...[/bold blue]")
        console.print(f"[dim]This will create realistic spending data (beer, restaurants, gas, groceries, bills)[/dim]")
        
        transactions = inject_data(
            db=db,
            account_id=account_id,
            months_back=months,
            include_income=not no_income
        )
        
        console.print(f"\n[bold green]✓ Successfully created {len(transactions)} test transactions[/bold green]")
        console.print("\n[bold]Try these queries:[/bold]")
        console.print("  • 'how much did I spend on beer?'")
        console.print("  • 'restaurant spending last month'")
        console.print("  • 'how much at Starbucks?'")
        console.print("  • 'what's my income?'")
        console.print("  • 'gas expenses'")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error injecting test data:[/bold red] {str(e)}")
        db.rollback()
    finally:
        db.close()


@cli.command()
@click.argument("query", required=False)
@click.option("--provider", help="AI provider to use (openai, anthropic)")
@click.option("--api-key", help="API key (overrides auto-detection)")
@click.option("--model", help="Exact model to use (e.g., gpt-4o, gemini-1.5-pro, claude-3-5-sonnet-20241022, command-r-plus)")
@click.option("--list-models", is_flag=True, help="List available models for a provider")
@click.option("--full-data", is_flag=True, help="Include full database export (use with caution)")
@click.option("--list-providers", is_flag=True, help="List available providers and exit")
def ai(query: str, provider: str, api_key: str, model: str, full_data: bool, list_providers: bool, list_models: bool):
    """Query AI with your financial data for analysis and insights"""
    from ..ai import AIClient, AIProvider, AIConfig
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    db = SessionLocal()
    
    try:
        # List providers if requested
        if list_providers:
            detected = AIConfig.detect_api_keys()
            if not detected:
                console.print("[bold yellow]No AI providers found.[/bold yellow]")
                console.print("\n[bold]To set up AI providers:[/bold]")
                console.print("1. Add to .env or .env.local:")
                console.print("   OPENAI_API_KEY=your_key_here")
                console.print("   ANTHROPIC_API_KEY=your_key_here")
                console.print("2. Or export in shell config (.bashrc, .zshrc, etc.):")
                console.print("   export OPENAI_API_KEY=your_key_here")
                return
            
            table = Table(title="Available AI Providers", box=box.ROUNDED)
            table.add_column("Provider", style="cyan")
            table.add_column("Source", style="yellow")
            table.add_column("Key Preview", style="dim")
            
            for provider_enum, sources in detected.items():
                for source, key in sources:
                    key_preview = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key[:8] + "..."
                    table.add_row(
                        provider_enum.value.title(),
                        source,
                        key_preview
                    )
            
            console.print(table)
            return
        
        # List models if requested
        if list_models:
            if not provider:
                console.print("[bold red]❌ Error: --list-models requires --provider[/bold red]")
                console.print("\n[bold]Usage:[/bold] python -m backend.app ai --list-models --provider openai")
                return
            
            try:
                provider_enum = AIProvider(provider.lower())
            except ValueError:
                console.print(f"[bold red]❌ Unknown provider: {provider}[/bold red]")
                return
            
            # Get available models for provider
            from ..ai.providers import get_provider
            try:
                # Create a dummy provider instance to get models
                # We'll use a placeholder key just to instantiate
                temp_provider = get_provider(provider_enum, "dummy_key")
                if hasattr(temp_provider, 'AVAILABLE_MODELS'):
                    models = temp_provider.AVAILABLE_MODELS
                else:
                    # Fallback to common models
                    models = {
                        AIProvider.OPENAI: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                        AIProvider.ANTHROPIC: ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                        AIProvider.GOOGLE: ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"],
                        AIProvider.COHERE: ["command-r-plus", "command-r", "command", "command-light"],
                    }.get(provider_enum, [])
                
                table = Table(title=f"Available Models for {provider_enum.value.title()}", box=box.ROUNDED)
                table.add_column("Model", style="cyan")
                table.add_column("Description", style="dim")
                
                model_descriptions = {
                    "gpt-4o": "Most capable, latest model",
                    "gpt-4o-mini": "Fast and affordable",
                    "gpt-4-turbo": "High performance",
                    "gpt-4": "Previous generation",
                    "gpt-3.5-turbo": "Fast and cost-effective",
                    "claude-3-5-sonnet-20241022": "Latest, most capable",
                    "claude-3-opus-20240229": "Most powerful",
                    "claude-3-sonnet-20240229": "Balanced performance",
                    "claude-3-haiku-20240307": "Fast and efficient",
                    "gemini-1.5-pro": "Most capable, latest",
                    "gemini-1.5-flash": "Fast and efficient",
                    "gemini-pro": "Previous generation",
                    "command-r-plus": "Most capable",
                    "command-r": "High performance",
                    "command": "Balanced",
                    "command-light": "Fast and efficient",
                }
                
                for model_name in models:
                    desc = model_descriptions.get(model_name, "Available model")
                    table.add_row(model_name, desc)
                
                console.print(table)
                console.print(f"\n[dim]Use --model to specify exact model: --model {models[0] if models else 'model-name'}[/dim]")
            except Exception as e:
                console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
            return
        
        # Require query if not listing providers
        if not query:
            console.print("[bold red]❌ Error: Query is required (or use --list-providers)[/bold red]")
            console.print("\n[bold]Usage:[/bold] python -m backend.app ai \"your question here\"")
            console.print("[bold]Example:[/bold] python -m backend.app ai \"where can I focus on budgeting to make quick wins with savings?\"")
            return
        
        # Determine provider
        provider_enum = None
        if provider:
            try:
                provider_enum = AIProvider(provider.lower())
            except ValueError:
                console.print(f"[bold red]❌ Unknown provider: {provider}[/bold red]")
                console.print(f"[bold]Available providers:[/bold] {', '.join([p.value for p in AIProvider])}")
                return
        
        # Initialize AI client
        try:
            ai_client = AIClient(
                db=db,
                provider=provider_enum,
                api_key=api_key,
                model=model
            )
        except ValueError as e:
            console.print(f"[bold red]❌ {str(e)}[/bold red]")
            console.print("\n[bold]Run with --list-providers to see available providers[/bold]")
            return
        
        # Query AI
        console.print(f"[bold blue]🤖 Querying {ai_client.provider.value.title()}...[/bold blue]")
        console.print(f"[dim]Query: {query}[/dim]\n")
        
        result = ai_client.query(query, include_full_data=full_data)
        
        if "error" in result:
            console.print(f"[bold red]❌ Error:[/bold red] {result['error']}")
            return
        
        # Display response
        response = result.get("response", "")
        data_info = result.get("data_included", {})
        
        # Format response as markdown
        markdown = Markdown(response)
        panel = Panel(
            markdown,
            title=f"[bold green]AI Response ({ai_client.provider.value.title()})[/bold green]",
            border_style="green"
        )
        console.print(panel)
        
        # Show data context info
        if data_info:
            console.print(f"\n[dim]Data included: {', '.join(data_info.get('keys', []))}[/dim]")
            if data_info.get('transaction_count', 0) > 0:
                console.print(f"[dim]Transactions: {data_info['transaction_count']}[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    finally:
        db.close()


if __name__ == "__main__":
    cli()
