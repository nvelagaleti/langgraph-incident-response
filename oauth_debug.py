#!/usr/bin/env python3
"""
OAuth Debug - Test different configurations
"""

import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_oauth_configuration():
    """Test OAuth configuration and identify issues."""
    print("🔍 OAuth Configuration Debug")
    print("=" * 50)
    
    load_dotenv()
    
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    
    print(f"✅ Client ID: {client_id[:10] if client_id else 'Missing'}...")
    print(f"✅ Client Secret: {'Configured' if client_secret else 'Missing'}")
    
    # Test different redirect URIs
    redirect_uris = [
        "http://localhost:8080/callback",
        "http://localhost:3000/callback", 
        "http://127.0.0.1:8080/callback",
        "https://oauth.pstmn.io/v1/callback"  # Postman OAuth callback
    ]
    
    scopes = [
        "read:jira-work",
        "write:jira-work", 
        "read:jira-user",
        "manage:jira-project"
    ]
    
    print(f"\n🔹 Testing Different Redirect URIs")
    print("-" * 30)
    
    for redirect_uri in redirect_uris:
        print(f"\n🔍 Testing: {redirect_uri}")
        
        params = {
            "audience": "api.atlassian.com",
            "client_id": client_id,
            "scope": ",".join(scopes),
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "prompt": "consent"
        }
        
        auth_url = f"https://auth.atlassian.com/authorize?{urlencode(params)}"
        
        print(f"🔗 Authorization URL:")
        print(f"   {auth_url}")
        print(f"📋 Instructions:")
        print(f"   1. Copy this URL")
        print(f"   2. Open in browser")
        print(f"   3. Try to log in")
        print(f"   4. Note any errors")
        
        # Ask user to test
        test = input(f"\n⏳ Test this URL? (y/n): ").strip().lower()
        if test == 'y':
            print(f"🌐 Opening browser...")
            import webbrowser
            webbrowser.open(auth_url)
            
            result = input(f"📋 What happened? (success/error): ").strip().lower()
            if result == 'success':
                print(f"✅ This redirect URI works!")
                return redirect_uri
            else:
                print(f"❌ This redirect URI failed")
    
    return None

def test_direct_api_approach():
    """Test direct API approach as alternative."""
    print(f"\n🔹 Testing Direct API Approach")
    print("-" * 30)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {'Configured' if jira_token else 'Missing'}")
    print(f"✅ Jira Email: {jira_email or 'Missing'}")
    
    if jira_url and jira_token:
        print(f"💡 Direct API approach available")
        print(f"   - No OAuth complexity")
        print(f"   - Works with API tokens")
        print(f"   - Can handle multiple projects")
        return True
    else:
        print(f"❌ Direct API approach not configured")
        return False

def main():
    """Main debug function."""
    print("🧪 OAuth Debug")
    print("=" * 60)
    
    # Test OAuth configuration
    working_redirect_uri = test_oauth_configuration()
    
    if working_redirect_uri:
        print(f"\n🎉 Found working redirect URI: {working_redirect_uri}")
        print(f"💡 Update your .env file with this redirect URI")
    else:
        print(f"\n⚠️  No working redirect URI found")
    
    # Test direct API approach
    direct_api_available = test_direct_api_approach()
    
    # Recommendations
    print(f"\n📋 Recommendations:")
    print("=" * 30)
    
    if working_redirect_uri:
        print(f"✅ Use OAuth with redirect URI: {working_redirect_uri}")
    elif direct_api_available:
        print(f"✅ Use Direct API approach (simpler)")
        print(f"   - No OAuth complexity")
        print(f"   - Just need API token")
    else:
        print(f"❌ Both approaches have issues")
        print(f"💡 Check your Atlassian app configuration")

if __name__ == "__main__":
    main()
