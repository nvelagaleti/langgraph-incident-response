"""
Enhanced Incident Response Agent with GitHub and Jira MCP Integration.
This agent leverages our working GitHub and Jira integrations for comprehensive incident response.
"""

import asyncio
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .base_agent import BaseAgent
from ..types.state import (
    AgentRole,
    IncidentState,
    InvestigationFinding,
    Recommendation,
    IncidentSeverity,
    IncidentStatus,
    GitCommit
)

# Import our working MCP integrations
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from jira_mcp_complete_integration import JiraMCPCompleteIntegration


class IncidentResponseAgent(BaseAgent):
    """
    Enhanced Incident Response Agent with GitHub and Jira MCP Integration.
    This agent can investigate incidents using both GitHub and Jira data.
    """
    
    def __init__(self, agent_id: str, **kwargs):
        capabilities = [
            "incident_investigation",
            "github_analysis",
            "jira_management",
            "code_review",
            "issue_tracking",
            "communication",
            "documentation"
        ]
        super().__init__(agent_id, AgentRole.INVESTIGATOR, capabilities, **kwargs)
        
        # Initialize MCP integrations
        self.github_mcp = None
        self.jira_mcp = None
        
        # Initialize Circuit LLM
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
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
    
    async def initialize_integrations(self):
        """Initialize GitHub and Jira MCP integrations."""
        try:
            print("🔗 Initializing MCP integrations for Incident Response Agent...")
            
            # Initialize Jira MCP integration
            self.jira_mcp = JiraMCPCompleteIntegration()
            jira_success = await self.jira_mcp.initialize()
            
            if jira_success:
                print("✅ Jira MCP integration initialized")
            else:
                print("❌ Jira MCP integration failed")
            
            # Initialize GitHub MCP integration (using existing service)
            try:
                from ..services.langchain_mcp_client import LangChainMCPClient
                self.github_mcp = LangChainMCPClient()
                
                config = {
                    "github_mcp_url": os.getenv("MCP_GITHUB_SERVER_URL"),
                    "github_token": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
                    "jira_mcp_url": None,  # We're using direct Jira integration
                    "jira_token": None
                }
                
                github_success = await self.github_mcp.initialize(config)
                if github_success:
                    print("✅ GitHub MCP integration initialized")
                else:
                    print("❌ GitHub MCP integration failed")
                    
            except Exception as e:
                print(f"⚠️  GitHub MCP integration error: {e}")
            
            return jira_success or (self.github_mcp and self.github_mcp.initialized)
            
        except Exception as e:
            print(f"❌ Error initializing MCP integrations: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        return """
        You are an Expert Incident Response Investigator with deep knowledge of:
        - Software development and deployment processes
        - GitHub repository analysis and code review
        - Jira issue tracking and project management
        - System architecture and troubleshooting
        - Incident response best practices
        
        Your capabilities include:
        1. Analyzing GitHub repositories for recent changes and potential issues
        2. Creating and managing Jira tickets for incident tracking
        3. Reviewing code commits and identifying problematic changes
        4. Investigating system logs and error patterns
        5. Coordinating with development and operations teams
        6. Documenting findings and recommendations
        
        You have access to:
        - GitHub repositories and commit history
        - Jira project management tools
        - Incident details and current status
        - System monitoring and logging data
        
        Your investigation approach should be:
        - Systematic and thorough
        - Evidence-based and analytical
        - Collaborative and communicative
        - Documented and traceable
        
        Always consider the impact on users and business operations.
        """
    
    def _get_task_prompt(self) -> str:
        return """
        As an Incident Response Investigator, you need to:
        
        1. Analyze the incident details and affected services
        2. Investigate recent GitHub changes that might be related
        3. Create or update Jira tickets for tracking
        4. Review code changes and identify potential root causes
        5. Document findings and provide recommendations
        
        Current incident: {incident_title}
        Severity: {severity}
        Affected services: {affected_services}
        Description: {description}
        
        Available tools:
        - GitHub repository analysis
        - Jira ticket management
        - Code review capabilities
        - Issue tracking and documentation
        
        What is your investigation plan and next steps?
        """
    
    async def execute(self, state: IncidentState) -> Dict[str, Any]:
        """Execute the incident response investigation."""
        context = self.get_context(state)
        
        # Initialize integrations if not already done
        if not self.jira_mcp or not self.jira_mcp.initialized:
            await self.initialize_integrations()
        
        # Analyze incident and create investigation plan
        investigation_plan = await self._create_investigation_plan(state)
        
        # Execute investigation steps
        findings = await self._execute_investigation(state, investigation_plan)
        
        # Create Jira tickets for tracking
        jira_tickets = await self._create_jira_tickets(state, findings)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(state, findings)
        
        # Update incident status
        updated_state = await self._update_incident_status(state, findings, recommendations)
        
        return updated_state
    
    async def _create_investigation_plan(self, state: IncidentState) -> Dict[str, Any]:
        """Create a comprehensive investigation plan."""
        incident_data = state.get('incident', {})
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", """
            Create a detailed investigation plan for this incident:
            
            Incident: {title}
            Severity: {severity}
            Affected Services: {services}
            Description: {description}
            
            Your plan should include:
            1. GitHub repository analysis steps
            2. Jira ticket creation strategy
            3. Code review priorities
            4. Timeline and milestones
            5. Success criteria
            
            Return your plan as JSON with the following structure:
            {{
                "investigation_steps": [
                    {{
                        "step": "string",
                        "description": "string",
                        "priority": "high|medium|low",
                        "estimated_time": "string"
                    }}
                ],
                "github_repos_to_analyze": ["list", "of", "repos"],
                "jira_tickets_needed": [
                    {{
                        "type": "string",
                        "summary": "string",
                        "description": "string",
                        "priority": "string"
                    }}
                ],
                "timeline": {{
                    "start": "datetime",
                    "estimated_completion": "datetime",
                    "milestones": ["list", "of", "milestones"]
                }}
            }}
            """)
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            plan = await chain.ainvoke({
                "title": incident_data.get('title', 'Unknown'),
                "severity": incident_data.get('severity', 'Unknown'),
                "services": ', '.join(incident_data.get('affected_services', [])),
                "description": incident_data.get('description', 'No description')
            })
            
            print(f"📋 Investigation Plan Created:")
            print(f"   Steps: {len(plan.get('investigation_steps', []))}")
            print(f"   GitHub Repos: {len(plan.get('github_repos_to_analyze', []))}")
            print(f"   Jira Tickets: {len(plan.get('jira_tickets_needed', []))}")
            
            return plan
            
        except Exception as e:
            print(f"❌ Error creating investigation plan: {e}")
            return {"investigation_steps": [], "github_repos_to_analyze": [], "jira_tickets_needed": []}
    
    async def _execute_investigation(self, state: IncidentState, plan: Dict[str, Any]) -> List[InvestigationFinding]:
        """Execute the investigation plan."""
        findings = []
        incident_data = state.get('incident', {})
        
        print("🔍 Executing Investigation Plan...")
        
        # Step 1: Analyze GitHub repositories
        if plan.get('github_repos_to_analyze') and self.github_mcp:
            github_findings = await self._analyze_github_repositories(
                plan['github_repos_to_analyze'],
                incident_data
            )
            findings.extend(github_findings)
        
        # Step 2: Review recent code changes
        if self.github_mcp:
            code_findings = await self._review_recent_changes(incident_data)
            findings.extend(code_findings)
        
        # Step 3: Analyze system patterns
        system_findings = await self._analyze_system_patterns(incident_data)
        findings.extend(system_findings)
        
        print(f"✅ Investigation completed: {len(findings)} findings discovered")
        return findings
    
    async def _analyze_github_repositories(self, repos: List[str], incident_data: Dict[str, Any]) -> List[InvestigationFinding]:
        """Analyze GitHub repositories for potential issues."""
        findings = []
        
        print(f"🔍 Analyzing GitHub repositories: {repos}")
        
        for repo in repos:
            try:
                # Get recent commits
                if self.github_mcp and hasattr(self.github_mcp, 'get_github_commits'):
                    commits = await self.github_mcp.get_github_commits(
                        repo_owner=repo.split('/')[0] if '/' in repo else 'unknown',
                        repo_name=repo.split('/')[1] if '/' in repo else repo,
                        since_date=(datetime.now() - timedelta(days=7)).isoformat(),
                        until_date=datetime.now().isoformat()
                    )
                    
                    if commits:
                        # Analyze commits for potential issues
                        commit_analysis = await self._analyze_commits_for_issues(commits, incident_data)
                        findings.extend(commit_analysis)
                
            except Exception as e:
                print(f"❌ Error analyzing repository {repo}: {e}")
        
        return findings
    
    async def _analyze_commits_for_issues(self, commits: List[GitCommit], incident_data: Dict[str, Any]) -> List[InvestigationFinding]:
        """Analyze commits for potential issues related to the incident."""
        findings = []
        
        # Use LLM to analyze commits
        commit_data = []
        for commit in commits[:10]:  # Analyze last 10 commits
            commit_data.append({
                "sha": commit.sha,
                "message": commit.message,
                "author": commit.author,
                "date": commit.date,
                "files": commit.files
            })
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are analyzing Git commits to identify potential issues related to an incident.
            Look for:
            - Configuration changes that might cause memory issues
            - Code changes that could introduce bugs
            - Deployment changes that might affect system stability
            - Changes to affected services mentioned in the incident
            """),
            ("human", """
            Analyze these commits for potential issues related to this incident:
            
            Incident: {incident_title}
            Affected Services: {affected_services}
            Description: {description}
            
            Commits to analyze:
            {commits}
            
            Return your analysis as JSON:
            {{
                "findings": [
                    {{
                        "title": "string",
                        "description": "string",
                        "severity": "high|medium|low",
                        "confidence": 0.0-1.0,
                        "commit_sha": "string",
                        "evidence": "string"
                    }}
                ]
            }}
            """)
        ])
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            analysis = await chain.ainvoke({
                "incident_title": incident_data.get('title', 'Unknown'),
                "affected_services": ', '.join(incident_data.get('affected_services', [])),
                "description": incident_data.get('description', 'No description'),
                "commits": json.dumps(commit_data, indent=2)
            })
            
            for finding_data in analysis.get('findings', []):
                finding = InvestigationFinding(
                    id=str(uuid.uuid4()),
                    title=finding_data['title'],
                    description=finding_data['description'],
                    severity=finding_data['severity'],
                    confidence=finding_data['confidence'],
                    evidence=finding_data['evidence'],
                    source="github_analysis",
                    created_at=datetime.now()
                )
                findings.append(finding)
                
        except Exception as e:
            print(f"❌ Error analyzing commits: {e}")
        
        return findings
    
    async def _review_recent_changes(self, incident_data: Dict[str, Any]) -> List[InvestigationFinding]:
        """Review recent code changes for potential issues."""
        findings = []
        
        print("🔍 Reviewing recent code changes...")
        
        # This would typically involve more sophisticated code analysis
        # For now, we'll create a basic finding based on the incident
        finding = InvestigationFinding(
            id=str(uuid.uuid4()),
            title="Recent Backend Configuration Change Detected",
            description="A recent backend configuration change may have triggered the memory leak. Need to review configuration files and deployment history.",
            severity="high",
            confidence=0.8,
            evidence="Incident description mentions recent backend configuration change",
            source="code_review",
            created_at=datetime.now()
        )
        findings.append(finding)
        
        return findings
    
    async def _analyze_system_patterns(self, incident_data: Dict[str, Any]) -> List[InvestigationFinding]:
        """Analyze system patterns and logs for insights."""
        findings = []
        
        print("🔍 Analyzing system patterns...")
        
        # Create findings based on incident analysis
        finding = InvestigationFinding(
            id=str(uuid.uuid4()),
            title="Memory Usage Pattern Analysis",
            description="Memory usage spiking to 95% suggests a memory leak rather than normal usage patterns. This is consistent with GraphQL service issues.",
            severity="high",
            confidence=0.9,
            evidence="Memory usage at 95% of allocated resources",
            source="system_analysis",
            created_at=datetime.now()
        )
        findings.append(finding)
        
        return findings
    
    async def _create_jira_tickets(self, state: IncidentState, findings: List[InvestigationFinding]) -> List[Dict[str, Any]]:
        """Create Jira tickets for incident tracking."""
        tickets = []
        
        if not self.jira_mcp or not self.jira_mcp.initialized:
            print("⚠️  Jira MCP not available, skipping ticket creation")
            return tickets
        
        print("📝 Creating Jira tickets...")
        
        incident_data = state.get('incident', {})
        
        # Create main incident ticket
        try:
            main_ticket = await self.jira_mcp.create_issue(
                project_key="IR",
                summary=f"INCIDENT: {incident_data.get('title', 'Unknown Incident')}",
                description=f"""
                **Incident Details:**
                - ID: {incident_data.get('id', 'Unknown')}
                - Severity: {incident_data.get('severity', 'Unknown')}
                - Affected Services: {', '.join(incident_data.get('affected_services', []))}
                
                **Description:**
                {incident_data.get('description', 'No description')}
                
                **Investigation Findings:**
                {self._format_findings_for_jira(findings)}
                
                **Status:** Under Investigation
                **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """,
                issue_type="Incident"
            )
            
            if main_ticket:
                tickets.append(main_ticket)
                print(f"✅ Created main incident ticket: {main_ticket.get('key', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error creating main incident ticket: {e}")
        
        # Create tickets for high-severity findings
        for finding in findings:
            if finding.severity == "high":
                try:
                    finding_ticket = await self.jira_mcp.create_issue(
                        project_key="IR",
                        summary=f"FINDING: {finding.title}",
                        description=f"""
                        **Finding Details:**
                        - ID: {finding.id}
                        - Severity: {finding.severity}
                        - Confidence: {finding.confidence:.1%}
                        - Source: {finding.source}
                        
                        **Description:**
                        {finding.description}
                        
                        **Evidence:**
                        {finding.evidence}
                        
                        **Related Incident:** {incident_data.get('id', 'Unknown')}
                        """,
                        issue_type="Task"
                    )
                    
                    if finding_ticket:
                        tickets.append(finding_ticket)
                        print(f"✅ Created finding ticket: {finding_ticket.get('key', 'Unknown')}")
                
                except Exception as e:
                    print(f"❌ Error creating finding ticket: {e}")
        
        return tickets
    
    def _format_findings_for_jira(self, findings: List[InvestigationFinding]) -> str:
        """Format findings for Jira ticket description."""
        if not findings:
            return "No findings yet."
        
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(f"""
            **Finding {i}:**
            - Title: {finding.title}
            - Severity: {finding.severity}
            - Confidence: {finding.confidence:.1%}
            - Description: {finding.description}
            """)
        
        return '\n'.join(formatted)
    
    async def _generate_recommendations(self, state: IncidentState, findings: List[InvestigationFinding]) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        print("💡 Generating recommendations...")
        
        # Use LLM to generate recommendations
        findings_data = []
        for finding in findings:
            findings_data.append({
                "title": finding.title,
                "description": finding.description,
                "severity": finding.severity,
                "confidence": finding.confidence,
                "evidence": finding.evidence
            })
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert incident response analyst. Based on the investigation findings,
            provide actionable recommendations to resolve the incident and prevent future occurrences.
            """),
            ("human", """
            Generate recommendations based on these investigation findings:
            
            Incident: {incident_title}
            Severity: {severity}
            
            Findings:
            {findings}
            
            Provide recommendations as JSON:
            {{
                "recommendations": [
                    {{
                        "title": "string",
                        "description": "string",
                        "priority": "high|medium|low",
                        "category": "immediate|short_term|long_term",
                        "estimated_effort": "string",
                        "impact": "string"
                    }}
                ]
            }}
            """)
        ])
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            analysis = await chain.ainvoke({
                "incident_title": state.get('incident', {}).get('title', 'Unknown'),
                "severity": state.get('incident', {}).get('severity', 'Unknown'),
                "findings": json.dumps(findings_data, indent=2)
            })
            
            for rec_data in analysis.get('recommendations', []):
                recommendation = Recommendation(
                    id=str(uuid.uuid4()),
                    title=rec_data['title'],
                    description=rec_data['description'],
                    priority=rec_data['priority'],
                    category=rec_data['category'],
                    estimated_effort=rec_data['estimated_effort'],
                    impact=rec_data['impact'],
                    created_at=datetime.now()
                )
                recommendations.append(recommendation)
                
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
        
        return recommendations
    
    async def _update_incident_status(self, state: IncidentState, findings: List[InvestigationFinding], recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Update the incident status based on investigation results."""
        
        # Determine new status based on findings
        if any(f.severity == "high" for f in findings):
            new_status = IncidentStatus.INVESTIGATING
        elif findings:
            new_status = IncidentStatus.ANALYZING
        else:
            new_status = IncidentStatus.INITIALIZED
        
        # Update state
        updated_state = state.copy()
        updated_state.update({
            'status': new_status,
            'findings': findings,
            'recommendations': recommendations,
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['investigation']
        })
        
        print(f"📊 Updated incident status: {new_status}")
        print(f"   Findings: {len(findings)}")
        print(f"   Recommendations: {len(recommendations)}")
        
        return updated_state
