"""CLI interface for Finance AI Analyzer"""

import click
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from ..database import SessionLocal, engine, Base
from ..models import Account
from ..plaid import PlaidClient, PlaidSync
from ..queries import QueryHandler
from ..analytics import NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer

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


if __name__ == "__main__":
    cli()
