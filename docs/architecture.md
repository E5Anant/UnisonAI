# Architecture Guide

## High-Level Overview

```
┌──────────────────────────────────────────────────┐
│                  UnisonAI Framework              │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Agent   │  │   Clan   │  │  Tools   │        │
│  │          │  │          │  │          │        │
│  │ • LLM    │  │ • Plan   │  │ • @tool  │        │
│  │ • Tools  │  │ • Assign │  │ • Base   │        │
│  │ • Loop   │  │ • A2A    │  │ • Field  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
│       │              │              │            │
│       ▼              ▼              ▼            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ LLM      │  │ History  │  │ Prompts  │        │
│  │ Providers│  │ (JSON)   │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────┘
```

---

## Core Components

### Agent

The central class. Works standalone or as part of a Clan.

**Standalone flow:**

```
User  →  Agent.unleash(task)
              │
              ▼
         Build system prompt (INDIVIDUAL_PROMPT)
              │
              ▼
         Agentic loop (max 10 turns):
           1. LLM generates response
           2. Extract <tool>...</tool> calls
           3. Execute tools safely (ast.parse)
           4. Feed results back to LLM
           5. Repeat until no tools → final answer
              │
              ▼
         Return answer
```

**Clan member flow:**

```
Manager  →  send_message(agent_name, message)
                 │
                 ▼
            Member.unleash(message)
                 │
                 ▼
            Same agentic loop, but uses AGENT_PROMPT
            with team info, plan, and shared instructions
                 │
                 ▼
            pass_result(result)  →  returned to Manager
```

### Clan

Coordinates multiple agents.

```
User  →  Clan.unleash()
              │
              ▼
         1. Planning Phase
            Manager LLM generates step-by-step plan
              │
              ▼
         2. Distribution
            Plan shared with all member agents
              │
              ▼
         3. Execution
            Manager.unleash(goal)
            Manager delegates via send_message()
            Members execute and return via pass_result()
              │
              ▼
         4. Completion
            Manager calls pass_result() → final output
```

### Tool System

```
@tool decorator  ──┐
                   ├──  BaseTool instance  ──  Agent.tools
BaseTool class  ──┘         │
                            ▼
                     create_tools()
                     (generates function signatures
                      for the system prompt)
```

**Tool execution safety:**

```
LLM Output:  <tool>calculator(operation="add", a=5, b=3)</tool>
                │
                ▼
         ast.parse()  →  validate function name
                │
                ▼
         ast.literal_eval()  →  parse arguments safely
                │
                ▼
         tool.run(**kwargs)  →  ToolResult
                │
                ▼
         Result fed back to LLM
```

---

## Prompt System

| Prompt | Used When | Key Placeholders |
|--------|-----------|-----------------|
| `INDIVIDUAL_PROMPT` | Standalone agent | `{identity}`, `{description}`, `{user_task}`, `{tools}` |
| `AGENT_PROMPT` | Clan member | Above + `{clan_name}`, `{plan}`, `{members}`, `{shared_instruction}` |
| `MANAGER_PROMPT` | Clan manager | Same as agent + `ask_user` docs |
| `PLAN_PROMPT` | Planning phase | `{members}`, `{client_task}` |

---

## Data Flow

### Conversation History

```
Agent.unleash()
    │
    ├── Load history from {history_folder}/{identity}.json
    │   (catches JSONDecodeError for corrupt files)
    │
    ├── Run agentic loop (appends messages)
    │
    └── Save updated history to JSON after each turn
```

### A2A Messaging

```
Manager                          Member
   │                                │
   ├── send_message("Member", msg) ─┤
   │                                ├── Member.unleash(msg)
   │                                ├── (runs own agentic loop)
   │                                ├── pass_result(result)
   │◄── "Message delivered." ───────┤
   │                                │
   ├── (continues with result)      │
```

---

## File Structure

```
unisonai/
├── __init__.py          # Exports: Agent, Clan, BaseTool, Field
├── agent.py             # Agent class, create_tools(), tool execution
├── clan.py              # Clan class, planning + execution
├── async_helper.py      # Async/sync bridge utilities
├── prompts/
│   ├── individual.py    # INDIVIDUAL_PROMPT
│   ├── agent.py         # AGENT_PROMPT
│   ├── manager.py       # MANAGER_PROMPT
│   └── plan.py          # PLAN_PROMPT
├── tools/
│   ├── tool.py          # BaseTool, Field, ToolResult, @tool
│   ├── types.py         # ToolParameterType enum
│   └── rag.py           # RAGTool
└── llms/
    ├── Basellm.py       # Abstract BaseLLM
    ├── genai.py          # Gemini
    ├── openaillm.py      # OpenAI
    ├── anthropicllm.py   # Anthropic
    ├── coherellm.py      # Cohere
    ├── groqllm.py        # Groq
    ├── mixtral.py        # Mixtral
    ├── xai.py            # xAI
    └── cerebras.py       # Cerebras
```
