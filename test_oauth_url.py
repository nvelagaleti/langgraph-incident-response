#!/usr/bin/env python3
"""
Test OAuth URL Generation
Simple test to verify the authorization URL is generated correctly
"""

import os
import secrets
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_oauth_url_generation():
    """Test OAuth URL generation."""
    print("🧪 Testing OAuth URL Generation")
    print("=" * 50)
    
    load_dotenv()
    
    # Configuration
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID", "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    auth_url = "https://auth.atlassian.com/authorize"
    
    # Generate state
    state = secrets.token_urlsafe(32)
    
    # Build parameters
    params = {
        "audience": "api.atlassian.com",
        "client_id": client_id,
        "scope": "read:jira-work manage:jira-project manage:jira-configuration read:jira-user write:jira-work manage:jira-webhook manage:jira-data-provider",
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code",
        "prompt": "consent"
    }
    
    # Generate URL
    authorization_url = f"{auth_url}?{urlencode(params)}"
    
    print(f"✅ OAuth URL generated successfully!")
    print(f"\n🔗 Authorization URL:")
    print(f"   {authorization_url}")
    print(f"\n📋 URL Components:")
    print(f"   Base URL: {auth_url}")
    print(f"   Client ID: {client_id}")
    print(f"   Redirect URI: {redirect_uri}")
    print(f"   State: {state}")
    print(f"   Scopes: {params['scope']}")
    
    # Verify it matches the provided URL pattern
    expected_pattern = "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP"
    
    if authorization_url.startswith(expected_pattern):
        print(f"\n✅ URL matches expected pattern!")
        print(f"✅ Ready for OAuth flow!")
    else:
        print(f"\n⚠️  URL pattern verification failed")
    
    return authorization_url, state

def test_token_exchange_format():
    """Test token exchange request format."""
    print(f"\n🧪 Testing Token Exchange Format")
    print("=" * 50)
    
    # Mock data for testing
    auth_code = "mock_authorization_code_123"
    client_id = "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP"
    client_secret = "your_client_secret_here"
    redirect_uri = "http://localhost:8080/callback"
    
    # Build token exchange request
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"✅ Token exchange request format:")
    print(f"   URL: https://auth.atlassian.com/oauth/token")
    print(f"   Method: POST")
    print(f"   Headers: {headers}")
    print(f"   Data: {data}")
    
    print(f"\n📋 Expected Response Format:")
    print(f"   {{")
    print(f"     'access_token': 'your_access_token_here',")
    print(f"     'refresh_token': 'your_refresh_token_here',")
    print(f"     'token_type': 'Bearer',")
    print(f"     'expires_in': 3600")
    print(f"   }}")
    
    return data, headers

if __name__ == "__main__":
    # Test URL generation
    auth_url, state = test_oauth_url_generation()
    
    # Test token exchange format
    data, headers = test_token_exchange_format()
    
    print(f"\n🎉 All tests completed!")
    print(f"🚀 Ready to run the full OAuth script!")
