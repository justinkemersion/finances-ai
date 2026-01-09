# Setup Guide

## Prerequisites

- Python 3.9 or higher
- Plaid account and API credentials

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
DATABASE_URL=sqlite:///./finance_ai.db
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
API_HOST=0.0.0.0
API_PORT=8000
```

4. Initialize the database:
```bash
python -m backend.app.api.cli init-db
```

Or using Alembic:
```bash
alembic upgrade head
```

## Usage

### CLI

Run queries using the CLI:
```bash
python -m backend.app.api.cli ask "What's my net worth?"
python -m backend.app.api.cli net-worth
python -m backend.app.api.cli performance --days 30
python -m backend.app.api.cli allocation
```

Sync data from Plaid:
```bash
python -m backend.app.api.cli sync --access-token <token> --item-id <item_id>
```

### API Server

Start the API server:
```bash
python -m backend.main
```

Or:
```bash
uvicorn backend.app.api.rest:app --reload
```

The API will be available at `http://localhost:8000`

API documentation at `http://localhost:8000/docs`

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```
