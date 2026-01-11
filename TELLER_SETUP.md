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

### 3. Install Dependencies

This project uses direct HTTP requests to the Teller API (no SDK required). The `requests` library is used for API calls:

```bash
pip install requests
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The `requests` library is already included in `requirements.txt` and is likely already installed as a dependency of other packages.

### 4. Configure Your .env File

Create or update your `.env` file in the project root:

```bash
# Default provider (optional, defaults to plaid)
DEFAULT_PROVIDER=teller

# Teller Configuration
TELLER_APPLICATION_ID=app_xxxxxxxxxxxxx  # Your Teller application ID (starts with "app_")
TELLER_CERTIFICATE_PATH=/absolute/path/to/certificate.pem  # Absolute path INCLUDING filename
TELLER_PRIVATE_KEY_PATH=/absolute/path/to/private_key.pem  # Absolute path INCLUDING filename
TELLER_ENV=sandbox  # or "production"
```

**Important**: 
- Use **absolute paths** (starting with `/`) for certificate and private key files
- **Include the filename** in the path (e.g., `/home/user/certs/certificate.pem`, not just `/home/user/certs/`)
- Example:
  ```bash
  TELLER_CERTIFICATE_PATH=/home/justin/Projects/finances-ai/certs/certificate.pem
  TELLER_PRIVATE_KEY_PATH=/home/justin/Projects/finances-ai/certs/private_key.pem
  ```

### 5. Understanding Teller Environments

- **Sandbox** (`sandbox`):
  - Free for personal use
  - **Can connect to REAL bank accounts** (not just test data)
  - Perfect for personal use and development
  - No payment setup required

- **Production** (`production`):
  - **Commercial use only** - requires payment setup
  - For apps that will be released/commercialized
  - Not needed for personal use
  - **Use sandbox for personal projects with real bank accounts**

### 6. Understanding Teller Connect

**Good news**: Unlike Plaid, Teller does **NOT** require you to pre-configure redirect URIs in the dashboard. The redirect URI is passed directly in the Connect URL, so you can use any redirect URI you want without dashboard configuration.

The redirect URI (`http://localhost:8080/success` by default) is automatically included in the Teller Connect URL when you run the connect command.

### 7. Connect Your Bank Account

```bash
# Connect using Teller
python -m backend.app.api.cli connect-bank --provider teller
```

This will:
1. Start a local web server on `http://localhost:8080`
2. Create a Teller Connect URL
3. Open your browser to Teller Connect
4. You connect your bank account
5. After connecting, Teller redirects back to your local server
6. The authorization code is automatically exchanged for an access token

**Note**: If you see a non-working page in the browser, it likely means:
- The redirect URI isn't configured in your Teller Dashboard (see step 6 above)
- The redirect URI doesn't match exactly between your `.env`/command and Teller Dashboard

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

### "Non-working page in browser" or Connect URL issues
**Solution**: 
- Teller does NOT require redirect URI configuration in the dashboard
- If you see a non-working page, it might be:
  - The Connect URL format is incorrect (check that your `TELLER_APPLICATION_ID` is correct)
  - Teller's Connect service is temporarily unavailable
  - Your application ID doesn't have Connect access enabled
- Verify your `TELLER_APPLICATION_ID` is correct in your `.env` file
- Check that you're using the correct environment (sandbox vs production)
- Try the Connect URL directly in your browser to see the actual error message
- Consult [Teller's Connect documentation](https://teller.io/docs) for the latest API format

### "requests library is required"
**Solution**: Install with `pip install requests` or `pip install -r requirements.txt`

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

## Notes

- Teller uses certificate-based authentication (not API keys)
- Certificate files must be kept secure
- Teller Connect uses a different flow than Plaid Link
- Investment holdings support may be limited compared to Plaid
- This implementation uses direct HTTP requests (no SDK required)
- The `requests` library handles certificate-based authentication automatically
