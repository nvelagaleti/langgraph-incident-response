#!/usr/bin/env python3
"""
Get fresh Jira OAuth token with refresh token support
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_authorization_url():
    """Generate the authorization URL with refresh token support."""
    
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI")
    
    # Scopes for Jira access
    scopes = [
        "read:jira-work",
        "manage:jira-project", 
        "manage:jira-configuration",
        "read:jira-user",
        "write:jira-work",
        "manage:jira-webhook",
        "manage:jira-data-provider"
    ]
    
    # Authorization URL with offline_access for refresh token
    auth_url = (
        "https://auth.atlassian.com/authorize?"
        f"audience=api.atlassian.com&"
        f"client_id={client_id}&"
        f"scope={'%20'.join(scopes)}&"
        f"redirect_uri={redirect_uri}&"
        f"state=your-state-value&"
        f"response_type=code&"
        f"prompt=consent&"
        f"offline_access=true"  # Request refresh token
    )
    
    print("🔗 Jira OAuth Authorization URL (with refresh token support):")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print("\n📋 Instructions:")
    print("1. Copy and paste this URL into your browser")
    print("2. Complete the OAuth authorization")
    print("3. Copy the authorization code from the callback URL")
    print("4. Provide the authorization code when prompted")
    
    return auth_url

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access and refresh tokens."""
    
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI")
    
    print(f"\n🔄 Exchanging authorization code for tokens...")
    print(f"🔑 Authorization Code: {auth_code[:50]}...")
    
    token_url = "https://auth.atlassian.com/oauth/token"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    try:
        response = requests.post(token_url, headers=headers, json=data)
        
        if response.status_code == 200:
            tokens = response.json()
            
            print("✅ Token exchange successful!")
            print(f"🔑 Access Token: {tokens.get('access_token', 'N/A')[:50]}...")
            print(f"🔄 Refresh Token: {tokens.get('refresh_token', 'N/A')[:50]}...")
            print(f"⏰ Expires In: {tokens.get('expires_in', 'N/A')} seconds")
            print(f"📝 Token Type: {tokens.get('token_type', 'N/A')}")
            
            # Update .env file
            update_env_file(tokens)
            
            return tokens
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None

def update_env_file(tokens):
    """Update the .env file with new tokens."""
    try:
        # Read current .env file
        env_path = ".env"
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or add token lines
        token_updated = False
        refresh_token_updated = False
        
        for i, line in enumerate(lines):
            if line.startswith("JIRA_OAUTH_ACCESS_TOKEN="):
                lines[i] = f"JIRA_OAUTH_ACCESS_TOKEN={tokens.get('access_token', '')}\n"
                token_updated = True
            elif line.startswith("JIRA_OAUTH_REFRESH_TOKEN="):
                lines[i] = f"JIRA_OAUTH_REFRESH_TOKEN={tokens.get('refresh_token', '')}\n"
                refresh_token_updated = True
        
        # Add new lines if they don't exist
        if not token_updated:
            lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={tokens.get('access_token', '')}\n")
        if not refresh_token_updated and tokens.get('refresh_token'):
            lines.append(f"JIRA_OAUTH_REFRESH_TOKEN={tokens.get('refresh_token', '')}\n")
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print("✅ .env file updated with new tokens!")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

def main():
    """Main function to get fresh tokens."""
    print("🔄 Jira OAuth Token Refresh")
    print("=" * 60)
    
    # Generate authorization URL
    auth_url = get_authorization_url()
    
    # Get authorization code from user
    print(f"\n📝 Please provide the authorization code from the callback URL:")
    auth_code = input("Authorization Code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(auth_code)
    
    if tokens:
        print("\n🎉 Token refresh completed successfully!")
        print("🔧 You can now use the updated tokens in your applications.")
        
        if tokens.get('refresh_token'):
            print("🔄 Refresh token obtained - automatic renewal will be available!")
        else:
            print("⚠️  No refresh token received - manual renewal will be required")
    else:
        print("\n❌ Token refresh failed. Please check your credentials and try again.")

if __name__ == "__main__":
    main()
