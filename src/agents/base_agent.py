"""
Base agent class for the LangGraph Incident Response System.
Following patterns from LangChain Academy Module 4 & 5.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..types.state import (
    AgentRole,
    AgentProfile,
    Memory,
    MemoryCollection,
    IncidentState,
    InvestigationFinding,
    Recommendation
)


class BaseAgent(ABC):
    """
    Base agent class with memory capabilities and profile management.
    Following patterns from Module 5 (Memory Agent).
    """
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[str],
        llm: Optional[Any] = None,
        **kwargs
    ):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        
        # Initialize Circuit LLM if not provided
        if llm is None:
            try:
                from circuit_llm_client import CircuitLLMWrapper
                circuit_wrapper = CircuitLLMWrapper()
                
                class CircuitLLM:
                    def __init__(self, wrapper):
                        self.wrapper = wrapper
                    
                    async def invoke(self, input_text: str) -> str:
                        return await self.wrapper.invoke(input_text)
                    
                    async def ainvoke(self, input_text: str) -> str:
                        return await self.wrapper.ainvoke(input_text)
                
                self.llm = CircuitLLM(circuit_wrapper)
            except ImportError:
                # Fallback to OpenAI if Circuit LLM is not available
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        else:
            self.llm = llm
        
        # Initialize agent profile
        self.profile = AgentProfile(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            preferences=kwargs.get("preferences", {}),
            performance_metrics=kwargs.get("performance_metrics", {})
        )
        
        # Memory management
        self.memories: List[Memory] = []
        self.memory_collection: Optional[MemoryCollection] = None
        
        # Agent state
        self.current_task: Optional[str] = None
        self.task_history: List[Dict[str, Any]] = []
        
        # Initialize agent-specific prompts
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize agent-specific prompts."""
        self.system_prompt = self._get_system_prompt()
        self.task_prompt = self._get_task_prompt()
        self.memory_prompt = self._get_memory_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    @abstractmethod
    def _get_task_prompt(self) -> str:
        """Get the task-specific prompt for this agent."""
        pass
    
    def _get_memory_prompt(self) -> str:
        """Get the memory management prompt."""
        return """
        You are an agent with memory capabilities. You can:
        1. Save important information to memory
        2. Retrieve relevant memories when needed
        3. Update your profile based on experiences
        
        When you encounter important information, decide whether to save it to memory.
        Consider saving memories for:
        - Key findings and insights
        - Important decisions made
        - Patterns you've observed
        - Lessons learned from failures
        - Successful strategies used
        """
    
    def add_memory(self, content: str, source: str = "agent", tags: List[str] = None):
        """Add a memory to the agent's memory collection."""
        memory = Memory(
            content=content,
            timestamp=datetime.now(),
            source=source,
            tags=tags or []
        )
        self.memories.append(memory)
        
        if self.memory_collection:
            self.memory_collection.memories.append(memory)
            self.memory_collection.updated_at = datetime.now()
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Retrieve memories relevant to a query."""
        # Simple keyword-based retrieval for now
        # In a real implementation, this would use semantic search
        relevant_memories = []
        query_lower = query.lower()
        
        for memory in self.memories:
            if any(tag.lower() in query_lower for tag in memory.tags):
                relevant_memories.append(memory)
            elif any(word in memory.content.lower() for word in query_lower.split()):
                relevant_memories.append(memory)
        
        return relevant_memories[:limit]
    
    def update_profile(self, updates: Dict[str, Any]):
        """Update the agent's profile."""
        for key, value in updates.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        
        # Update performance metrics
        if "performance_metrics" in updates:
            self.profile.performance_metrics.update(updates["performance_metrics"])
    
    def get_context(self, state: IncidentState) -> Dict[str, Any]:
        """Get context for the agent based on current state."""
        context = {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "current_task": self.current_task,
            "relevant_memories": self.get_relevant_memories(state.get("description", "")),
            "incident_info": {
                "id": state.get("incident_id"),
                "title": state.get("title"),
                "severity": state.get("severity"),
                "affected_services": state.get("affected_services", [])
            }
        }
        return context
    
    async def process_task(self, state: IncidentState, task: str) -> Dict[str, Any]:
        """Process a task and return results."""
        self.current_task = task
        context = self.get_context(state)
        
        # Get relevant memories
        relevant_memories = self.get_relevant_memories(task)
        memory_context = "\n".join([m.content for m in relevant_memories])
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
            Task: {task}
            
            Current Context:
            {self._format_context(context)}
            
            Relevant Memories:
            {memory_context}
            
            Please process this task and provide your response.
            """)
        ]
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        
        # Parse response
        result = self._parse_response(response.content, task)
        
        # Update task history
        self.task_history.append({
            "task": task,
            "result": result,
            "timestamp": datetime.now()
        })
        
        # Add to memory if important
        if result.get("importance", 0) > 0.7:
            self.add_memory(
                content=f"Task: {task}\nResult: {result.get('summary', '')}",
                source="agent",
                tags=["task", "result"]
            )
        
        return result
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for LLM consumption."""
        formatted = []
        for key, value in context.items():
            if isinstance(value, dict):
                formatted.append(f"{key}: {self._format_context(value)}")
            elif isinstance(value, list):
                formatted.append(f"{key}: {', '.join(map(str, value))}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
    
    def _parse_response(self, response: str, task: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format."""
        # This is a simplified parser - in practice, you'd use structured output
        return {
            "task": task,
            "summary": response[:200] + "..." if len(response) > 200 else response,
            "full_response": response,
            "timestamp": datetime.now(),
            "agent_id": self.agent_id,
            "importance": 0.5  # Default importance
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's performance."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "tasks_completed": len(self.task_history),
            "memory_count": len(self.memories),
            "performance_metrics": self.profile.performance_metrics,
            "recent_tasks": self.task_history[-5:] if self.task_history else []
        }
    
    @abstractmethod
    async def execute(self, state: IncidentState) -> Dict[str, Any]:
        """Execute the agent's main logic."""
        pass
    
    def __str__(self):
        return f"{self.role.value.capitalize()}Agent({self.agent_id})"
    
    def __repr__(self):
        return self.__str__()


class AgentFactory:
    """Factory for creating agents."""
    
    _agents = {}
    
    @classmethod
    def register_agent(cls, role: AgentRole, agent_class: type):
        """Register an agent class for a role."""
        cls._agents[role] = agent_class
    
    @classmethod
    def create_agent(cls, role: AgentRole, agent_id: str, **kwargs) -> BaseAgent:
        """Create an agent instance."""
        if role not in cls._agents:
            raise ValueError(f"No agent registered for role: {role}")
        
        agent_class = cls._agents[role]
        return agent_class(agent_id=agent_id, role=role, **kwargs)
    
    @classmethod
    def get_available_roles(cls) -> List[AgentRole]:
        """Get list of available agent roles."""
        return list(cls._agents.keys())

