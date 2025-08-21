#!/usr/bin/env python3
"""
Exchange authorization code for access token and refresh token.
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

async def exchange_auth_code():
    """Exchange authorization code for tokens."""
    print("🚀 Exchanging Authorization Code for Tokens")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Authorization code from user
    auth_code = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2YTc4YTdjYi1kOGEzLTRkMDctOGNlZi1hN2RiZmMzODhkZDciLCJzdWIiOiI3MDEyMTpjZmQxOWQyNy1iNGM1LTQwNTMtYjFkMS02NWRkMTgyYWMyNzgiLCJuYmYiOjE3NTU3NjU2NTEsImlzcyI6ImF1dGguYXRsYXNzaWFuLmNvbSIsImlhdCI6MTc1NTc2NTY1MSwiZXhwIjoxNzU1NzY1OTUxLCJhdWQiOiJJUnBUa1NZUnFZMnNQYzJGeGhIT0pHcGliNGtsS3BYUCIsImNsaWVudF9hdXRoX3R5cGUiOiJQT1NUIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3ZlcmlmaWVkIjp0cnVlLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vdWp0IjoiNmE3OGE3Y2ItZDhhMy00ZDA3LThjZWYtYTdkYmZjMzg4ZGQ3Iiwic2NvcGUiOlsibWFuYWdlOmppcmEtY29uZmlndXJhdGlvbiIsIm1hbmFnZTpqaXJhLXByb2plY3QiLCJtYW5hZ2U6amlyYS13ZWJob29rIiwicmVhZDpqaXJhLXVzZXIiLCJyZWFkOmppcmEtd29yayIsIndyaXRlOmppcmEtd29yayJdLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vYXRsX3Rva2VuX3R5cGUiOiJBVVRIX0NPREUiLCJodHRwczovL2lkLmF0bGFzc2lhbi5jb20vaGFzUmVkaXJlY3RVcmkiOnRydWUsImh0dHBzOi8vaWQuYXRsYXNzaWFuLmNvbS9zZXNzaW9uX2lkIjoiNWQ4M2FjZDctNzcxMC00OTFlLTlkMDUtOTk0OTQ4MzFkODUyIiwiaHR0cHM6Ly9pZC5hdGxhc3NpYW4uY29tL3Byb2Nlc3NSZWdpb24iOiJ1cy13ZXN0LTIifQ.qAUYRgeTuzKwKzDdyptPhmv-AuWy4urLaeFJNgfUXYc"
    
    # OAuth configuration
    client_id = os.getenv('JIRA_OAUTH_CLIENT_ID')
    client_secret = os.getenv('JIRA_OAUTH_CLIENT_SECRET')
    redirect_uri = os.getenv('JIRA_OAUTH_REDIRECT_URI', 'http://localhost:8080/callback')
    
    print(f"🔑 Authorization Code: {auth_code[:20]}...")
    print(f"🔧 Client ID: {client_id}")
    print(f"🌐 Redirect URI: {redirect_uri}")
    
    if not all([auth_code, client_id, client_secret]):
        print("❌ Missing required OAuth configuration")
        return False
    
    # Exchange authorization code for tokens
    token_url = "https://auth.atlassian.com/oauth/token"
    
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
        print("🔄 Exchanging authorization code for tokens...")
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                tokens = response.json()
                
                access_token = tokens.get('access_token')
                refresh_token = tokens.get('refresh_token')
                
                print("✅ Token exchange successful!")
                print(f"🔑 Access Token: {access_token[:50]}...")
                if refresh_token:
                    print(f"🔄 Refresh Token: {refresh_token[:50]}...")
                
                # Update .env file
                await update_env_file(access_token, refresh_token)
                
                return True
            else:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"📄 Error response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

async def update_env_file(access_token, refresh_token):
    """Update the .env file with new tokens."""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Update access token
        if 'JIRA_OAUTH_ACCESS_TOKEN=' in env_content:
            env_content = env_content.replace(
                env_content.split('JIRA_OAUTH_ACCESS_TOKEN=')[1].split('\n')[0],
                access_token
            )
        else:
            env_content += f"\nJIRA_OAUTH_ACCESS_TOKEN={access_token}"
        
        # Update refresh token if available
        if refresh_token:
            if 'JIRA_OAUTH_REFRESH_TOKEN=' in env_content:
                env_content = env_content.replace(
                    env_content.split('JIRA_OAUTH_REFRESH_TOKEN=')[1].split('\n')[0],
                    refresh_token
                )
            else:
                env_content += f"\nJIRA_OAUTH_REFRESH_TOKEN={refresh_token}"
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file updated with new tokens")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    success = asyncio.run(exchange_auth_code())
    if not success:
        print("\n❌ Token refresh failed. Please check the error messages above.")
    else:
        print("\n✅ Token refresh completed successfully!")
