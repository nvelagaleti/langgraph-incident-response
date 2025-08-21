#!/usr/bin/env python3
"""
Debug script to test step2 repository selection for frontend incident
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the studio directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'studio'))

# Import the step2 function and related classes
from incident_response_enhanced import step2_identify_first_repo, IncidentState

async def debug_step2_frontend_incident():
    """Debug step2 with the frontend incident data."""
    print("🔍 Debugging Step 2 Repository Selection for Frontend Incident")
    print("=" * 80)
    
    # Create test state with the frontend incident data
    test_state = IncidentState(
        incident_id="IR-1",
        title="Products Web Application - GraphQL Service Connection Failure",
        description="Customer reports UI failure when attempting to view product data. Web application loads successfully but fails to display product information. Users are experiencing timeout errors when trying to access the products page.",
        severity="medium",
        status="open",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        completed_steps=['step1_parse_ir_ticket'],
        messages=[]
    )
    
    print(f"🔍 Test incident:")
    print(f"  Title: {test_state['title']}")
    print(f"  Description: {test_state['description']}")
    print(f"  Severity: {test_state['severity']}")
    print()
    
    try:
        # Call step2 function
        print("🔄 Calling step2_identify_first_repo...")
        result = await step2_identify_first_repo(test_state)
        
        print("\n✅ Step 2 completed!")
        print("\n📊 Results:")
        print(f"  First Repo: {result.get('first_repo', 'N/A')}")
        print(f"  All Repos: {result.get('all_repos', [])}")
        
        # Check repo analysis
        repo_analysis = result.get('repo_analysis', {})
        if repo_analysis:
            print(f"\n🔍 Repository Analysis:")
            print(f"  Search Strategy: {repo_analysis.get('search_strategy', {})}")
            print(f"  Found Repos: {repo_analysis.get('found_repos', [])}")
            print(f"  Main Repository: {repo_analysis.get('main_repository', 'N/A')}")
            print(f"  Related Repositories: {repo_analysis.get('related_repositories', [])}")
            print(f"  Reasoning: {repo_analysis.get('reasoning', 'N/A')}")
        
        # Check if the correct repository was selected
        first_repo = result.get('first_repo', '')
        if 'productsWebApp' in first_repo:
            print(f"\n✅ SUCCESS: Correctly identified productsWebApp as main repository!")
        else:
            print(f"\n❌ ISSUE: Incorrectly identified {first_repo} instead of productsWebApp")
            print(f"   Expected: productsWebApp (frontend incident)")
            print(f"   Got: {first_repo}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in step2: {e}")
        import traceback
        traceback.print_exc()
        return None

async def debug_search_keywords():
    """Debug the search keyword generation for frontend incident."""
    print("\n🔍 Debugging Search Keyword Generation")
    print("=" * 50)
    
    # Test the search keyword generation logic
    title = "Products Web Application - GraphQL Service Connection Failure"
    description = "Customer reports UI failure when attempting to view product data. Web application loads successfully but fails to display product information."
    
    print(f"🔍 Incident:")
    print(f"  Title: {title}")
    print(f"  Description: {description}")
    print()
    
    # Expected keywords for frontend incident
    expected_keywords = ["products", "frontend", "ui", "web", "app", "graphql"]
    
    print(f"🔍 Expected keywords for frontend incident: {expected_keywords}")
    print()
    
    # Test if the LLM would generate appropriate keywords
    try:
        from incident_response_enhanced import llm
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a GitHub repository analyst for incident response. Based on the incident description, identify search keywords.
            """),
            ("human", """
            Incident Analysis:
            - Title: {title}
            - Description: {description}
            
            Generate search keywords as JSON array: ["keyword1", "keyword2", "keyword3"]
            Focus on frontend/UI keywords for UI incidents.
            """)
        ])
        
        formatted_prompt = prompt.format_messages(title=title, description=description)
        response = await llm.invoke(formatted_prompt[-1].content)
        
        print(f"🔍 LLM Response: {response}")
        
        # Parse keywords
        import re
        import json
        
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            keywords = json.loads(json_match.group())
            print(f"🔍 Parsed keywords: {keywords}")
            
            # Check if keywords are appropriate for frontend
            frontend_keywords = [kw for kw in keywords if any(frontend in kw.lower() for frontend in ['frontend', 'ui', 'web', 'app', 'react'])]
            if frontend_keywords:
                print(f"✅ Found frontend keywords: {frontend_keywords}")
            else:
                print(f"⚠️  No frontend keywords found in: {keywords}")
        else:
            print(f"⚠️  Could not parse keywords from response")
            
    except Exception as e:
        print(f"❌ Error testing keyword generation: {e}")

async def main():
    """Run debug tests."""
    print("🚀 Debugging Step 2 Repository Selection")
    print("=" * 80)
    
    # Test 1: Full step2 execution
    result = await debug_step2_frontend_incident()
    
    # Test 2: Search keyword generation
    await debug_search_keywords()
    
    print("\n" + "=" * 80)
    print("🎉 Debugging completed!")

if __name__ == "__main__":
    asyncio.run(main())
