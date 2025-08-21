#!/usr/bin/env python3
"""
Exchange Authorization Code for Tokens
Simple script to exchange the authorization code for access and refresh tokens
"""

import os
import json
import requests
from dotenv import load_dotenv

def exchange_code_for_token(auth_code, client_id, client_secret, redirect_uri):
    """Exchange authorization code for access token."""
    print(f"🔄 Exchanging authorization code for tokens...")
    
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
    
    try:
        response = requests.post("https://auth.atlassian.com/oauth/token", data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            
            print(f"✅ Token exchange successful!")
            print(f"📄 Response: {json.dumps(token_data, indent=2)}")
            
            # Extract and display tokens
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            token_type = token_data.get("token_type", "Bearer")
            expires_in = token_data.get("expires_in")
            
            print(f"\n🎉 TOKENS OBTAINED:")
            print(f"=" * 50)
            print(f"🔑 Access Token: {access_token}")
            print(f"🔄 Refresh Token: {refresh_token}")
            print(f"📋 Token Type: {token_type}")
            print(f"⏰ Expires In: {expires_in} seconds")
            print(f"=" * 50)
            
            # Save to environment variables
            os.environ["JIRA_OAUTH_ACCESS_TOKEN"] = access_token
            if refresh_token:
                os.environ["JIRA_OAUTH_REFRESH_TOKEN"] = refresh_token
            
            print(f"\n💾 Tokens saved to environment variables:")
            print(f"   JIRA_OAUTH_ACCESS_TOKEN")
            print(f"   JIRA_OAUTH_REFRESH_TOKEN")
            
            # Save to .env file
            with open('.env', 'a') as f:
                f.write(f"\n# OAuth Tokens (Generated)\n")
                f.write(f"JIRA_OAUTH_ACCESS_TOKEN={access_token}\n")
                if refresh_token:
                    f.write(f"JIRA_OAUTH_REFRESH_TOKEN={refresh_token}\n")
            
            print(f"\n💾 Tokens also saved to .env file")
            
            return token_data
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None

def main():
    """Main function to exchange the authorization code."""
    print("🚀 Exchange Authorization Code for Tokens")
    print("=" * 60)
    
    load_dotenv()
    
    # Configuration
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID", "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    
    if not client_secret:
        print("❌ Client secret not configured")
        print("💡 Please set JIRA_OAUTH_CLIENT_SECRET in your .env file")
        return
    
    # The authorization code we received
    auth_code = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlZTFhYjk0ZS05ZTQwLTRhN2YtYWQxNC1jMGJkZWEyMmYwMWYiLCJzdWIiOiI3MDEyMTpjZmQxOWQyNy1iNGM1LTQwNTMtYjFkMS02NWRkMTgyYWMyNzgiLCJuYmYiOjE3NTU3MjU4MzUsImlzcyI6ImF1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTc1NTcyNTgzNSwiZXhwIjoxNzU1NzI2MTM1LCJhdWQiOiJJUnBUa1NZUnFZMnNQYzJGeGhIT0pHcGliNGtsS3BYUCIsImNsaWVudF9hdXRoX3R5cGUiOiJQT1NUIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3ZlcmlmaWVkIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdWp0IjoiZWUxYWI5NGUtOWU0MC00YTdmLWFkMTQtYzBiZGVhMjJmMDFmIiwic2NvcGUiOlsibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiIsIm1hbmFnZTpqaXJhLWRhdGEtcHJvdmlkZXIiLCJtYW5hZ2U6amlyYS1wcm9qZWN0IiwibWFuYWdlOmppcmEtd2ViaG9vayIsInJlYWQ6amlyYS11c2VyIiwicmVhZDpqaXJhLXdvcmsiLCJ3cml0ZTpqaXJhLXdvcmsiXSwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2F0bF90b2tlbl90eXBlIjoiQVVUSF9DT0RFIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2hhc1JlZGlyZWN0VXJpIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vc2Vzc2lvbl9pZCI6IjVkODNhY2Q3LTc3MTAtNDkxZS05ZDA1LTk5NDk0ODMxZDg1MiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIn0.XzEVyd4BJybbEthPbI0WfJU1DckXaqcHGcUo6VNBej0"
    
    print(f"🔑 Authorization Code: {auth_code[:50]}...")
    print(f"🔧 Client ID: {client_id}")
    print(f"🌐 Redirect URI: {redirect_uri}")
    
    # Exchange code for tokens
    token_data = exchange_code_for_token(auth_code, client_id, client_secret, redirect_uri)
    
    if token_data:
        print(f"\n🎊 SUCCESS! OAuth tokens obtained successfully!")
        print(f"🚀 Ready to use with Jira MCP integration!")
        
        # Show usage example
        print(f"\n📋 Usage Example:")
        print(f"   # Add to your .env file:")
        print(f"   JIRA_OAUTH_ACCESS_TOKEN={token_data.get('access_token')}")
        print(f"   JIRA_OAUTH_REFRESH_TOKEN={token_data.get('refresh_token')}")
        
    else:
        print(f"\n❌ Failed to exchange code for tokens")

if __name__ == "__main__":
    main()
