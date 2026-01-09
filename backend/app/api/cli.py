"""CLI interface for Finance AI Analyzer"""

import click
import os
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from ..database import SessionLocal, engine, Base
from ..models import Account
from ..plaid import PlaidClient, PlaidSync
from ..queries import QueryHandler
from ..analytics import NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer, IncomeAnalyzer

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


if __name__ == "__main__":
    cli()
