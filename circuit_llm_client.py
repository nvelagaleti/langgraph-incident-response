"""
Circuit LLM Client for Cisco's Internal LLM Service
This module provides integration with Cisco's Circuit LLM API.
"""

import os
import json
import base64
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CircuitLLMClient:
    """Client for Cisco's Circuit LLM API with OAuth2 authentication."""
    
    def __init__(self):
        # Circuit API configuration
        self.base_url = "https://chat-ai.cisco.com"
        self.auth_url = "https://id.cisco.com/oauth2/default/v1/token"
        self.client_id = os.getenv("CIRCUIT_CLIENT_ID")
        self.client_secret = os.getenv("CIRCUIT_CLIENT_SECRET")
        self.app_key = os.getenv("CIRCUIT_APP_KEY")
        self.model = os.getenv("CIRCUIT_MODEL", "gpt-4o-mini")
        self.api_version = "2025-04-01-preview"
        self.timeout = int(os.getenv("CIRCUIT_TIMEOUT", "30"))
        
        # Token management
        self.access_token = None
        self.token_expiry = None
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def _get_access_token(self) -> str:
        """Obtain OAuth2 access token using client credentials flow."""
        if not self.client_id or not self.client_secret:
            raise ValueError("CIRCUIT_CLIENT_ID and CIRCUIT_CLIENT_SECRET must be set in environment variables")
        
        # Base64 encode client_id:client_secret
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        data = "grant_type=client_credentials"
        
        try:
            response = await self.client.post(
                self.auth_url,
                headers=headers,
                content=data
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            if not self.access_token:
                raise ValueError("No access token received from authentication endpoint")
            
            # Set token expiry (tokens expire every hour)
            import time
            self.token_expiry = time.time() + 3600  # 1 hour from now
            
            return self.access_token
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"Authentication failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Authentication error: {str(e)}")
    
    async def _ensure_valid_token(self) -> str:
        """Ensure we have a valid access token, refreshing if necessary."""
        import time
        
        # Check if token is expired or will expire soon (within 5 minutes)
        if (not self.access_token or 
            not self.token_expiry or 
            time.time() > (self.token_expiry - 300)):
            await self._get_access_token()
        
        return self.access_token
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a chat completion request to Circuit LLM."""
        
        if not self.app_key:
            raise ValueError("CIRCUIT_APP_KEY must be set in environment variables")
        
        # Ensure we have a valid token
        access_token = await self._ensure_valid_token()
        
        # Use specified model or default
        model_name = model or self.model
        
        # Build user object
        user_obj = {"appkey": self.app_key}
        if user_id:
            user_obj["user"] = user_id
        if session_id:
            user_obj["session_id"] = session_id
        
        # Prepare request payload
        payload = {
            "messages": messages,
            "user": json.dumps(user_obj),
            "stop": ["<|im_end|>"]  # Empty stop array for continuous conversation
        }
        
        # Add optional parameters
        if temperature != 0.1:
            payload["temperature"] = temperature
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": access_token
        }
        
        # Build endpoint URL
        endpoint_url = f"{self.base_url}/openai/deployments/{model_name}/chat/completions"
        
        try:
            response = await self.client.post(
                endpoint_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request error: {str(e)}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using a simple prompt."""
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, **kwargs)
        
        # Extract the generated text from the response
        if response.get("choices") and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            raise Exception("No response content received")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class CircuitLLMWrapper:
    """LangChain-compatible wrapper for Circuit LLM."""
    
    def __init__(self):
        self.circuit_client = CircuitLLMClient()
        self.model = os.getenv("CIRCUIT_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("CIRCUIT_TEMPERATURE", "0.1"))
    
    async def invoke(self, input_text: str) -> str:
        """LangChain-compatible invoke method."""
        return await self.circuit_client.generate_text(
            input_text,
            temperature=self.temperature
        )
    
    async def ainvoke(self, input_text: str) -> str:
        """LangChain-compatible async invoke method."""
        return await self.invoke(input_text)
    
    async def close(self):
        """Close the client."""
        await self.circuit_client.close()


async def test_circuit_llm():
    """Test the Circuit LLM client."""
    print("🔧 Testing Circuit LLM Client...")
    
    # Check environment variables
    required_vars = ["CIRCUIT_CLIENT_ID", "CIRCUIT_CLIENT_SECRET", "CIRCUIT_APP_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Please set these in your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    try:
        # Test authentication
        print("🔐 Testing authentication...")
        client = CircuitLLMClient()
        token = await client._get_access_token()
        print(f"✅ Authentication successful! Token: {token[:20]}...")
        
        # Test chat completion
        print("💬 Testing chat completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Please respond with 'Circuit LLM is working!'"}
        ]
        
        response = await client.chat_completion(messages)
        print(f"✅ Chat completion successful!")
        print(f"📝 Response: {response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
        
        # Test text generation
        print("📝 Testing text generation...")
        text = await client.generate_text("Say 'Hello from Circuit LLM!'")
        print(f"✅ Text generation successful!")
        print(f"📝 Generated text: {text}")
        
        await client.close()
        print("🎉 All tests passed! Circuit LLM is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(test_circuit_llm())
