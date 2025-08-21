#!/usr/bin/env python3
"""
Verify OpenAI API Key Configuration
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

def verify_openai_key():
    """Verify that the OpenAI API key is working correctly."""
    
    print("🔑 Verifying OpenAI API Key Configuration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Make sure to set OPENAI_API_KEY in your .env file")
        return False
    
    # Check key format
    if not api_key.startswith(('sk-', 'sk-proj-')):
        print("❌ Invalid API key format")
        print(f"🔍 Key starts with: {api_key[:10]}...")
        print("💡 OpenAI keys should start with 'sk-' or 'sk-proj-'")
        print("🔧 Common issues:")
        print("   - Make sure you copied the full key from OpenAI")
        print("   - Check for extra spaces or characters")
        print("   - Ensure it's an OpenAI key, not from another service")
        print("   - Get a new key from: https://platform.openai.com/api-keys")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"🔍 Key length: {len(api_key)} characters")
    
    # Test API connection
    print("\n🧪 Testing API Connection...")
    
    try:
        # Initialize LLM with cheaper model for testing
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Cheaper model for testing
            temperature=0.1,
            api_key=api_key,
            max_retries=1,
            timeout=30
        )
        
        # Test simple API call
        print("📡 Making test API call...")
        response = llm.invoke("Hello! Please respond with 'API test successful'")
        
        if response and response.content:
            print(f"✅ API Response: {response.content}")
            print("🎉 OpenAI API key is working correctly!")
            return True
        else:
            print("❌ Empty response from API")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("💡 This indicates an invalid API key")
            print("🔧 Solutions:")
            print("   - Check your API key is correct")
            print("   - Ensure you have OpenAI credits/billing set up")
            print("   - Verify the key hasn't expired")
        elif "429" in error_str or "rate limit" in error_str:
            print("💡 Rate limit exceeded")
            print("🔧 Solutions:")
            print("   - Wait a moment and try again")
            print("   - Check your OpenAI usage limits")
        elif "timeout" in error_str:
            print("💡 Connection timeout")
            print("🔧 Solutions:")
            print("   - Check your internet connection")
            print("   - Try again in a moment")
        else:
            print("💡 Unexpected error")
            print("🔧 Solutions:")
            print("   - Check your internet connection")
            print("   - Verify OpenAI service status")
        
        return False

def check_environment_setup():
    """Check if all environment variables are properly set."""
    
    print("\n🌍 Checking Environment Setup...")
    print("=" * 50)
    
    load_dotenv()
    
    required_vars = {
        "OPENAI_API_KEY": "Required for LLM operations",
    }
    
    optional_vars = {
        "LANGSMITH_API_KEY": "Optional - for tracing and monitoring",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "Optional - for GitHub integration",
        "JIRA_OAUTH_TOKEN": "Optional - for Jira integration"
    }
    
    print("📋 Required Variables:")
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Set ({description})")
        else:
            print(f"   ❌ {var}: Not set ({description})")
            all_required_set = False
    
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Set ({description})")
        else:
            print(f"   ⚪ {var}: Not set ({description})")
    
    return all_required_set

if __name__ == "__main__":
    print("🎯 OpenAI API Key Verification Tool")
    print("This script will verify your OpenAI API key is working correctly.\n")
    
    # Check environment setup
    env_ok = check_environment_setup()
    
    if not env_ok:
        print("\n❌ Environment setup incomplete")
        print("💡 Please set the required environment variables and try again")
        exit(1)
    
    # Verify API key
    api_ok = verify_openai_key()
    
    print("\n" + "=" * 50)
    
    if api_ok:
        print("🎉 SUCCESS: OpenAI API key is working correctly!")
        print("✅ You can now run the enhanced incident response workflow")
        print("\n🚀 Next steps:")
        print("   1. Run: python3 run_enhanced_workflow.py")
        print("   2. Or use LangGraph Studio with the studio/ folder")
    else:
        print("❌ FAILED: OpenAI API key verification failed")
        print("🔧 Please fix the issues above and try again")
        exit(1)
