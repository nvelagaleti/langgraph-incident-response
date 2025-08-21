# LangGraph Studio - Incident Response System

This Studio folder contains everything needed to run the LangGraph Incident Response System in LangGraph Studio.

## 🚀 Quick Start

1. **Set up environment variables** in a `.env` file:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   JIRA_OAUTH_TOKEN=your_jira_oauth_token
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Open in LangGraph Studio**:
   - Navigate to this folder in LangGraph Studio
   - The system will automatically detect the available graphs

## 📊 Available Graphs

### 1. Basic Incident Response (`incident_response_basic`)
A simple incident response workflow without external integrations.

**Use case**: Quick incident analysis and basic recommendations.

### 2. Enhanced Incident Response (`incident_response_enhanced`)
A comprehensive incident response workflow with advanced features.

**Use case**: Full incident response with coordination, investigation, analysis, and execution.

### 3. MCP Integration (`incident_response_with_mcp`)
Incident response with GitHub and Jira MCP integration.

**Use case**: Advanced incident response using external tools and data sources.

### 4. Coordinator Agent (`coordinator_agent`)
A specialized agent for coordinating incident response activities.

**Use case**: Managing multi-agent incident response workflows.

### 5. Investigator Agent (`investigator_agent`)
A specialized agent for investigating incidents and gathering evidence.

**Use case**: Deep incident investigation and root cause analysis.

## 🔧 Configuration

The `configuration.py` file defines configurable parameters:

- `user_id`: User identifier for the session
- `incident_severity`: Default incident severity level
- `enable_mcp_integration`: Enable/disable MCP integrations
- `enable_github_integration`: Enable/disable GitHub integration
- `enable_jira_integration`: Enable/disable Jira integration
- `auto_create_tickets`: Automatically create Jira tickets
- `enable_auto_remediation`: Enable automatic remediation actions

## 📝 Usage Examples

### Basic Incident Response
```python
# Initialize with incident data
initial_state = {
    "title": "Service Outage",
    "description": "API service is down",
    "severity": "HIGH"
}

# Run the graph
result = await graph.ainvoke(initial_state)
```

### Enhanced Incident Response
```python
# Initialize with comprehensive incident data
initial_state = {
    "title": "Critical Memory Leak",
    "description": "GraphQL service experiencing memory issues",
    "severity": "CRITICAL",
    "affected_services": ["api-service", "web-app"]
}

# Run the enhanced workflow
result = await graph_with_memory.ainvoke(initial_state)
```

### MCP Integration
```python
# Initialize with MCP-enabled incident
initial_state = {
    "title": "Deployment Failure",
    "description": "Recent deployment caused service issues",
    "severity": "HIGH",
    "github_repos": ["company/api-service"],
    "jira_project": "IR"
}

# Run with MCP integrations
result = await graph.ainvoke(initial_state)
```

## 🔍 Graph Features

### State Management
All graphs use TypedDict state definitions for type safety and include:
- Incident tracking information
- Progress tracking
- Findings and recommendations
- Communication logs
- MCP integration status

### Memory and Checkpointing
Graphs include memory savers for:
- Session persistence
- State recovery
- Multi-step workflows
- Debugging and analysis

### Conditional Logic
Enhanced graphs include conditional edges for:
- Escalation decisions
- Immediate action requirements
- Resource allocation
- Workflow optimization

## 🛠️ Customization

### Adding New Nodes
1. Define the node function
2. Add it to the graph workflow
3. Connect it with appropriate edges
4. Update state management

### Extending MCP Integrations
1. Add new MCP server configurations
2. Create integration functions
3. Update state definitions
4. Add conditional logic for availability

### Custom State Types
1. Define new TypedDict classes
2. Update graph state type
3. Modify node functions
4. Update memory handling

## 📚 Integration with Main System

This Studio setup is designed to work with the main LangGraph Incident Response System:

- **Shared Types**: Uses compatible state definitions
- **MCP Integration**: Leverages the same MCP client implementations
- **Agent Patterns**: Follows the same agent architecture
- **Configuration**: Uses consistent environment variables

## 🚨 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all required tokens are set in `.env`
   - Check token validity and permissions

2. **MCP Integration Failures**
   - Verify MCP server availability
   - Check authentication credentials
   - Review network connectivity

3. **Graph Execution Errors**
   - Check state type compatibility
   - Verify node function signatures
   - Review error logs for specific issues

### Debug Mode
Enable debug logging by setting:
```bash
export LANGGRAPH_DEBUG=1
```

## 📈 Performance Optimization

### Memory Management
- Use checkpointing for long-running workflows
- Implement state cleanup for completed incidents
- Monitor memory usage in large-scale deployments

### Parallel Processing
- Consider parallel execution for independent nodes
- Use async/await patterns for I/O operations
- Implement caching for repeated operations

## 🔐 Security Considerations

- Store sensitive tokens securely
- Use environment variables for configuration
- Implement proper access controls
- Audit MCP server connections
- Monitor API usage and rate limits

## 📞 Support

For issues and questions:
1. Check the main system documentation
2. Review error logs and stack traces
3. Verify environment configuration
4. Test with simplified workflows first

---

**Note**: This Studio setup is designed for educational and demonstration purposes. For production use, ensure proper security, monitoring, and error handling are implemented.
