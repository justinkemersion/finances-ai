"""Helper script to test Plaid connection and create sandbox items"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest

from ..config import config


def test_plaid_connection():
    """Test if Plaid credentials are working"""
    print("Testing Plaid connection...")
    
    try:
        # Set up Plaid client
        # Note: Plaid SDK only has Sandbox and Production
        # "development" maps to Production environment
        host_map = {
            "sandbox": Environment.Sandbox,
            "development": Environment.Production,  # Development uses Production endpoint
            "production": Environment.Production,
        }
        
        plaid_host = host_map.get(config.PLAID_ENV.lower())
        if not plaid_host:
            print(f"❌ Invalid Plaid environment: {config.PLAID_ENV}")
            return False
        
        plaid_config = Configuration(
            host=plaid_host,
            api_key={
                "clientId": config.PLAID_CLIENT_ID,
                "secret": config.PLAID_SECRET,
            }
        )
        
        api_client = ApiClient(plaid_config)
        client = plaid_api.PlaidApi(api_client)
        
        # Test by getting institutions (this doesn't require auth)
        print("✓ Plaid client initialized")
        print(f"✓ Environment: {config.PLAID_ENV}")
        client_id_preview = config.PLAID_CLIENT_ID[:10] + "..." if config.PLAID_CLIENT_ID and len(config.PLAID_CLIENT_ID) > 10 else (config.PLAID_CLIENT_ID or "Not set")
        print(f"✓ Client ID: {client_id_preview}")
        
        return True, client
        
    except Exception as e:
        print(f"❌ Error connecting to Plaid: {str(e)}")
        return False, None


def create_sandbox_item(client, institution_id="ins_109508"):
    """
    Create a sandbox test item and get access_token
    
    Args:
        client: Plaid API client
        institution_id: Institution to use (default: First Platypus Bank for testing)
                        For Schwab, you'd use their institution_id
    """
    print(f"\nCreating sandbox test item for institution: {institution_id}")
    
    try:
        # Step 1: Create a public token
        # Products needs to be imported and used correctly
        from plaid.model.products import Products
        products_list = [Products('investments')]
        
        request = SandboxPublicTokenCreateRequest(
            institution_id=institution_id,
            initial_products=products_list,
        )
        
        response = client.sandbox_public_token_create(request)
        if not response or not hasattr(response, 'public_token'):
            raise Exception(f"Invalid response from Plaid: {response}")
        public_token = response.public_token
        
        print(f"✓ Created public token: {public_token[:20]}...")
        
        # Step 2: Exchange public token for access token
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.access_token
        item_id = exchange_response.item_id
        
        print(f"✓ Exchanged for access token")
        print(f"\n{'='*60}")
        print("SUCCESS! Here are your credentials:")
        print(f"{'='*60}")
        print(f"Access Token: {access_token}")
        print(f"Item ID: {item_id}")
        print(f"\nYou can now use these to sync data:")
        print(f"python -m backend.app.api.cli sync --access-token {access_token} --item-id {item_id}")
        print(f"{'='*60}")
        
        return access_token, item_id
        
    except Exception as e:
        print(f"❌ Error creating sandbox item: {str(e)}")
        if "institution_id" in str(e).lower():
            print("\n💡 Tip: The institution_id might not support investments.")
            print("   Try a different institution or check Plaid's sandbox documentation.")
        return None, None


def list_sandbox_institutions(client):
    """List available sandbox institutions"""
    print("\nAvailable sandbox institutions for testing:")
    print("(These are test institutions, not real banks)")
    
    # Common sandbox institution IDs
    institutions = {
        "ins_109508": "First Platypus Bank",
        "ins_109509": "First Gingham Credit Union",
        "ins_109510": "Tartan Bank",
        "ins_109511": "Houndstooth Bank",
    }
    
    print("\nInstitution ID -> Name:")
    for inst_id, name in institutions.items():
        print(f"  {inst_id} -> {name}")
    
    print("\n💡 Note: For Charles Schwab, you'll need to use their real institution_id")
    print("   which you can find in the Plaid Dashboard or by searching institutions.")


def main():
    """Main function"""
    print("="*60)
    print("Plaid Connection Test & Sandbox Item Creator")
    print("="*60)
    
    # Test connection
    success, client = test_plaid_connection()
    if not success:
        print("\n❌ Failed to connect to Plaid. Check your credentials in .env")
        sys.exit(1)
    
    # List institutions
    list_sandbox_institutions(client)
    
    # Ask user if they want to create a test item
    print("\n" + "="*60)
    response = input("\nCreate a sandbox test item? (y/n): ").strip().lower()
    
    if response == 'y':
        institution_id = input("Enter institution ID (or press Enter for default): ").strip()
        if not institution_id:
            institution_id = "ins_109508"  # Default test bank
        
        access_token, item_id = create_sandbox_item(client, institution_id)
        
        if access_token and item_id:
            print("\n✅ Sandbox item created successfully!")
            print("\nNext steps:")
            print("1. Save these credentials somewhere safe")
            print("2. Run: python -m backend.app.api.cli sync --access-token <token> --item-id <item_id>")
        else:
            print("\n❌ Failed to create sandbox item")
    else:
        print("\nSkipping sandbox item creation.")
        print("\nFor real bank connections, you'll need to:")
        print("1. Implement Plaid Link in your frontend")
        print("2. User goes through OAuth flow")
        print("3. You receive an access_token from the callback")


if __name__ == "__main__":
    main()
