# Provider Architecture

This document describes the provider abstraction architecture that allows the application to support multiple financial data providers (Plaid, Teller, and future providers).

## Architecture Overview

The provider system uses the **Strategy Pattern** and **Factory Pattern** to provide a clean, extensible architecture:

```
┌─────────────────────────────────────────┐
│         Application Layer              │
│  (CLI, REST API, Analytics)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      ProviderFactory                     │
│  (Creates provider instances)           │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
┌─────▼──────┐        ┌──────▼──────┐
│ BaseProvider│        │ BaseProvider │
│   Client    │        │    Sync     │
│ (Abstract)  │        │  (Abstract) │
└─────┬───────┘        └──────┬──────┘
      │                        │
      │                        │
┌─────▼──────┐        ┌──────▼──────┐
│ PlaidClient│        │ PlaidSync   │
│ TellerClient│       │ TellerSync  │
│ (Future...) │       │ (Future...) │
└─────────────┘       └─────────────┘
```

## Design Principles

### 1. **Single Responsibility Principle (SRP)**
- Each provider implementation handles only its specific API
- Sync logic is separated from client logic
- Factory handles creation, not business logic

### 2. **Open/Closed Principle (OCP)**
- Open for extension (add new providers)
- Closed for modification (existing code doesn't change)

### 3. **Dependency Inversion Principle (DIP)**
- High-level modules depend on abstractions (`BaseProviderClient`, `BaseProviderSync`)
- Low-level modules (Plaid, Teller) implement those abstractions

### 4. **Interface Segregation Principle (ISP)**
- Base classes define clear, focused interfaces
- Providers only implement what they support

## File Structure

```
backend/app/providers/
├── __init__.py          # Public API exports
├── base.py              # Abstract base classes
├── factory.py           # Provider factory
├── plaid_client.py      # Plaid client implementation
├── plaid_sync.py        # Plaid sync implementation
├── teller_client.py     # Teller client implementation
└── teller_sync.py       # Teller sync implementation
```

## Base Classes

### `BaseProviderClient`

Abstract interface for provider API clients. All providers must implement:

- `get_accounts(access_token)` - Get account list
- `get_investment_holdings(access_token)` - Get investment holdings
- `get_investment_transactions(access_token, start_date, end_date)` - Get investment transactions
- `get_transactions(access_token, start_date, end_date, account_ids)` - Get banking transactions
- `create_link_token(redirect_uri)` - Create connection token/URL
- `exchange_public_token(public_token)` - Exchange token for access token

### `BaseProviderSync`

Abstract interface for syncing provider data to database. All providers must implement:

- `sync_accounts(db, access_token, item_id)` - Sync accounts
- `sync_holdings(db, access_token, as_of_date)` - Sync investment holdings
- `sync_transactions(db, access_token, start_date, end_date, ...)` - Sync transactions
- `sync_all(db, access_token, item_id, ...)` - Sync everything

## Provider Factory

The `ProviderFactory` creates provider instances:

```python
from backend.app.providers import ProviderFactory, ProviderType

# Create client
client = ProviderFactory.create_client(ProviderType.PLAID)
client = ProviderFactory.create_client(ProviderType.TELLER)

# Create sync handler
sync = ProviderFactory.create_sync(ProviderType.PLAID)
sync = ProviderFactory.create_sync(ProviderType.TELLER)

# From string
provider = ProviderFactory.from_string("plaid")
provider = ProviderFactory.from_string("teller")
```

## Configuration

Add to `.env`:

```bash
# Default provider
DEFAULT_PROVIDER=plaid  # or "teller"

# Plaid Configuration
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox  # or "production"

# Teller Configuration
TELLER_APPLICATION_ID=your_application_id
TELLER_CERTIFICATE_PATH=/path/to/certificate.pem
TELLER_PRIVATE_KEY_PATH=/path/to/private_key.pem
TELLER_ENV=sandbox  # or "production"
```

## Usage Examples

### CLI Commands

```bash
# Use default provider (from config)
python -m backend.app.api.cli sync --access-token <token> --item-id <id>

# Explicitly specify provider
python -m backend.app.api.cli sync --access-token <token> --item-id <id> --provider plaid
python -m backend.app.api.cli sync --access-token <token> --item-id <id> --provider teller

# Connect bank account
python -m backend.app.api.cli connect-bank --provider teller
python -m backend.app.api.cli connect-bank --provider plaid
```

### REST API

```bash
# Sync with default provider
POST /sync
{
  "access_token": "...",
  "item_id": "...",
  "sync_holdings": true,
  "sync_transactions": true
}

# Sync with specific provider
POST /sync
{
  "access_token": "...",
  "item_id": "...",
  "provider": "teller",
  "sync_holdings": true,
  "sync_transactions": true
}
```

### Python Code

```python
from backend.app.providers import ProviderFactory, ProviderType

# Get default provider from config
sync = ProviderFactory.create_sync()
results = sync.sync_all(db, access_token, item_id)

# Use specific provider
sync = ProviderFactory.create_sync(ProviderType.TELLER)
results = sync.sync_all(db, access_token, item_id)
```

## Adding a New Provider

To add a new provider (e.g., "Yodlee"):

1. **Add to `ProviderType` enum** in `base.py`:
   ```python
   class ProviderType(Enum):
       PLAID = "plaid"
       TELLER = "teller"
       YODLEE = "yodlee"  # New provider
   ```

2. **Create `yodlee_client.py`**:
   ```python
   from .base import BaseProviderClient
   
   class YodleeClient(BaseProviderClient):
       def get_accounts(self, access_token: str):
           # Implement Yodlee-specific logic
           pass
       # ... implement other methods
   ```

3. **Create `yodlee_sync.py`**:
   ```python
   from .base import BaseProviderSync
   
   class YodleeSync(BaseProviderSync):
       def sync_accounts(self, db, access_token, item_id):
           # Implement Yodlee-specific sync logic
           pass
       # ... implement other methods
   ```

4. **Update `factory.py`**:
   ```python
   from .yodlee_client import YodleeClient
   from .yodlee_sync import YodleeSync
   
   # In create_client():
   elif provider == ProviderType.YODLEE:
       return YodleeClient(**kwargs)
   
   # In create_sync():
   elif provider == ProviderType.YODLEE:
       return YodleeSync(provider_client)
   ```

5. **Add configuration** to `config.py`:
   ```python
   YODLEE_CLIENT_ID: Optional[str] = os.getenv("YODLEE_CLIENT_ID")
   # ... etc
   ```

That's it! The new provider is now available throughout the application.

## Data Standardization

All providers return data in a **standardized format**, regardless of the underlying API:

- **Accounts**: Same structure (id, name, type, balances, etc.)
- **Transactions**: Same structure (id, date, amount, category, etc.)
- **Holdings**: Same structure (account_id, security_id, quantity, value, etc.)

This allows the rest of the application to work with any provider without knowing which one is being used.

## Error Handling

Providers handle errors gracefully:

- Missing SDK: Clear error messages if provider SDK not installed
- Invalid credentials: Specific error messages per provider
- API errors: Wrapped in standardized exceptions

## Testing

The abstraction makes testing easier:

- Mock `BaseProviderClient` for unit tests
- Test sync logic independently of provider
- Test provider-specific logic in isolation

## Benefits

1. **Flexibility**: Users can choose their preferred provider
2. **Resilience**: Fallback if one provider has issues
3. **Extensibility**: Easy to add new providers
4. **Maintainability**: Clear separation of concerns
5. **Testability**: Easy to mock and test

## Current Status

### ✅ Implemented
- Abstract base classes
- Plaid implementation (fully functional)
- Teller implementation (structure complete, may need SDK API adjustments)
- Provider factory
- CLI integration
- REST API integration
- Configuration support

### 🔧 May Need Adjustment
- Teller SDK API calls (verify against actual Teller Python SDK)
- Teller Connect URL generation (verify actual API)

### 📝 Next Steps
1. Test Teller implementation with actual SDK
2. Adjust Teller API calls based on real SDK
3. Add comprehensive tests
4. Update documentation with Teller-specific setup

## Notes

- **Teller SDK**: The Teller implementation assumes the SDK API structure. You may need to adjust method calls based on the actual `teller-python` SDK.
- **Optional Dependencies**: Teller SDK is optional - code works without it, just can't use Teller provider.
- **Backward Compatibility**: Existing Plaid code continues to work unchanged.
