#!/usr/bin/env python3
"""
Quick script to exchange user-provided authorization code for tokens
"""

import requests
import json
import os
from dotenv import load_dotenv

def exchange_auth_code_for_tokens(auth_code: str):
    """Exchange authorization code for access and refresh tokens."""
    
    # Load environment variables
    load_dotenv()
    
    # OAuth configuration
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID", "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    
    # Token exchange URL
    token_url = "https://auth.atlassian.com/oauth/token"
    
    # Request data
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    print("🔄 Exchanging authorization code for tokens...")
    print(f"🔑 Authorization Code: {auth_code[:20]}...")
    print(f"🔧 Client ID: {client_id}")
    print(f"🌐 Redirect URI: {redirect_uri}")
    
    try:
        # Make the token exchange request
        response = requests.post(token_url, data=data)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            tokens = response.json()
            
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            
            print("✅ Token exchange successful!")
            print(f"🔑 Access Token: {access_token[:20]}...")
            if refresh_token:
                print(f"🔄 Refresh Token: {refresh_token[:20]}...")
            
            # Update .env file
            update_env_file(access_token, refresh_token)
            
            return access_token, refresh_token
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None, None

def update_env_file(access_token: str, refresh_token: str = None):
    """Update .env file with new tokens."""
    
    env_file = ".env"
    
    # Read existing .env file
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update or add token lines
    token_updated = False
    refresh_updated = False
    
    for i, line in enumerate(lines):
        if line.startswith("JIRA_OAUTH_ACCESS_TOKEN="):
            lines[i] = f"JIRA_OAUTH_ACCESS_TOKEN={access_token}\n"
            token_updated = True
        elif line.startswith("JIRA_OAUTH_REFRESH_TOKEN="):
            lines[i] = f"JIRA_OAUTH_REFRESH_TOKEN={refresh_token or ''}\n"
            refresh_updated = True
    
    # Add missing lines
    if not token_updated:
        lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={access_token}\n")
    if not refresh_updated and refresh_token:
        lines.append(f"JIRA_OAUTH_REFRESH_TOKEN={refresh_token}\n")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"💾 Updated {env_file} with new tokens")
    
    # Also update studio/.env if it exists
    studio_env_file = "studio/.env"
    if os.path.exists(studio_env_file):
        with open(studio_env_file, 'w') as f:
            f.writelines(lines)
        print(f"💾 Updated {studio_env_file} with new tokens")

if __name__ == "__main__":
    # Use the authorization code provided by the user
    auth_code = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJhMTYwNGY4Yy0xODcxLTQ0N2UtOGMzZS1hM2JkNTU5NjA3NTYiLCJzdWIiOiI3MDEyMTpjZmQxOWQyNy1iNGM1LTQwNTMtYjFkMS02NWRkMTgyYWMyNzgiLCJuYmYiOjE3NTU3NTk4OTMsImlzcyI6ImF1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTc1NTc1OTg5MywiZXhwIjoxNzU1NzYwMTkzLCJhdWQiOiJJUnBUa1NZUnFZMnNQYzJGeGhIT0pHcGliNGtsS3BYUCIsImNsaWVudF9hdXRoX3R5cGUiOiJQT1NUIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3ZlcmlmaWVkIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdWp0IjoiYTE2MDRmOGMtMTg3MS00NDdlLThjM2UtYTNiZDU1OTYwNzU2Iiwic2NvcGUiOlsibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiIsIm1hbmFnZTpqaXJhLWRhdGEtcHJvdmlkZXIiLCJtYW5hZ2U6amlyYS1wcm9qZWN0IiwibWFuYWdlOmppcmEtd2ViaG9vayIsInJlYWQ6amlyYS11c2VyIiwicmVhZDpqaXJhLXdvcmsiLCJ3cml0ZTpqaXJhLXdvcmsiXSwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2F0bF90b2tlbl90eXBlIjoiQVVUSF9DT0RFIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2hhc1JlZGlyZWN0VXJpIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vc2Vzc2lvbl9pZCI6IjVkODNhY2Q3LTc3MTAtNDkxZS05ZDA1LTk5NDk0ODMxZDg1MiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIn0.8VUMv3hWhWmjg08DBSZLb6wFUPhxYAkDfg9NhNWGhQ8"
    
    print("🚀 Exchanging User-Provided Authorization Code for Tokens")
    print("=" * 60)
    
    access_token, refresh_token = exchange_auth_code_for_tokens(auth_code)
    
    if access_token:
        print("\n✅ Success! New tokens have been saved to .env file")
        print("🔄 You can now restart the LangGraph Studio server")
    else:
        print("\n❌ Failed to exchange authorization code")
        print("💡 The authorization code may have expired. Please get a fresh one.")
