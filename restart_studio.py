#!/usr/bin/env python3
"""
Restart LangGraph Studio Server
"""

import os
import subprocess
import time
import signal

def kill_langgraph_processes():
    """Kill any existing langgraph dev processes."""
    print("🔪 Killing existing LangGraph processes...")
    
    try:
        # Use pkill to kill langgraph processes
        result = subprocess.run(['pkill', '-f', 'langgraph dev'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Killed existing LangGraph processes")
        else:
            print("✅ No LangGraph processes found to kill")
        
        time.sleep(2)  # Give processes time to terminate
        
    except Exception as e:
        print(f"⚠️  Error killing processes: {e}")
        print("✅ Continuing anyway...")

def start_langgraph_studio():
    """Start LangGraph Studio server."""
    print("🚀 Starting LangGraph Studio...")
    
    # Change to studio directory
    studio_dir = os.path.join(os.path.dirname(__file__), 'studio')
    os.chdir(studio_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if langgraph.json exists
    if not os.path.exists('langgraph.json'):
        print("❌ langgraph.json not found in studio directory")
        return False
    
    # Start langgraph dev server
    try:
        print("🔧 Starting langgraph dev --config langgraph.json...")
        process = subprocess.Popen(
            ['langgraph', 'dev', '--config', 'langgraph.json'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for the server to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ LangGraph Studio server started successfully!")
            print("🌐 Studio should be available at: http://localhost:8123")
            print("📋 Available graphs:")
            print("   - incident_response_enhanced")
            print("   - incident_response_with_mcp")
            print("   - incident_response_simple")
            print("   - investigator_agent")
            print("   - coordinator_agent")
            print("\n💡 Press Ctrl+C to stop the server")
            
            # Keep the process running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping LangGraph Studio...")
                process.terminate()
                process.wait()
                print("✅ LangGraph Studio stopped")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ LangGraph Studio failed to start")
            print(f"📄 stdout: {stdout}")
            print(f"📄 stderr: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ langgraph command not found. Please install langgraph-cli:")
        print("   pip install langgraph-cli")
        return False
    except Exception as e:
        print(f"❌ Error starting LangGraph Studio: {e}")
        return False

def main():
    """Main function to restart LangGraph Studio."""
    print("🔄 Restarting LangGraph Studio Server")
    print("=" * 50)
    
    # Kill existing processes
    kill_langgraph_processes()
    
    # Start new server
    success = start_langgraph_studio()
    
    if success:
        print("\n🎉 LangGraph Studio restart completed successfully!")
    else:
        print("\n❌ LangGraph Studio restart failed!")

if __name__ == "__main__":
    main()
