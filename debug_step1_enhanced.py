#!/usr/bin/env python3
"""
Debug Step 1 function from incident_response_enhanced.py to see why it's failing.
"""

import asyncio
import os
from dotenv import load_dotenv

async def debug_step1_enhanced():
    """Debug the step1_parse_ir_ticket function specifically."""
    print("🔍 Debugging Step 1 from incident_response_enhanced.py")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Import the specific function
        from studio.incident_response_enhanced import step1_parse_ir_ticket, IncidentInput
        
        # Create test state with existing incident ID
        test_state = IncidentInput(
            incident_id="IR-1"
        )
        
        print(f"🔍 Testing with incident ID: {test_state.get('incident_id')}")
        print("🔄 Calling step1_parse_ir_ticket...")
        
        # Call the function
        result = await step1_parse_ir_ticket(test_state)
        
        print("✅ Function completed!")
        print(f"📋 Title: {result.get('title', 'N/A')}")
        print(f"📄 Description: {result.get('description', 'N/A')[:100]}...")
        print(f"🚨 Severity: {result.get('severity', 'N/A')}")
        print(f"📋 Status: {result.get('status', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in step1_parse_ir_ticket: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(debug_step1_enhanced())
