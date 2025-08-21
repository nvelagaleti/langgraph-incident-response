#!/usr/bin/env python3
"""
Generate a new Jira OAuth authorization URL.
"""

import os
from dotenv import load_dotenv
import urllib.parse

def generate_auth_url():
    """Generate a new Jira OAuth authorization URL."""
    print("🔗 Generating New Jira OAuth Authorization URL")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get OAuth configuration
    client_id = os.getenv('JIRA_OAUTH_CLIENT_ID')
    redirect_uri = os.getenv('JIRA_OAUTH_REDIRECT_URI', 'http://localhost:8080/callback')
    
    if not client_id:
        print("❌ JIRA_OAUTH_CLIENT_ID not found in .env file")
        return False
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Define the scopes needed for Jira
    scopes = [
        "read:jira-user",
        "read:jira-work",
        "write:jira-work",
        "manage:jira-project",
        "manage:jira-configuration",
        "manage:jira-webhook"
    ]
    
    # Build the authorization URL
    base_url = "https://auth.atlassian.com/authorize"
    params = {
        "audience": "api.atlassian.com",
        "client_id": client_id,
        "scope": " ".join(scopes),
        "redirect_uri": redirect_uri,
        "state": "jira_oauth_state",
        "response_type": "code",
        "prompt": "consent"
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print("\n🔗 Authorization URL Generated:")
    print("=" * 60)
    print(auth_url)
    print("=" * 60)
    
    print("\n📋 Instructions:")
    print("1. Copy the URL above and paste it in your browser")
    print("2. Log in to your Atlassian account")
    print("3. Grant the requested permissions")
    print("4. You'll be redirected to a URL with an authorization code")
    print("5. Copy the authorization code from the URL")
    print("6. Use the authorization code with the exchange script")
    
    return auth_url

if __name__ == "__main__":
    generate_auth_url()
