# AI Models by Task - GitHub Copilot Reference

A quick reference guide for selecting the right AI model based on your development task.

---

## Quick Reference Table

| Model | Task Area | Primary Use Case | Capabilities |
|-------|-----------|------------------|--------------|
| GPT-4.1 | General-purpose | Fast code completions | Agent, Vision |
| GPT-5.2 | Deep reasoning | Multi-step problem solving | Agent |
| GPT-5.1 | Deep reasoning | Architecture-level analysis | Agent |
| GPT-5-Codex | General-purpose | Fast code completions | Agent |
| GPT-5 mini | General-purpose | Fast code completions | Agent, Reasoning, Vision |
| GPT-5 | Deep reasoning | Multi-step problem solving | Reasoning |
| Claude Haiku 4.5 | Fast/simple tasks | Lightweight coding questions | Agent |
| Claude Sonnet 4.5 | General-purpose/Agent | Complex problem-solving | Agent |
| Claude Opus 4.1 | Deep reasoning | Sophisticated reasoning | Reasoning, Vision |
| Claude Sonnet 4 | Deep reasoning | Balanced coding workflows | Agent, Vision |
| Gemini 2.5 Pro | Deep reasoning | Complex code generation | Reasoning, Vision |
| Gemini 3 Flash | Fast/simple tasks | Lightweight coding questions | Agent |
| Grok Code Fast 1 | General-purpose | Fast code completions | Agent |
| Qwen2.5 | General-purpose | Code generation & repair | Reasoning |
| Raptor mini | General-purpose | Fast code completions | Agent |

---

## Task Categories

### General-Purpose Coding and Writing

For common development tasks requiring balance of quality, speed, and cost.

**Recommended Models:**

| Model | Why It's a Good Fit |
|-------|---------------------|
| **GPT-5-Codex** | Higher-quality code on complex tasks (features, tests, debugging, refactors, reviews) without lengthy instructions |
| **GPT-5 mini** | Reliable default for most tasks. Fast, accurate, works across languages/frameworks |
| **Grok Code Fast 1** | Specialized for coding. Strong at code generation and debugging |
| **Raptor mini** | Specialized for fast, accurate inline suggestions and explanations |

**Use when you want to:**
- Write or review functions, short files, or code diffs
- Generate documentation, comments, or summaries
- Explain errors or unexpected behavior quickly
- Work in non-English programming environments

---

### Fast Help with Simple or Repetitive Tasks

Optimized for speed and responsiveness - quick edits, utility functions, syntax help.

**Recommended Models:**

| Model | Why It's a Good Fit |
|-------|---------------------|
| **Claude Haiku 4.5** | Balances fast responses with quality. Ideal for small tasks and lightweight explanations |

**Use when you want to:**
- Write or edit small functions or utility code
- Ask quick syntax or language questions
- Prototype ideas with minimal setup
- Get fast feedback on simple prompts or edits

---

### Deep Reasoning and Debugging

For step-by-step reasoning, complex decision-making, or high-context awareness.

**Recommended Models:**

| Model | Why It's a Good Fit |
|-------|---------------------|
| **GPT-5 mini** | Deep reasoning with faster responses and lower resource usage than GPT-5 |
| **GPT-5** | Great at complex reasoning, code analysis, and technical decision-making |
| **Claude Sonnet 4** | More reliable completions and smarter reasoning under pressure |
| **Claude Opus 4.1** | Anthropic's most powerful model |
| **Gemini 2.5 Pro** | Advanced reasoning across long contexts and technical analysis |

**Use when you want to:**
- Debug complex issues across multiple files
- Refactor large or interconnected codebases
- Plan features or architecture across layers
- Weigh trade-offs between libraries, patterns, or workflows
- Analyze logs, performance data, or system behavior

---

### Working with Visuals (Diagrams, Screenshots)

For multimodal input - screenshots, diagrams, UI components, visual debugging.

**Recommended Models:**

| Model | Why It's a Good Fit |
|-------|---------------------|
| **GPT-5 mini** | Supports multimodal input for visual reasoning tasks |
| **Claude Sonnet 4** | Reliable completions with visual context |
| **Gemini 2.5 Pro** | Deep reasoning ideal for visual debugging and research |

**Use when you want to:**
- Ask questions about diagrams, screenshots, or UI components
- Get feedback on visual drafts or workflows
- Understand front-end behavior from visual context

---

## Decision Flowchart

```
Start
  │
  ├─► Need speed? ──────────────► Claude Haiku 4.5
  │
  ├─► Working with images? ─────► GPT-5 mini / Claude Sonnet 4 / Gemini 2.5 Pro
  │
  ├─► Complex debugging? ───────► GPT-5 / Claude Opus 4.1 / Gemini 2.5 Pro
  │
  ├─► Multi-file refactor? ─────► Claude Sonnet 4 / GPT-5
  │
  └─► General coding? ──────────► GPT-5 mini / GPT-5-Codex / Grok Code Fast 1
```

---

## Notes

- **Grok Code Fast 1**: Complimentary access continuing past previously announced end time
- **Default recommendation**: Start with GPT-4.1 or GPT-5 mini, adjust based on needs
- **Agent mode**: Available on most models for autonomous task completion
- **Vision**: Required for image/screenshot analysis tasks

---

## Further Reading

- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/using-github-copilot/ai-models/supported-ai-models)
- [Comparing AI models using different tasks](https://docs.github.com/en/copilot/using-github-copilot/ai-models/comparing-ai-models)
- [Changing the AI model for Copilot Chat](https://docs.github.com/en/copilot/using-github-copilot/ai-models/changing-ai-model-chat)
- [Extending Copilot with MCP servers](https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-mcp)

---

*Source: GitHub Copilot Documentation - January 2026*
