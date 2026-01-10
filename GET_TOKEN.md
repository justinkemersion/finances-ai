# How to Get a Plaid Access Token

## Quick Method: Sandbox Testing (Recommended to Start)

For testing and development, you can create a **sandbox test item** which gives you an access token without connecting a real bank:

```bash
source venv/bin/activate
python -m backend.app.api.cli get-token
```

This will:
1. Test your Plaid credentials
2. Create a sandbox test item
3. Give you an `access_token` and `item_id` that you can use immediately

**Note**: Sandbox items use fake/test data, perfect for development.

## For Real Bank Connections (Charles Schwab, etc.)

### Option 1: Use Built-in Connect Command (Easiest - Recommended)

The easiest way to connect a real bank account is using the built-in `connect-bank` command:

```bash
python -m backend.app.api.cli connect-bank
```

This command will:
1. Create a Plaid link token
2. Start a local web server on `http://localhost:8080`
3. Automatically open your browser
4. Let you connect your bank through Plaid's secure interface
5. Exchange the token and display your credentials

**Options:**
- `--port PORT`: Use a different port (default: 8080)
- `--no-browser`: Don't automatically open browser (you'll need to visit the URL manually)

**⚠️ Important: Configure Redirect URI First**

Before running `connect-bank`, you must add the redirect URI to your Plaid Dashboard:

1. Go to https://dashboard.plaid.com/team/api
2. Scroll to "Allowed redirect URIs" section
3. Click "Add redirect URI"
4. Enter: `http://localhost:8080/success` (or your custom port if using `--port`)
5. Click "Save"
6. Run the command again

If you see a redirect URI error, follow the instructions above to add it to your dashboard.

**Examples:**
```bash
# Use default port 8080
python -m backend.app.api.cli connect-bank

# Use a different port if 8080 is busy (remember to add the redirect URI for that port too!)
python -m backend.app.api.cli connect-bank --port 3000

# Don't open browser automatically
python -m backend.app.api.cli connect-bank --no-browser
```

After connecting, you'll see your `access_token` and `item_id` displayed in the terminal. You can then use these with the sync command.

### Option 2: Exchange Public Token (For Hosted Link or Manual Tokens)

If you have a `public_token` from Plaid Hosted Link or another source, exchange it:

```bash
python -m backend.app.api.cli exchange-token <public_token>
```

This will exchange the public token for an access token and display your credentials.

**Example:**
```bash
python -m backend.app.api.cli exchange-token public-sandbox-abc123...
```

### Option 3: Plaid Dashboard

You can also find access tokens in the Plaid Dashboard:
1. Go to [Plaid Dashboard](https://dashboard.plaid.com/)
2. Navigate to "Items" section
3. Find your connected bank account
4. Copy the `access_token` and `item_id`

## What to Do With the Token

Once you have an `access_token` and `item_id`:

```bash
python -m backend.app.api.cli sync --access-token <your_token> --item-id <your_item_id>
```

This will sync:
- Accounts
- Holdings (stocks, ETFs, etc.)
- Transactions

## Finding Your Token After Connection

If you've already connected an account through Plaid Link:
- The `access_token` is returned in the Plaid Link `onSuccess` callback
- You can also find it in the Plaid Dashboard under "Items"
- Each connected bank account has its own `access_token` and `item_id`

## Summary

**For Testing**: Use `python -m backend.app.api.cli get-token` (sandbox)

**For Real Accounts**: Use Plaid Link in a frontend, or use Plaid's Quickstart tool
