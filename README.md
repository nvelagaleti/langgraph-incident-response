# LangGraph Incident Response System

A sophisticated multi-agent incident response system built with LangGraph, following patterns from LangChain Academy Module 4 (Multi-agent with Subgraphs and Parallelization) and Module 5 (Memory Management).

## 🎯 Overview

This system demonstrates advanced LangGraph concepts for automated incident response:

- **Multi-agent Architecture**: Specialized agents (Coordinator, Investigator, Analyst, Communicator, Executor)
- **Parallel Execution**: Subgraphs running simultaneously for investigation, analysis, and communication
- **Memory Management**: Persistent memory for learning and context retention
- **State Management**: Comprehensive state tracking with checkpointing
- **Root Cause Analysis**: Automated investigation and correlation of evidence
- **Real MCP Integration**: Direct access to GitHub and Jira using Model Context Protocol

## 🏗️ Architecture

### Core Components

```
langgraph-incident-response/
├── src/
│   ├── types/
│   │   └── state.py              # State definitions and data models
│   ├── agents/
│   │   ├── base_agent.py         # Base agent with memory capabilities
│   │   └── coordinator_agent.py  # Coordinator agent for workflow management
│   ├── graphs/
│   │   ├── main_graph.py         # Main incident response workflow
│   │   └── subgraphs.py          # Parallel subgraphs for specialized tasks
│   └── main.py                   # Demo and entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

### Agent Roles

1. **Coordinator Agent**: Orchestrates the entire incident response workflow
2. **Investigator Agent**: Performs root cause analysis and evidence collection
3. **Analyst Agent**: Analyzes data patterns and correlations
4. **Communicator Agent**: Manages stakeholder communication and notifications
5. **Executor Agent**: Implements fixes and actions

### Subgraphs

- **Investigation Subgraph**: Log analysis, git commit analysis, evidence correlation
- **Analysis Subgraph**: Performance analysis, pattern recognition, correlation identification
- **Communication Subgraph**: Stakeholder identification, notification management, escalation
- **Execution Subgraph**: Action planning, resource allocation, implementation

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (for LLM integration)
- GitHub Personal Access Token (for real Git data)
- Jira API Token (for real Jira integration)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd langgraph-incident-response
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your credentials
   nano .env
   ```

4. **Configure External MCP Servers (No Local Installation Required!):**
   ```bash
   # Set external MCP server URLs in .env
   MCP_GITHUB_SERVER_URL=https://your-github-mcp-server.com
   MCP_JIRA_SERVER_URL=https://your-jira-mcp-server.com
   
   # Or use GitHub's official MCP server (if available)
   MCP_GITHUB_SERVER_URL=https://api.github.com/mcp
   ```

5. **Test External MCP Integration:**
   ```bash
   # Test LangChain MCP client
   python test_langchain_mcp.py
   ```

6. **Run the demo:**
   ```bash
   python -m src.main
   ```

## 📋 Demo Scenarios

### 1. OOM Incident Simulation

The main demo simulates a realistic incident scenario:

```
🚨 Incident: GraphQL Service Out of Memory Error
📊 Severity: HIGH
🔧 Affected Services: productsGraphQLService, productsWebApp, productsBackendService

Root Cause: Backend configuration change triggers memory leak in GraphQL service
Impact: UI crashes, customer-facing application unavailable
```

### 2. Memory Capabilities Demo

Demonstrates the system's memory management:

- Persistent memory across incident responses
- Context retention and learning
- Memory-based decision making

### 3. Parallel Execution Demo

Shows parallel processing capabilities:

- Simultaneous investigation, analysis, and communication
- Subgraph coordination
- Performance optimization

## 🔧 Key Features

### Multi-Agent Coordination

```python
# Coordinator manages workflow
coordinator = CoordinatorAgent(agent_id="coordinator-001")
result = await coordinator.execute(incident_state)
```

### Parallel Subgraphs

```python
# Investigation subgraph
investigation_graph = create_investigation_subgraph()
investigation_result = await investigation_graph.ainvoke(investigation_state)

# Analysis subgraph  
analysis_graph = create_analysis_subgraph()
analysis_result = await analysis_graph.ainvoke(analysis_state)
```

### Memory Management

```python
# Add memory
agent.add_memory(
    content="Key finding: Memory leak detected",
    source="investigator",
    tags=["memory", "finding"]
)

# Retrieve relevant memories
memories = agent.get_relevant_memories("memory leak")
```

### State Management

```python
# Comprehensive state tracking
incident_state = IncidentState(
    incident_id="INC-2024-001",
    title="GraphQL Service OOM",
    severity=IncidentSeverity.HIGH,
    findings=[],
    recommendations=[],
    memories=MemoryCollection(...),
    context={}
)
```

### LangChain MCP Adapters Integration

```python
# External MCP server connections via URLs
servers_config = {
    "github": {
        "transport": "streamable_http",
        "url": "https://your-github-mcp-server.com",
        "headers": {"Authorization": f"Bearer {github_token}"}
    },
    "jira": {
        "transport": "streamable_http", 
        "url": "https://your-jira-mcp-server.com",
        "headers": {"Authorization": f"Bearer {jira_token}"}
    }
}

# No local installation required!
client = MultiServerMCPClient(servers_config)
tools = await client.get_tools()
```

## 📊 Workflow Overview

```
1. Initialize Incident
   ↓
2. Coordinator Assessment
   ↓
3. Parallel Execution
   ├── Investigation Subgraph
   ├── Analysis Subgraph  
   └── Communication Subgraph
   ↓
4. Synthesize Results
   ↓
5. Decision Point
   ↓
6. Execution Subgraph
   ↓
7. Finalize Incident
```

## 🧠 Memory System

The system implements sophisticated memory management:

### Memory Types

- **Semantic Memories**: Key findings and insights
- **Procedural Memories**: Decision patterns and strategies
- **Context Memories**: Incident-specific context

### Memory Operations

- **Storage**: Automatic memory creation during agent operations
- **Retrieval**: Semantic search for relevant memories
- **Updates**: Continuous learning and memory refinement

## ⚡ Performance Features

### Parallelization

- **Subgraph Parallelization**: Investigation, analysis, and communication run simultaneously
- **Agent Parallelization**: Multiple agents work on different aspects concurrently
- **Task Parallelization**: Independent tasks within subgraphs execute in parallel

### State Management

- **Checkpointing**: Automatic state persistence
- **Resume Capability**: Workflow can be resumed from any point
- **State Optimization**: Efficient state updates and memory usage

## 🔍 Investigation Capabilities

### Evidence Collection

- **Log Analysis**: Automated parsing and correlation of service logs
- **Git Analysis**: Real-time commit history analysis using GitHub MCP
- **Performance Metrics**: Real-time performance data analysis
- **MCP Integration**: Direct access to GitHub repositories and Jira projects

### Root Cause Analysis

- **Pattern Recognition**: Automated detection of patterns in data
- **Correlation Analysis**: Identifying relationships between different factors
- **Confidence Scoring**: Quantified confidence in findings

## 📈 Analysis Features

### Data Analysis

- **Performance Metrics**: Response time, memory usage, error rates
- **Trend Analysis**: Historical data analysis and trend identification
- **Anomaly Detection**: Automatic detection of unusual patterns

### Pattern Recognition

- **Memory Growth Patterns**: Detection of memory leaks
- **Error Patterns**: Identification of error patterns and correlations
- **Performance Degradation**: Recognition of performance issues

## 📢 Communication Management

### Stakeholder Management

- **Automatic Identification**: Identifying relevant stakeholders
- **Communication Planning**: Creating communication strategies
- **Escalation Management**: Automatic escalation based on triggers

### Notification System

- **Jira Integration**: Automatic incident ticket creation and updates
- **Multi-channel Notifications**: Email, Slack, SMS, etc.
- **Status Updates**: Real-time status updates to stakeholders
- **Response Monitoring**: Tracking stakeholder responses
- **MCP Integration**: Direct Jira ticket management

## ⚙️ Execution System

### Action Planning

- **Automated Planning**: Creating action plans based on findings
- **Resource Allocation**: Optimizing resource allocation
- **Risk Assessment**: Evaluating risks of proposed actions

### Implementation

- **Automated Execution**: Executing planned actions
- **Progress Monitoring**: Real-time progress tracking
- **Failure Handling**: Automatic handling of execution failures

## 🛠️ Customization

### Adding New Agents

```python
class CustomAgent(BaseAgent):
    def _get_system_prompt(self) -> str:
        return "Your custom system prompt"
    
    def _get_task_prompt(self) -> str:
        return "Your custom task prompt"
    
    async def execute(self, state: IncidentState) -> Dict[str, Any]:
        # Your custom logic
        return result

# Register the agent
AgentFactory.register_agent(AgentRole.CUSTOM, CustomAgent)
```

### Extending Subgraphs

```python
def create_custom_subgraph():
    builder = StateGraph(CustomState)
    
    # Add custom nodes
    builder.add_node("custom_node", _custom_node_function)
    
    # Add edges
    builder.add_edge(START, "custom_node")
    builder.add_edge("custom_node", END)
    
    return builder.compile(checkpointer=MemorySaver())
```

### Custom Memory Types

```python
class CustomMemory(BaseModel):
    custom_field: str = Field(description="Custom memory field")
    # ... other fields

# Use in agents
agent.add_memory(
    content="Custom memory content",
    source="custom_agent",
    tags=["custom"],
    custom_field="custom_value"
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# GitHub MCP (Required for real Git data)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_OWNER=your-github-organization
GITHUB_REPO=your-github-repository

# Jira MCP (Required for real Jira integration)
JIRA_URL=https://your-domain.atlassian.net
JIRA_TOKEN=your_jira_api_token
JIRA_PROJECT=INCIDENT

# Optional
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langgraph-incident-response
```

### MCP Server Setup

The system uses real MCP servers for GitHub and Jira integration:

#### GitHub MCP Server
```bash
# Install globally
npm install -g @modelcontextprotocol/server-github

# Test connection
npx @modelcontextprotocol/server-github --token YOUR_TOKEN --owner your-org --repo your-repo
```

#### Jira MCP Server
```bash
# Install globally
npm install -g @modelcontextprotocol/server-jira

# Test connection
npx @modelcontextprotocol/server-jira --url https://your-domain.atlassian.net --token YOUR_TOKEN --project INCIDENT
```

### Agent Configuration

```python
# Custom agent configuration
agent_config = {
    "preferences": {
        "analysis_depth": "deep",
        "communication_style": "technical"
    },
    "performance_metrics": {
        "response_time": 0.0,
        "accuracy": 0.0
    }
}

coordinator = CoordinatorAgent(
    agent_id="coordinator-001",
    preferences=agent_config["preferences"],
    performance_metrics=agent_config["performance_metrics"]
)
```

## 📊 Monitoring and Observability

### LangSmith Integration

The system integrates with LangSmith for:

- **Tracing**: Complete workflow tracing
- **Debugging**: Step-by-step debugging capabilities
- **Performance Monitoring**: Performance metrics and optimization
- **Collaboration**: Team collaboration on incident response

### Logging

Comprehensive logging for:

- **Agent Operations**: All agent activities and decisions
- **State Changes**: Complete state evolution tracking
- **Memory Operations**: Memory creation, retrieval, and updates
- **Error Handling**: Detailed error information and stack traces

## 🧪 Testing

### Unit Tests

```bash
# Run unit tests
pytest tests/unit/

# Run with coverage
pytest --cov=src tests/unit/
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Test specific scenarios
pytest tests/integration/test_oom_scenario.py
```

### Performance Tests

```bash
# Run performance tests
pytest tests/performance/

# Benchmark parallel execution
pytest tests/performance/test_parallel_execution.py
```

## 🚀 Deployment

### Local Development

```bash
# Development setup
pip install -r requirements.txt
python -m src.main
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-incident-response
spec:
  replicas: 1
  selector:
    matchLabels:
      app: langgraph-incident-response
  template:
    metadata:
      labels:
        app: langgraph-incident-response
    spec:
      containers:
      - name: incident-response
        image: langgraph-incident-response:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain Academy**: For the excellent Module 4 and 5 content
- **LangGraph Team**: For the powerful graph-based workflow framework
- **OpenAI**: For the LLM capabilities that power the agents

## 📞 Support

For questions, issues, or contributions:

- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

---

**Built with ❤️ using LangGraph and following LangChain Academy best practices**
