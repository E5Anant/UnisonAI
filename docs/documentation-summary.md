# Documentation Summary

## Documentation Files

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Overview, installation, parameter reference |
| [quick-start.md](quick-start.md) | 5-minute setup guide |
| [api-reference.md](api-reference.md) | Complete API documentation |
| [usage-guide.md](usage-guide.md) | Best practices and patterns |
| [tools-guide.md](tools-guide.md) | Tool creation guide (`@tool` and `BaseTool`) |
| [architecture.md](architecture.md) | System design and data flow |

## Examples

| File | What It Shows |
|------|---------------|
| [basic_agent.py](../examples/basic_agent.py) | Minimal agent, no tools |
| [tool_example.py](../examples/tool_example.py) | `@tool` decorator and `BaseTool` class |
| [advanced_tools.py](../examples/advanced_tools.py) | Stateful tools with agent |
| [single_agent_example.py](../examples/single_agent_example.py) | Agent with time and calculator tools |
| [clan-agent_example.py](../examples/clan-agent_example.py) | Multi-agent travel planning clan |
| [clan_coordination.py](../examples/clan_coordination.py) | Research team coordination |

## Learning Path

1. **Start here** — [Quick Start](quick-start.md) (5 min)
2. **Add tools** — [Tool Guide](tools-guide.md) (10 min)
3. **Build a clan** — [Usage Guide](usage-guide.md) (10 min)
4. **Deep dive** — [API Reference](api-reference.md) + [Architecture](architecture.md)

## Checklists

### Setup
- [ ] Python 3.10–3.12 installed
- [ ] `pip install unisonai-sdk`
- [ ] API key configured

### Tool Development
- [ ] Purpose defined
- [ ] Parameters typed correctly
- [ ] Error cases handled
- [ ] Tested with agent

### Clan Development
- [ ] Manager agent chosen
- [ ] Member roles defined
- [ ] Shared instructions written (keep concise)
- [ ] Goal clearly stated
