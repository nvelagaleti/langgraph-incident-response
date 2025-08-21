#!/usr/bin/env python3
"""
Simple Jira OAuth Script
Get authorization code and exchange for access/refresh tokens
"""

import os
import asyncio
import json
import secrets
from urllib.parse import urlencode, parse_qs, urlparse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import requests
from dotenv import load_dotenv

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback."""
    
    def __init__(self, *args, auth_code_queue=None, **kwargs):
        self.auth_code_queue = auth_code_queue
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle OAuth callback."""
        query_components = parse_qs(urlparse(self.path).query)
        
        # Extract authorization code
        auth_code = query_components.get('code', [None])[0]
        state = query_components.get('state', [None])[0]
        error = query_components.get('error', [None])[0]
        
        if error:
            print(f"❌ OAuth error: {error}")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>OAuth Error</h1><p>Authorization failed.</p>")
            return
        
        if auth_code:
            print(f"✅ Authorization code received: {auth_code[:20]}...")
            if self.auth_code_queue:
                self.auth_code_queue.put(auth_code)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Success!</h1><p>Authorization successful. You can close this window.</p>")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Error</h1><p>No authorization code received.</p>")

class JiraOAuthSimple:
    """Simple Jira OAuth client."""
    
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("JIRA_OAUTH_CLIENT_ID", "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP")
        self.client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
        self.redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
        self.auth_url = "https://auth.atlassian.com/authorize"
        self.token_url = "https://auth.atlassian.com/oauth/token"
        
    def get_authorization_url(self, state=None):
        """Generate authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": "read:jira-work manage:jira-project manage:jira-configuration read:jira-user write:jira-work manage:jira-webhook manage:jira-data-provider",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent"
        }
        
        return f"{self.auth_url}?{urlencode(params)}", state
    
    def start_callback_server(self, port=8080):
        """Start HTTP server to handle OAuth callback."""
        auth_code_queue = asyncio.Queue()
        
        class Handler(OAuthCallbackHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, auth_code_queue=auth_code_queue, **kwargs)
        
        server = HTTPServer(('localhost', port), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        return server, auth_code_queue
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token."""
        print(f"🔄 Exchanging authorization code for tokens...")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            
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
                
                return token_data
            else:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"📄 Error response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error during token exchange: {e}")
            return None
    
    async def get_authorization_code(self):
        """Get authorization code through OAuth flow."""
        print("🔐 Jira OAuth Authorization Flow")
        print("=" * 50)
        
        if not self.client_secret:
            print("❌ Client secret not configured")
            print("💡 Please set JIRA_OAUTH_CLIENT_SECRET in your .env file")
            return None
        
        # Generate authorization URL
        auth_url, state = self.get_authorization_url()
        print(f"🔗 Authorization URL:")
        print(f"   {auth_url}")
        print(f"\n🔐 State: {state}")
        
        # Start callback server
        server, auth_code_queue = self.start_callback_server()
        print(f"🌐 Callback server started on port 8080")
        
        try:
            # Open browser for authorization
            print(f"\n🌐 Opening browser for authorization...")
            webbrowser.open(auth_url)
            
            # Wait for authorization code
            print(f"⏳ Waiting for authorization...")
            auth_code = await asyncio.wait_for(auth_code_queue.get(), timeout=300)  # 5 minutes timeout
            
            print(f"✅ Authorization code received!")
            return auth_code
            
        except asyncio.TimeoutError:
            print(f"❌ Authorization timeout")
            return None
        except Exception as e:
            print(f"❌ Error getting authorization code: {e}")
            return None
        finally:
            server.shutdown()

async def main():
    """Main function to get authorization code and exchange for tokens."""
    print("🚀 Jira OAuth Token Setup")
    print("=" * 60)
    
    oauth_client = JiraOAuthSimple()
    
    # Step 1: Get authorization code
    print("🔍 Step 1: Get Authorization Code")
    auth_code = await oauth_client.get_authorization_code()
    
    if not auth_code:
        print("❌ Failed to get authorization code")
        return
    
    # Step 2: Exchange code for tokens
    print(f"\n🔍 Step 2: Exchange Code for Access Token")
    token_data = oauth_client.exchange_code_for_token(auth_code)
    
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
    asyncio.run(main())
