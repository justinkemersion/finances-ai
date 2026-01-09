# Plaid Setup Guide

## Getting Started with Plaid

### 1. Sign Up for Plaid

1. Go to [https://dashboard.plaid.com/signup](https://dashboard.plaid.com/signup)
2. Create an account (it's free for development)
3. Verify your email

### 2. Get Your Credentials

Once logged into the Plaid Dashboard:

1. **Navigate to Team Settings** → **Keys**
   - You'll see your `Client ID` and `Secret` keys
   - There are different keys for different environments:
     - **Sandbox** - For testing (free, no real bank connections)
     - **Development** - For development with real banks (limited)
     - **Production** - For live use (requires approval)

2. **For initial development, use Sandbox:**
   - Copy your `Client ID` (starts with something like `5f...`)
   - Copy your `Secret` (starts with something like `secret-sandbox-...`)

### 3. Configure Your .env File

Create a `.env` file in the project root:

```bash
# Plaid Configuration
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox  # Use 'sandbox' for testing
```

### 4. Understanding Plaid Environments

- **Sandbox** (`sandbox`):
  - Free testing environment
  - Use test credentials (username: `user_good`, password: `pass_good`)
  - No real bank connections
  - Perfect for development and testing

- **Development** (`development`):
  - Real bank connections
  - Limited to 100 items (bank connections)
  - Good for testing with your own accounts

- **Production** (`production`):
  - Live environment
  - Requires Plaid approval
  - For actual users

### 5. Testing the Connection

After setting up your `.env` file, you can test the Plaid connection. However, to actually connect a bank account, you'll need to:

1. Use Plaid Link (their frontend component) to get an `access_token`
2. Or use their API to create a test item in sandbox mode

### 6. Getting an Access Token

For **Sandbox testing**, you can create a test item directly:

```python
# This would be done through Plaid Link in a real app
# For sandbox, you can use their test credentials
```

For **real connections**, you'll need to:
1. Implement Plaid Link in your frontend (or use their API)
2. User goes through OAuth flow
3. You receive an `access_token` for that connection
4. Use that token to sync data

### 7. Charles Schwab Specific Notes

- Schwab is supported in Plaid's investment products
- Make sure you're using the Investment API endpoints (which this project does)
- In sandbox, you can test with mock investment accounts

### Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Dashboard](https://dashboard.plaid.com/)
- [Plaid API Reference](https://plaid.com/docs/api/)
- [Investment Products](https://plaid.com/docs/investments/)

### Quick Start for Testing

1. Sign up at dashboard.plaid.com
2. Get your sandbox credentials
3. Add them to `.env`
4. The sync command will work once you have an access_token

**Note**: Getting an `access_token` requires implementing Plaid Link or using their API to create test items. For initial testing, you might want to create a simple script to generate a test access token using Plaid's API.
