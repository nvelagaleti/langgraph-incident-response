#!/usr/bin/env python3
"""
Simple script to run LangGraph Studio development server
"""

import asyncio
import uvicorn
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Run the LangGraph Studio development server"""
    print("🚀 Starting LangGraph Studio Development Server...")
    print("=" * 50)
    
    # Check if langgraph.json exists
    config_file = Path("langgraph.json")
    if not config_file.exists():
        print("❌ langgraph.json not found in current directory")
        return
    
    print(f"✅ Found config: {config_file}")
    
    # Try to import and test our graphs
    try:
        from incident_response_enhanced import create_graph
        graph = create_graph()
        print("✅ Enhanced incident response graph loaded")
        
        from incident_response_basic import create_graph as create_basic_graph
        basic_graph = create_basic_graph()
        print("✅ Basic incident response graph loaded")
        
        print("\n🎉 All graphs loaded successfully!")
        print("📁 Studio directory is ready for development")
        
    except Exception as e:
        print(f"❌ Error loading graphs: {e}")
        return
    
    print("\n💡 Next steps:")
    print("1. Open your browser to http://localhost:8123")
    print("2. Select a graph to run")
    print("3. Provide incident data to test the workflow")
    print("4. Monitor the Circuit LLM-powered incident response process")

if __name__ == "__main__":
    main()
