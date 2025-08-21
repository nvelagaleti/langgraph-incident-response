# Circuit LLM Setup Guide

## 🎯 **Overview**
This guide helps you configure the Circuit LLM integration for the incident response system using Cisco's internal LLM service.

## 📋 **Required Information from API Documentation**

Please extract the following details from the Circuit API documentation:

### **1. API Endpoints**
- **Base URL**: The main API endpoint (e.g., `https://api.cisco.com/circuit/v1`)
- **Chat Completions Endpoint**: Where to send chat requests (e.g., `/chat/completions`)
- **Health Check Endpoint**: For testing connectivity (e.g., `/health`)

### **2. Authentication**
- **Authentication Method**: How to authenticate (Bearer token, API key, OAuth, etc.)
- **API Key Format**: How the API key should be formatted
- **Required Headers**: Any additional headers needed

### **3. Request Format**
- **Model Names**: Available model names (e.g., `gpt-4`, `gpt-3.5-turbo`)
- **Required Fields**: What fields are required in the request
- **Optional Fields**: What optional parameters are supported

### **4. Response Format**
- **Response Structure**: How the API response is structured
- **Content Location**: Where the generated text is located in the response

## 🔧 **Configuration Steps**

### **Step 1: Update Environment Variables**
Add the following to your `.env` file:

```bash
# Circuit LLM Configuration
CIRCUIT_API_URL=https://your-circuit-api-url.com
CIRCUIT_API_KEY=your_circuit_api_key_here
CIRCUIT_MODEL=gpt-4
CIRCUIT_TIMEOUT=30
CIRCUIT_TEMPERATURE=0.1
CIRCUIT_MAX_TOKENS=1000
CIRCUIT_AUTH_TYPE=bearer
```

### **Step 2: Update Configuration File**
Edit `circuit_config.py` with the details from the API documentation:

```python
# Update these values based on the Circuit API documentation
CIRCUIT_API_URL = "https://your-actual-api-url.com"
CHAT_COMPLETIONS_ENDPOINT = "/your-chat-endpoint"
AUTH_TYPE = "your-auth-method"
```

### **Step 3: Test the Configuration**
Run the configuration validation:

```bash
python3 circuit_config.py
```

### **Step 4: Test Circuit LLM**
Test the Circuit LLM integration:

```bash
python3 circuit_llm_client.py
```

## 🧪 **Testing Process**

### **1. Configuration Test**
```bash
python3 circuit_config.py
```
This will validate your configuration settings.

### **2. Circuit LLM Test**
```bash
python3 circuit_llm_client.py
```
This will test the actual API connection and response.

### **3. Enhanced Workflow Test**
Once Circuit LLM is working, test the full workflow:

```bash
python3 run_enhanced_workflow.py
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Authentication Errors**
   - Check API key format
   - Verify authentication method
   - Ensure proper headers

2. **Connection Errors**
   - Check network connectivity
   - Verify API URL
   - Check firewall settings

3. **Request Format Errors**
   - Verify request structure
   - Check required fields
   - Validate model names

4. **Response Parsing Errors**
   - Check response format
   - Verify content location
   - Validate JSON structure

### **Debug Steps:**

1. **Check Configuration**
   ```bash
   python3 circuit_config.py
   ```

2. **Test API Connection**
   ```bash
   python3 circuit_llm_client.py
   ```

3. **Check Environment Variables**
   ```bash
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CIRCUIT_API_KEY:', 'Set' if os.getenv('CIRCUIT_API_KEY') else 'Not set')"
   ```

## 📞 **Support**

If you encounter issues:

1. **Check the API documentation** for the correct endpoints and formats
2. **Verify your network access** to the Circuit API
3. **Test with a simple curl command** to verify API connectivity
4. **Check the error messages** in the test output

## 🎉 **Success Criteria**

The Circuit LLM integration is working when:

- ✅ Configuration validation passes
- ✅ API connection test succeeds
- ✅ Text generation works correctly
- ✅ Enhanced workflow runs without errors

## 🚀 **Next Steps**

Once Circuit LLM is configured and working:

1. **Run the enhanced incident response workflow**
2. **Test with real IR ticket scenarios**
3. **Integrate with your Jira and GitHub systems**
4. **Deploy in LangGraph Studio**

---

**Need Help?** Please provide the specific error messages or issues you encounter, and I'll help you troubleshoot them!
