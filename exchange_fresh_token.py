#!/usr/bin/env python3
"""
Exchange fresh authorization code for access token
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def exchange_authorization_code():
    """Exchange authorization code for access token."""
    
    # The fresh authorization code you provided
    auth_code = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1MGJmZjMxMS1hODUxLTQwZmEtYWVjMC02MzE1YjVhOWUwMmIiLCJzdWIiOiI3MDEyMTpjZmQxOWQyNy1iNGM1LTQwNTMtYjFkMS02NWRkMTgyYWMyNzgiLCJuYmYiOjE3NTU3OTA5MzEsImlzcyI6ImF1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTc1NTc5MDkzMSwiZXhwIjoxNzU1NzkxMjMxLCJhdWQiOiJJUnBUa1NZUnFZMnNQYzJGeGhIT0pHcGliNGtsS3BYUCIsImNsaWVudF9hdXRoX3R5cGUiOiJQT1NUIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3ZlcmlmaWVkIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdWp0IjoiNTBiZmYzMTEtYTg1MS00MGZhLWFlYzAtNjMxNWI1YTllMDJiIiwic2NvcGUiOlsibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiIsIm1hbmFnZTpqaXJhLWRhdGEtcHJvdmlkZXIiLCJtYW5hZ2U6amlyYS1wcm9qZWN0IiwibWFuYWdlOmppcmEtd2ViaG9vayIsInJlYWQ6amlyYS11c2VyIiwicmVhZDpqaXJhLXdvcmsiLCJ3cml0ZTpqaXJhLXdvcmsiXSwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2F0bF90b2tlbl90eXBlIjoiQVVUSF9DT0RFIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL2hhc1JlZGlyZWN0VXJpIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vc2Vzc2lvbl9pZCI6IjVkODNhY2Q3LTc3MTAtNDkxZS05ZDA1LTk5NDk0ODMxZDg1MiIsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9wcm9jZXNzUmVnaW9uIjoidXMtd2VzdC0yIn0.VLloO-TVNjJoTjQmgqe0u8U9awTjZxhuFw6Q8JwXeqw"
    
    # Get credentials from environment
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI")
    
    print("🚀 Exchange Fresh Authorization Code for Tokens")
    print("=" * 60)
    print(f"🔑 Authorization Code: {auth_code[:50]}...")
    print(f"🔧 Client ID: {client_id}")
    print(f"🌐 Redirect URI: {redirect_uri}")
    
    # Prepare the token exchange request
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
    
    print("🔄 Exchanging authorization code for tokens...")
    
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
        # Update main .env file
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
        
        print("✅ Main .env file updated with new tokens!")
        
        # Update studio/.env file
        studio_env_path = "studio/.env"
        if os.path.exists(studio_env_path):
            with open(studio_env_path, 'r') as f:
                studio_lines = f.readlines()
            
            # Update or add token lines
            studio_token_updated = False
            studio_refresh_token_updated = False
            
            for i, line in enumerate(studio_lines):
                if line.startswith("JIRA_OAUTH_ACCESS_TOKEN="):
                    studio_lines[i] = f"JIRA_OAUTH_ACCESS_TOKEN={tokens.get('access_token', '')}\n"
                    studio_token_updated = True
                elif line.startswith("JIRA_OAUTH_REFRESH_TOKEN="):
                    studio_lines[i] = f"JIRA_OAUTH_REFRESH_TOKEN={tokens.get('refresh_token', '')}\n"
                    studio_refresh_token_updated = True
            
            # Add new lines if they don't exist
            if not studio_token_updated:
                studio_lines.append(f"JIRA_OAUTH_ACCESS_TOKEN={tokens.get('access_token', '')}\n")
            if not studio_refresh_token_updated and tokens.get('refresh_token'):
                studio_lines.append(f"JIRA_OAUTH_REFRESH_TOKEN={tokens.get('refresh_token', '')}\n")
            
            # Write back to studio/.env file
            with open(studio_env_path, 'w') as f:
                f.writelines(studio_lines)
            
            print("✅ Studio .env file updated with new tokens!")
        else:
            print("⚠️  Studio .env file not found, skipping update")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    tokens = exchange_authorization_code()
    if tokens:
        print("\n🎉 Token exchange completed successfully!")
        print("🔧 You can now use the updated tokens in your applications.")
    else:
        print("\n❌ Token exchange failed. Please check your credentials and try again.")
