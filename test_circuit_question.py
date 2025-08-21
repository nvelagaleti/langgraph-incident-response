#!/usr/bin/env python3
"""
Test Circuit LLM with a specific question.
"""

import asyncio
import json
from circuit_llm_client import CircuitLLMClient, CircuitLLMWrapper

async def test_circuit_question():
    """Test Circuit LLM with the question 'What is LLM'."""
    print("🔧 Testing Circuit LLM with: 'What is LLM'")
    print("=" * 60)
    
    try:
        # Test 1: Direct client test
        print("📡 Test 1: Direct Circuit Client")
        print("-" * 30)
        
        client = CircuitLLMClient()
        
        # Test authentication first
        print("🔐 Authenticating...")
        token = await client._get_access_token()
        print(f"✅ Token obtained: {token[:20]}...")
        
        # Test chat completion
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Provide clear and informative explanations."},
            {"role": "user", "content": "What is LLM? Please provide a brief explanation."}
        ]
        
        print("💬 Sending chat completion request...")
        response = await client.chat_completion(messages)
        
        print(f"📊 Raw response structure:")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if response.get("choices"):
            print(f"Number of choices: {len(response['choices'])}")
            for i, choice in enumerate(response["choices"]):
                print(f"Choice {i} keys: {list(choice.keys()) if isinstance(choice, dict) else 'Not a dict'}")
                if isinstance(choice, dict) and "message" in choice:
                    message = choice["message"]
                    print(f"Message keys: {list(message.keys()) if isinstance(message, dict) else 'Not a dict'}")
                    content = message.get("content", "")
                    print(f"Content length: {len(content)}")
                    print(f"Content type: {type(content)}")
                    if content:
                        print(f"✅ Circuit LLM Response:")
                        print(f"{content}")
                        print("-" * 60)
                    else:
                        print(f"⚠️  Content is empty")
        else:
            print(f"⚠️  No 'choices' in response")
            print(f"Full response: {json.dumps(response, indent=2)}")
        
        await client.close()
        
        # Test 2: LangChain wrapper test
        print("\n🔗 Test 2: LangChain Wrapper")
        print("-" * 30)
        
        wrapper = CircuitLLMWrapper()
        
        print("💬 Testing with wrapper...")
        try:
            wrapper_response = await wrapper.invoke("What is LLM? Please explain briefly.")
            print(f"✅ Wrapper Response:")
            print(f"{wrapper_response}")
        except Exception as e:
            print(f"❌ Wrapper error: {str(e)}")
        
        await wrapper.close()
        
        # Test 3: Simple text generation
        print("\n📝 Test 3: Simple Text Generation")
        print("-" * 30)
        
        client2 = CircuitLLMClient()
        try:
            text_response = await client2.generate_text("What is LLM?")
            print(f"✅ Text Generation Response:")
            print(f"{text_response}")
        except Exception as e:
            print(f"❌ Text generation error: {str(e)}")
        
        await client2.close()
        
        print("\n🎉 Circuit LLM testing completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_circuit_question())
