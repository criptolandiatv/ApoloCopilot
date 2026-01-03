---
name: prompt-architect
description: Advanced prompt engineering and software construction skill based on Amanda Askell and Erik Schluntz principles. Use for prompt analysis, context engineering, building AI-powered software, and understanding 90% of any complex topic through structured decomposition.
---

# Prompt Architect Skill

Master-level prompt engineering and software construction based on Anthropic's leading engineers: **Amanda Askell** (philosopher/prompt engineer) and **Erik Schluntz** (context engineering).

## Core Philosophy

> "Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome." - Anthropic

## Part 1: Amanda Askell's Prompt Engineering Principles

### 1. Clarity Over Cleverness

Prompt engineering is fundamentally about **clear communication**, not clever tricks.

```xml
<!-- BAD: Vague -->
<prompt>Help me with my code</prompt>

<!-- GOOD: Crystal clear -->
<prompt>
  <role>You are a senior Python developer with 10 years of FastAPI experience</role>
  <task>Review this endpoint for security vulnerabilities</task>
  <format>List each vulnerability with severity (HIGH/MEDIUM/LOW) and fix</format>
  <constraints>Focus only on OWASP Top 10 issues</constraints>
</prompt>
```

### 2. Treat Claude Like a Brilliant New Employee

Claude has no context on your norms, styles, or preferences. Be explicit:

```xml
<context>
  <project>E-commerce API with 50k daily users</project>
  <tech_stack>FastAPI, PostgreSQL, Redis, Docker</tech_stack>
  <coding_standards>PEP8, type hints required, 80% test coverage</coding_standards>
  <team_conventions>
    - Use dataclasses over Pydantic for internal models
    - All endpoints must have OpenAPI documentation
    - Error responses follow RFC 7807
  </team_conventions>
</context>
```

### 3. Iterate Rapidly

Amanda sends **hundreds of prompts in 15 minutes**. Apply this workflow:

```
ITERATION LOOP:
1. Draft initial prompt
2. Send to Claude
3. Analyze response gaps
4. Identify edge cases
5. Refine prompt
6. Repeat until 95% accuracy
```

### 4. Remove Assumptions

The hardest and most important part. Check your prompt for:

```xml
<assumption_checklist>
  <item>Am I assuming Claude knows my domain terminology?</item>
  <item>Am I assuming a specific output format without stating it?</item>
  <item>Am I assuming Claude will handle edge cases my way?</item>
  <item>Am I assuming context from previous conversations?</item>
  <item>Am I assuming Claude shares my values/priorities?</item>
</assumption_checklist>
```

### 5. Break Down Into Steps

Structure reasoning for complex tasks:

```xml
<task>Analyze this codebase for refactoring opportunities</task>

<thinking_structure>
  <step_1>First, identify all code smells (duplication, long methods, etc.)</step_1>
  <step_2>Then, categorize by impact (HIGH/MEDIUM/LOW)</step_2>
  <step_3>Next, propose refactoring patterns for each</step_3>
  <step_4>Finally, prioritize by effort-to-impact ratio</step_4>
</thinking_structure>

<output_format>
  Present findings in a table with columns: Issue | Impact | Pattern | Effort | Priority
</output_format>
```

### 6. Use Claude as Collaborator

Ask Claude to improve your prompts:

```
"Here's my current prompt for [task]. What ambiguities do you see?
How would you rephrase it for better results?"
```

### 7. Stress-Test Prompts

Good-sounding answers can hide subtle errors. Test with:

```xml
<stress_tests>
  <edge_case>Empty input</edge_case>
  <edge_case>Maximum length input</edge_case>
  <edge_case>Malformed data</edge_case>
  <edge_case>Ambiguous instructions</edge_case>
  <edge_case>Contradictory requirements</edge_case>
  <edge_case>Adversarial inputs</edge_case>
</stress_tests>
```

## Part 2: Erik Schluntz's Context Engineering

### The Context Budget

Context is **finite and precious**. Every token counts.

```
CONTEXT HIERARCHY (by priority):
1. Current task instructions (HIGHEST)
2. Relevant code/data for THIS task
3. Project conventions and standards
4. Background knowledge
5. Nice-to-have context (LOWEST)
```

### Fighting Context Rot

As context grows, accuracy degrades. Strategies:

```xml
<context_management>
  <strategy name="pruning">
    Remove irrelevant dialogue turns after task completion
  </strategy>

  <strategy name="summarization">
    Compress past interactions: "Previously: implemented auth system with JWT"
  </strategy>

  <strategy name="delegation">
    Offload sub-tasks to specialized agents with fresh context
  </strategy>

  <strategy name="chunking">
    Process large codebases in focused chunks, not all at once
  </strategy>
</context_management>
```

### Tool Design Principles

Design tools that are intuitive for Claude:

```python
# BAD: Ambiguous tool
def process_data(data, mode, options):
    """Process data somehow"""
    pass

# GOOD: Clear, scoped tool
def validate_user_email(
    email: str,
    check_mx_record: bool = True,
    allow_plus_addressing: bool = False
) -> EmailValidationResult:
    """
    Validate email address format and optionally verify MX record.

    Returns:
        EmailValidationResult with:
        - is_valid: bool
        - error_message: str | None
        - mx_verified: bool | None
    """
    pass
```

### Workflow vs Agent Architecture

```
WORKFLOWS (Orchestrated):
├── Predefined execution paths
├── Deterministic flow control
├── Best for: Known processes, pipelines
└── Example: CI/CD, data ETL

AGENTS (Autonomous):
├── Dynamic decision-making
├── Self-directed tool usage
├── Best for: Open-ended problems
└── Example: Code review, research tasks
```

## Part 3: XML Tagging Mastery

Claude was trained to recognize XML tags as organizational structure.

### Standard Tag Library

```xml
<!-- Task Definition -->
<role>Your identity/expertise</role>
<task>What to accomplish</task>
<context>Background information</context>
<constraints>Limitations and boundaries</constraints>

<!-- Reasoning Structure -->
<thinking>Internal reasoning (can be hidden)</thinking>
<analysis>Step-by-step breakdown</analysis>
<conclusion>Final determination</conclusion>

<!-- Output Control -->
<format>Expected output structure</format>
<examples>Few-shot demonstrations</examples>
<output>The actual response</output>

<!-- Multi-perspective Analysis -->
<positive_argument>Arguments in favor</positive_argument>
<negative_argument>Arguments against</negative_argument>
<synthesis>Balanced conclusion</synthesis>
```

### Advanced Pattern: Debate Framework

```xml
<task>Evaluate whether to use microservices vs monolith</task>

<advocate_microservices>
  Present the strongest case for microservices architecture
</advocate_microservices>

<advocate_monolith>
  Present the strongest case for monolithic architecture
</advocate_monolith>

<judge>
  Based on both arguments and the specific context provided,
  render a verdict with confidence level (HIGH/MEDIUM/LOW)
</judge>
```

## Part 4: Chain of Thought Patterns

### Basic CoT

```xml
<task>Calculate the optimal cache TTL for this API</task>

<thinking>
  Step 1: Analyze data update frequency
  Step 2: Measure current response times
  Step 3: Calculate staleness tolerance
  Step 4: Factor in infrastructure costs
</thinking>

<answer>
  Recommended TTL: 300 seconds
  Rationale: [derived from thinking]
</answer>
```

### Tree of Thought (Advanced)

```xml
<task>Design authentication system</task>

<branch_1>
  <approach>JWT with refresh tokens</approach>
  <pros>Stateless, scalable</pros>
  <cons>Token revocation complexity</cons>
  <score>7/10</score>
</branch_1>

<branch_2>
  <approach>Session-based with Redis</approach>
  <pros>Easy revocation, familiar</pros>
  <cons>State management overhead</cons>
  <score>6/10</score>
</branch_2>

<branch_3>
  <approach>OAuth2 with external provider</approach>
  <pros>Delegated security, SSO</pros>
  <cons>Vendor dependency</cons>
  <score>8/10</score>
</branch_3>

<selection>Branch 3 - OAuth2</selection>
<justification>Best balance of security and maintenance for team size</justification>
```

## Part 5: 90% Topic Comprehension Framework

To understand 90% of any complex topic:

### Step 1: Core Decomposition

```xml
<topic>Kubernetes</topic>

<decomposition>
  <layer_1_fundamentals weight="40%">
    <concept>Pods - smallest deployable unit</concept>
    <concept>Services - network abstraction</concept>
    <concept>Deployments - declarative updates</concept>
  </layer_1_fundamentals>

  <layer_2_architecture weight="30%">
    <concept>Control plane components</concept>
    <concept>Node components</concept>
    <concept>Networking model</concept>
  </layer_2_architecture>

  <layer_3_operations weight="20%">
    <concept>kubectl commands</concept>
    <concept>YAML manifests</concept>
    <concept>Helm charts</concept>
  </layer_3_operations>

  <layer_4_advanced weight="10%">
    <concept>Custom operators</concept>
    <concept>Service mesh</concept>
    <concept>Multi-cluster</concept>
  </layer_4_advanced>
</decomposition>
```

### Step 2: Feynman Technique Prompt

```xml
<task>Explain [TOPIC] so a smart 12-year-old would understand</task>

<constraints>
  - No jargon without immediate definition
  - Use concrete analogies from everyday life
  - Build concepts incrementally
  - End with "why this matters"
</constraints>
```

### Step 3: Expert Interview Simulation

```xml
<role>You are the world's leading expert on [TOPIC]</role>

<interview_questions>
  <q1>What's the single most important concept beginners miss?</q1>
  <q2>What common misconception frustrates you most?</q2>
  <q3>If someone has 2 hours to learn this, what should they focus on?</q3>
  <q4>What's the cutting edge that most practitioners don't know?</q4>
</interview_questions>
```

## Part 6: Software Construction Principles

### The Anthropic Agent Pattern

```python
from anthropic import Anthropic

class EffectiveAgent:
    """
    Agent following Anthropic's building effective agents principles.
    """

    def __init__(self, client: Anthropic):
        self.client = client
        self.context_budget = 100000  # tokens
        self.current_context = []

    def manage_context(self, new_content: str) -> None:
        """Prune and summarize to stay within budget."""
        # 1. Summarize completed tasks
        # 2. Remove irrelevant turns
        # 3. Keep only high-signal tokens
        pass

    def design_tool(self, name: str, description: str) -> dict:
        """
        Tool design principles:
        - Clear, non-overlapping functions
        - Intuitive for LLM understanding
        - Robust, well-scoped purpose
        - Unambiguous parameters
        """
        return {
            "name": name,
            "description": description,  # Be VERY specific
            "input_schema": {
                # Define every parameter explicitly
            }
        }

    def execute_with_thinking(self, task: str) -> str:
        """Use extended thinking for complex tasks."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=16000,
            thinking={
                "type": "enabled",
                "budget_tokens": 10000
            },
            messages=[{"role": "user", "content": task}]
        )
        return response
```

### Prompt Template Library

```python
TEMPLATES = {
    "code_review": """
<role>Senior {language} developer with security expertise</role>
<task>Review this code for bugs, security issues, and improvements</task>
<code>
{code}
</code>
<output_format>
## Critical Issues
## Warnings
## Suggestions
## Security Concerns
</output_format>
""",

    "architecture_decision": """
<context>{project_context}</context>
<decision_required>{decision}</decision_required>

<analysis_framework>
1. List all viable options
2. For each option, analyze:
   - Technical fit
   - Team expertise match
   - Maintenance burden
   - Scalability implications
3. Recommend with confidence level
</analysis_framework>
""",

    "debug_assistant": """
<error>{error_message}</error>
<code_context>{relevant_code}</code_context>
<environment>{env_details}</environment>

<thinking>
1. Parse the error message
2. Identify likely root causes
3. Check code context for issues
4. Consider environment factors
</thinking>

<solution>
Provide step-by-step fix with explanation
</solution>
"""
}
```

## Workflow: Applying This Skill

### When User Asks for Prompt Analysis

1. Identify the prompt's goal
2. Check for assumption violations (Askell principle #4)
3. Evaluate context efficiency (Schluntz principles)
4. Suggest XML structure improvements
5. Provide stress-test scenarios
6. Offer iteration improvements

### When User Asks for Software Construction

1. Clarify requirements using decomposition
2. Apply 90% comprehension framework to the domain
3. Design tools following Anthropic principles
4. Structure prompts with XML tagging
5. Implement with context management
6. Test with stress scenarios

### When User Wants to Understand a Topic

1. Apply core decomposition (40/30/20/10 rule)
2. Use Feynman technique for fundamentals
3. Conduct expert interview simulation
4. Identify practical applications
5. Create hands-on exercises

## Sources

- [Amanda Askell's Prompt Engineering Secrets](https://startupspells.com/p/amanda-askell-prompt-engineering-secrets)
- [Anthropic Prompt Engineering Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)
- [Building Effective Agents - Anthropic](https://www.anthropic.com/engineering/building-effective-agents)
- [Context Engineering for AI Agents - Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude Best Practices - Anthropic](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Chain of Thought Prompting - Claude Docs](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
