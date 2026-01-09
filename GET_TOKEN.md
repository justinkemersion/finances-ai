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

For real bank accounts, you need to use **Plaid Link** - their frontend component that handles the OAuth flow. Here's the process:

### Option 1: Use Plaid's Quickstart (Easiest)

1. Go to [Plaid Quickstart](https://plaid.com/docs/quickstart/)
2. They provide a simple HTML page with Plaid Link embedded
3. Connect your bank account through their interface
4. You'll get an `access_token` in the response

### Option 2: Build Your Own Frontend

1. Add Plaid Link to your frontend (React, Vue, vanilla JS, etc.)
2. User clicks "Connect Bank"
3. Plaid Link opens, user authenticates
4. You receive `access_token` and `item_id` in the callback
5. Use those to sync data

### Option 3: Use Plaid's API Directly (Advanced)

You can create items programmatically, but this requires handling the OAuth flow yourself.

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
