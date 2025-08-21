"""
Coordinator Agent for LangGraph Studio.
This graph demonstrates a coordinator agent that manages incident response workflow.
"""

import os
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import uuid

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()


# State definition
class CoordinatorState(TypedDict):
    """State for the coordinator agent workflow."""
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    assigned_agents: List[str]
    coordination_plan: Dict[str, Any]
    next_steps: List[str]
    messages: List[Dict[str, Any]]


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


async def initialize_coordination(state: CoordinatorState) -> CoordinatorState:
    """Initialize the coordination process and generate incident details."""
    print("👥 Initializing Coordination...")
    
    incident_id = state.get('incident_id', '')
    
    # Generate incident details using Circuit LLM
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
            "severity": "critical|high|medium|low"
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
                "severity": "high"
            }
        
        updated_state = state.copy()
        updated_state.update({
            'title': incident_details.get('title', f'Incident {incident_id}'),
            'description': incident_details.get('description', ''),
            'severity': incident_details.get('severity', 'medium'),
            'status': 'COORDINATING',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'assigned_agents': [],
            'coordination_plan': {},
            'next_steps': [],
            'messages': state.get('messages', []) + [{
                'role': 'system',
                'content': f'Coordinator agent initialized for {incident_id}.'
            }]
        })
        
        print(f"✅ Coordination initialized: {updated_state['incident_id']}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error initializing coordination: {e}")
        return state


async def analyze_incident(state: CoordinatorState) -> CoordinatorState:
    """Analyze the incident and determine required resources."""
    print("📊 Analyzing Incident...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Coordinator. Analyze the incident and determine required resources.
        """),
        ("human", """
        Incident: {title}
        Severity: {severity}
        Description: {description}
        
        Analyze and provide coordination plan as JSON:
        {{
            "required_agents": ["list", "of", "required", "agents"],
            "priority_level": "high|medium|low",
            "estimated_duration": "estimated time",
            "resource_requirements": ["list", "of", "resources"],
            "escalation_needed": true|false
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(
            title=state.get('title', 'Unknown'),
            severity=state.get('severity', 'Unknown'),
            description=state.get('description', 'No description')
        )
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"required_agents": [], "priority_level": "medium"}
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'ANALYZING',
            'updated_at': datetime.now(),
            'assigned_agents': result.get('required_agents', []),
            'coordination_plan': result,
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Analysis completed. Required agents: {', '.join(result.get('required_agents', []))}"
            }]
        })
        
        print(f"✅ Analysis completed: {len(updated_state['assigned_agents'])} agents required")
        return updated_state
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return state


async def create_action_plan(state: CoordinatorState) -> CoordinatorState:
    """Create an action plan based on analysis."""
    print("📋 Creating Action Plan...")
    
    coordination_plan = state.get('coordination_plan', {})
    assigned_agents = state.get('assigned_agents', [])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Coordinator. Create a detailed action plan.
        """),
        ("human", """
        Coordination Plan: {coordination_plan}
        Assigned Agents: {assigned_agents}
        
        Create action plan as JSON:
        {{
            "next_steps": ["list", "of", "next", "steps"],
            "timeline": "estimated timeline",
            "success_criteria": ["list", "of", "criteria"],
            "communication_plan": "communication strategy"
        }}
        """)
    ])
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "coordination_plan": str(coordination_plan),
            "assigned_agents": str(assigned_agents)
        })
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'PLANNING',
            'updated_at': datetime.now(),
            'next_steps': result.get('next_steps', []),
            'action_plan': result,
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Action plan created. Next steps: {len(result.get('next_steps', []))} steps defined"
            }]
        })
        
        print(f"✅ Action plan created: {len(updated_state['next_steps'])} steps")
        return updated_state
        
    except Exception as e:
        print(f"❌ Action plan error: {e}")
        return state


async def finalize_coordination(state: CoordinatorState) -> CoordinatorState:
    """Finalize the coordination process."""
    print("🏁 Finalizing Coordination...")
    
    updated_state = state.copy()
    updated_state.update({
        'status': 'COORDINATED',
        'updated_at': datetime.now(),
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': 'Coordination completed successfully. Ready for execution.'
        }]
    })
    
    print("✅ Coordination finalized")
    return updated_state


# Create the graph
def create_graph() -> StateGraph:
    """Create the coordinator agent graph."""
    
    workflow = StateGraph(CoordinatorState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_coordination)
    workflow.add_node("analyze", analyze_incident)
    workflow.add_node("plan", create_action_plan)
    workflow.add_node("finalize", finalize_coordination)
    
    # Define edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "analyze")
    workflow.add_edge("analyze", "plan")
    workflow.add_edge("plan", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# Create the graph instance
graph = create_graph()
