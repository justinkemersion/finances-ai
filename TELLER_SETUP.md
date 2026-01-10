# Teller Setup Guide

## Overview

Teller is a financial data provider that offers a free tier for personal use. It's a great alternative to Plaid, especially if you want to avoid paid plans.

## Getting Started

### 1. Sign Up for Teller

1. Go to [https://teller.io](https://teller.io)
2. Create an account
3. Complete the application process

### 2. Get Your Credentials

After signing up, you'll receive:
- **Application ID** - Your Teller application identifier
- **Certificate** (`certificate.pem`) - Client certificate for authentication
- **Private Key** (`private_key.pem`) - Private key for certificate authentication

These are typically provided in a `teller.zip` file that you download.

### 3. Install Teller SDK

```bash
pip install teller-python
```

Or add to `requirements.txt`:
```
teller-python>=1.0.0
```

### 4. Configure Your .env File

Create or update your `.env` file in the project root:

```bash
# Default provider (optional, defaults to plaid)
DEFAULT_PROVIDER=teller

# Teller Configuration
TELLER_APPLICATION_ID=your_application_id_here
TELLER_CERTIFICATE_PATH=/path/to/certificate.pem
TELLER_PRIVATE_KEY_PATH=/path/to/private_key.pem
TELLER_ENV=sandbox  # or "production"
```

**Important**: Use absolute paths for certificate and private key files.

### 5. Understanding Teller Environments

- **Sandbox** (`sandbox`):
  - Free testing environment
  - Test bank connections
  - Perfect for development

- **Production** (`production`):
  - Real bank connections
  - Free tier available for personal use
  - Production-ready

### 6. Connect Your Bank Account

```bash
# Connect using Teller
python -m backend.app.api.cli connect-bank --provider teller
```

This will:
1. Create a Teller Connect URL
2. Open your browser to Teller Connect
3. You connect your bank account
4. After connecting, you'll get an authorization code
5. Exchange the code for an access token

**After connecting**, extract the authorization code from the callback URL and run:

```bash
python -m backend.app.api.cli exchange-token <authorization_code> --provider teller
```

### 7. Sync Your Data

```bash
# Sync using Teller
python -m backend.app.api.cli sync --access-token <token> --item-id <item_id> --provider teller
```

## Teller vs Plaid

| Feature | Teller | Plaid |
|---------|--------|-------|
| Free Tier | ✅ Yes (personal use) | ❌ Requires paid plan for production |
| Investment Support | ⚠️ Limited | ✅ Full support |
| Banking Transactions | ✅ Yes | ✅ Yes |
| Setup Complexity | Medium (certificates) | Easy (API keys) |
| API Style | Modern REST | Comprehensive |

## Troubleshooting

### "Teller SDK not installed"
**Solution**: Install with `pip install teller-python`

### "Certificate not found"
**Solution**: 
- Check that `TELLER_CERTIFICATE_PATH` points to the correct file
- Use absolute paths, not relative paths
- Verify the file exists and is readable

### "Private key not found"
**Solution**:
- Check that `TELLER_PRIVATE_KEY_PATH` points to the correct file
- Use absolute paths
- Verify the file exists and is readable

### "Invalid credentials"
**Solution**:
- Verify your Application ID is correct
- Ensure certificate and private key match
- Check that you're using the correct environment (sandbox vs production)

## Resources

- [Teller Documentation](https://teller.io/docs)
- [Teller API Reference](https://teller.io/docs/api)
- [Teller Connect Guide](https://teller.io/docs/guides/quickstart)
- [Teller Python SDK](https://github.com/teller/teller-python)

## Notes

- Teller uses certificate-based authentication (not API keys)
- Certificate files must be kept secure
- Teller Connect uses a different flow than Plaid Link
- Investment holdings support may be limited compared to Plaid
