"""
Simplified Incident Response Agent for LangGraph Studio.
This agent only requires an incident_id and generates a complete incident response.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime, timedelta
import uuid
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()


# Simplified State definition - only requires incident_id
class SimpleIncidentState(TypedDict):
    """Simplified state for incident response workflow."""
    # Only required input
    incident_id: str
    
    # Generated during workflow
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Analysis results
    root_cause_analysis: Dict[str, Any]
    action_items: List[Dict[str, Any]]
    recommendations: List[str]
    
    # Messages and tracking
    messages: List[Dict[str, Any]]
    completed_steps: List[str]


# Circuit LLM setup
from circuit_llm_client import CircuitLLMWrapper

# Initialize Circuit LLM wrapper
circuit_llm_wrapper = CircuitLLMWrapper()

# Create a LangChain-compatible LLM interface
class CircuitLLM:
    """LangChain-compatible interface for Circuit LLM."""
    
    def __init__(self, wrapper: CircuitLLMWrapper):
        self.wrapper = wrapper
    
    async def invoke(self, input_text: str) -> str:
        """Invoke Circuit LLM with input text."""
        return await self.wrapper.invoke(input_text)
    
    async def ainvoke(self, input_text: str) -> str:
        """Async invoke Circuit LLM with input text."""
        return await self.wrapper.ainvoke(input_text)

# Initialize the LLM
llm = CircuitLLM(circuit_llm_wrapper)


async def step1_generate_incident_details(state: SimpleIncidentState) -> SimpleIncidentState:
    """Step 1: Generate incident details from incident_id."""
    print("📋 Step 1: Generating Incident Details...")
    
    incident_id = state.get('incident_id', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Generate realistic incident details based on the incident ID.
        Create a plausible incident scenario that could occur in a software system.
        """),
        ("human", """
        Incident ID: {incident_id}
        
        Generate incident details as JSON:
        {{
            "title": "string",
            "description": "string", 
            "severity": "critical|high|medium|low",
            "status": "open|investigating|resolved",
            "created_at": "ISO datetime string",
            "updated_at": "ISO datetime string"
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(incident_id=incident_id)
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            incident_details = json.loads(json_match.group())
        else:
            # Fallback
            incident_details = {
                "title": f"Incident {incident_id}",
                "description": "System performance degradation detected",
                "severity": "high",
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        updated_state = state.copy()
        updated_state.update({
            'title': incident_details.get('title', f'Incident {incident_id}'),
            'description': incident_details.get('description', ''),
            'severity': incident_details.get('severity', 'medium'),
            'status': incident_details.get('status', 'open'),
            'created_at': datetime.fromisoformat(incident_details.get('created_at', datetime.now().isoformat())),
            'updated_at': datetime.fromisoformat(incident_details.get('updated_at', datetime.now().isoformat())),
            'completed_steps': ['step1_generate_incident_details'],
            'messages': [{
                'role': 'assistant',
                'content': f"Generated incident details for {incident_id}"
            }]
        })
        
        print(f"✅ Generated incident: {incident_details.get('title', 'Unknown')}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error generating incident details: {e}")
        return state


async def step2_analyze_root_cause(state: SimpleIncidentState) -> SimpleIncidentState:
    """Step 2: Analyze root cause based on incident details."""
    print("🔍 Step 2: Analyzing Root Cause...")
    
    title = state.get('title', '')
    description = state.get('description', '')
    severity = state.get('severity', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Analyze the incident and identify the root cause.
        Consider common software issues like configuration changes, memory leaks, network issues, etc.
        """),
        ("human", """
        Incident Title: {title}
        Description: {description}
        Severity: {severity}
        
        Provide root cause analysis as JSON:
        {{
            "root_cause": "string",
            "contributing_factors": ["list", "of", "factors"],
            "timeline": "string",
            "confidence": 0.0-1.0,
            "evidence": ["list", "of", "evidence"]
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(
            title=title,
            description=description,
            severity=severity
        )
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            rca = json.loads(json_match.group())
        else:
            # Fallback
            rca = {
                "root_cause": "Configuration change in backend service",
                "contributing_factors": ["Recent deployment", "Memory pressure"],
                "timeline": "Issue started 2 hours ago",
                "confidence": 0.8,
                "evidence": ["Error logs", "Performance metrics"]
            }
        
        updated_state = state.copy()
        updated_state.update({
            'root_cause_analysis': rca,
            'completed_steps': state.get('completed_steps', []) + ['step2_analyze_root_cause'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Root cause identified: {rca.get('root_cause', 'Unknown')}"
            }]
        })
        
        print(f"✅ Root cause: {rca.get('root_cause', 'Unknown')}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error analyzing root cause: {e}")
        return state


async def step3_generate_actions(state: SimpleIncidentState) -> SimpleIncidentState:
    """Step 3: Generate action items and recommendations."""
    print("📋 Step 3: Generating Action Items...")
    
    rca = state.get('root_cause_analysis', {})
    severity = state.get('severity', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Generate actionable items and recommendations based on the root cause analysis.
        Focus on immediate actions, short-term fixes, and long-term prevention.
        """),
        ("human", """
        Root Cause: {root_cause}
        Contributing Factors: {factors}
        Severity: {severity}
        
        Generate action items as JSON:
        {{
            "action_items": [
                {{
                    "action": "string",
                    "priority": "high|medium|low",
                    "category": "immediate|short_term|long_term",
                    "assignee": "string",
                    "estimated_effort": "string",
                    "description": "string"
                }}
            ],
            "immediate_actions": ["list", "of", "immediate", "actions"],
            "prevention_measures": ["list", "of", "prevention", "measures"]
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(
            root_cause=rca.get('root_cause', 'Unknown'),
            factors=str(rca.get('contributing_factors', [])),
            severity=severity
        )
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            actions = json.loads(json_match.group())
        else:
            # Fallback
            actions = {
                "action_items": [
                    {
                        "action": "Rollback recent configuration changes",
                        "priority": "high",
                        "category": "immediate",
                        "assignee": "DevOps Team",
                        "estimated_effort": "30 minutes",
                        "description": "Revert the configuration that caused the issue"
                    }
                ],
                "immediate_actions": ["Rollback configuration", "Monitor system"],
                "prevention_measures": ["Add configuration validation", "Improve monitoring"]
            }
        
        updated_state = state.copy()
        updated_state.update({
            'action_items': actions.get('action_items', []),
            'recommendations': actions.get('immediate_actions', []) + actions.get('prevention_measures', []),
            'completed_steps': state.get('completed_steps', []) + ['step3_generate_actions'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Generated {len(actions.get('action_items', []))} action items"
            }]
        })
        
        print(f"✅ Generated {len(actions.get('action_items', []))} action items")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error generating actions: {e}")
        return state


async def step4_finalize_incident(state: SimpleIncidentState) -> SimpleIncidentState:
    """Step 4: Finalize the incident response."""
    print("✅ Step 4: Finalizing Incident Response...")
    
    incident_id = state.get('incident_id', '')
    title = state.get('title', '')
    rca = state.get('root_cause_analysis', {})
    action_items = state.get('action_items', [])
    
    updated_state = state.copy()
    updated_state.update({
        'status': 'resolved',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step4_finalize_incident'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Incident {incident_id} response completed. Root cause: {rca.get('root_cause', 'Unknown')}. {len(action_items)} action items generated."
        }]
    })
    
    print(f"✅ Incident {incident_id} response completed")
    return updated_state


def create_graph():
    """Create the simplified incident response graph."""
    
    # Create the graph
    workflow = StateGraph(SimpleIncidentState)
    
    # Add nodes
    workflow.add_node("step1_generate_incident_details", step1_generate_incident_details)
    workflow.add_node("step2_analyze_root_cause", step2_analyze_root_cause)
    workflow.add_node("step3_generate_actions", step3_generate_actions)
    workflow.add_node("step4_finalize_incident", step4_finalize_incident)
    
    # Define the flow
    workflow.set_entry_point("step1_generate_incident_details")
    workflow.add_edge("step1_generate_incident_details", "step2_analyze_root_cause")
    workflow.add_edge("step2_analyze_root_cause", "step3_generate_actions")
    workflow.add_edge("step3_generate_actions", "step4_finalize_incident")
    workflow.add_edge("step4_finalize_incident", END)
    
    # Compile the graph
    graph = workflow.compile()
    
    return graph


# Create the graph instance
graph = create_graph()
