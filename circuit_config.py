"""
Circuit LLM Configuration Template
Please fill in the details from the Circuit API documentation.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Circuit LLM Configuration
CIRCUIT_BASE_URL = "https://chat-ai.cisco.com"
CIRCUIT_AUTH_URL = "https://id.cisco.com/oauth2/default/v1/token"
CIRCUIT_CLIENT_ID = os.getenv("CIRCUIT_CLIENT_ID", "")
CIRCUIT_CLIENT_SECRET = os.getenv("CIRCUIT_CLIENT_SECRET", "")
CIRCUIT_APP_KEY = os.getenv("CIRCUIT_APP_KEY", "")

# Model configuration
CIRCUIT_MODEL = os.getenv("CIRCUIT_MODEL", "gpt-4o-mini")
CIRCUIT_API_VERSION = "2025-04-01-preview"
CIRCUIT_TEMPERATURE = float(os.getenv("CIRCUIT_TEMPERATURE", "0.1"))
CIRCUIT_TIMEOUT = int(os.getenv("CIRCUIT_TIMEOUT", "30"))

# Available models
AVAILABLE_MODELS = {
    "gpt-4.1": {
        "context_window": "120K Tokens",
        "free_tier": True,
        "description": "GPT-4.1 model with 120K token context"
    },
    "gpt-4o-mini": {
        "context_window": "120K Tokens", 
        "free_tier": True,
        "description": "GPT-4o-mini model with 120K token context"
    },
    "gpt-4o": {
        "context_window": "120K Tokens",
        "free_tier": True, 
        "description": "GPT-4o model with 120K token context"
    },
    "o4-mini": {
        "context_window": "200K Tokens",
        "free_tier": False,
        "description": "O4-mini model with 200K token context"
    },
    "o3": {
        "context_window": "200K Tokens", 
        "free_tier": False,
        "description": "O3 model with 200K token context"
    },
    "gemini-2.5-flash": {
        "context_window": "1M Tokens",
        "free_tier": False,
        "description": "Gemini 2.5 Flash model with 1M token context"
    },
    "gemini-2.5-pro": {
        "context_window": "1M Tokens",
        "free_tier": False,
        "description": "Gemini 2.5 Pro model with 1M token context"
    }
}

def validate_configuration():
    """Validate the Circuit LLM configuration."""
    errors = []
    
    # Check required environment variables
    if not CIRCUIT_CLIENT_ID:
        errors.append("CIRCUIT_CLIENT_ID is not set")
    if not CIRCUIT_CLIENT_SECRET:
        errors.append("CIRCUIT_CLIENT_SECRET is not set")
    if not CIRCUIT_APP_KEY:
        errors.append("CIRCUIT_APP_KEY is not set")
    
    # Check if model is valid
    if CIRCUIT_MODEL not in AVAILABLE_MODELS:
        errors.append(f"Invalid model '{CIRCUIT_MODEL}'. Available models: {', '.join(AVAILABLE_MODELS.keys())}")
    
    # Check temperature range
    if not 0 <= CIRCUIT_TEMPERATURE <= 2:
        errors.append(f"Temperature must be between 0 and 2, got {CIRCUIT_TEMPERATURE}")
    
    # Check timeout
    if CIRCUIT_TIMEOUT <= 0:
        errors.append(f"Timeout must be positive, got {CIRCUIT_TIMEOUT}")
    
    return errors

def get_configuration():
    """Get the current configuration as a dictionary."""
    return {
        "base_url": CIRCUIT_BASE_URL,
        "auth_url": CIRCUIT_AUTH_URL,
        "client_id": CIRCUIT_CLIENT_ID,
        "client_secret": "***" if CIRCUIT_CLIENT_SECRET else None,
        "app_key": CIRCUIT_APP_KEY,
        "model": CIRCUIT_MODEL,
        "api_version": CIRCUIT_API_VERSION,
        "temperature": CIRCUIT_TEMPERATURE,
        "timeout": CIRCUIT_TIMEOUT,
        "available_models": list(AVAILABLE_MODELS.keys())
    }

def print_configuration():
    """Print the current configuration."""
    print("🔧 Circuit LLM Configuration:")
    print("=" * 50)
    
    config = get_configuration()
    
    print(f"Base URL: {config['base_url']}")
    print(f"Auth URL: {config['auth_url']}")
    print(f"Client ID: {config['client_id'] or '❌ Not set'}")
    print(f"Client Secret: {'✅ Set' if config['client_secret'] else '❌ Not set'}")
    print(f"App Key: {config['app_key'] or '❌ Not set'}")
    print(f"Model: {config['model']}")
    print(f"API Version: {config['api_version']}")
    print(f"Temperature: {config['temperature']}")
    print(f"Timeout: {config['timeout']} seconds")
    
    print(f"\n📋 Available Models:")
    for model, info in AVAILABLE_MODELS.items():
        free_tier = "✅ Free" if info['free_tier'] else "❌ Paid"
        print(f"  • {model}: {info['context_window']} ({free_tier})")
    
    # Validate configuration
    errors = validate_configuration()
    if errors:
        print(f"\n❌ Configuration Errors:")
        for error in errors:
            print(f"  • {error}")
        return False
    else:
        print(f"\n✅ Configuration is valid!")
        return True

def create_env_template():
    """Create a template .env file for Circuit LLM."""
    template = """# Circuit LLM Configuration
# Get these credentials from Cisco's API request form
CIRCUIT_CLIENT_ID=your_client_id_here
CIRCUIT_CLIENT_SECRET=your_client_secret_here
CIRCUIT_APP_KEY=your_app_key_here

# Model configuration (optional)
CIRCUIT_MODEL=gpt-4o-mini
CIRCUIT_TEMPERATURE=0.1
CIRCUIT_TIMEOUT=30
"""
    
    with open(".env.circuit.template", "w") as f:
        f.write(template)
    
    print("📝 Created .env.circuit.template file")
    print("💡 Copy this to .env and fill in your actual credentials")

if __name__ == "__main__":
    print_configuration()
    print("\n" + "=" * 50)
    create_env_template()
