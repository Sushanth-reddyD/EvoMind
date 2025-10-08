# EvoMind

Production-ready AI Agent System with dynamic tool creation, Gemini LLM integration, and interactive UI.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Sushanth-reddyD/EvoMind.git
cd EvoMind

# 2. Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set your Gemini API key (optional, for LLM features)
export GEMINI_API_KEY="your_api_key_here"

# 4. Run the interactive UI
./run_ui.sh
# Or: streamlit run ui/app.py
```

The UI will open at `http://localhost:8501` 🎉

## Overview

EvoMind is a comprehensive AI agent framework that can dynamically author and execute its own Python tools in a secure, isolated environment. Now with **Google Gemini LLM integration** and an **interactive Streamlit UI**!

### Key Features

- **🤖 Gemini LLM Integration**: AI-powered code generation, planning, and chat
- **🎨 Interactive UI**: Web-based interface with Streamlit
- **🔄 Dual Mode**: LLM-powered or template-based generation
- **🛡️ Safe Execution**: Sandboxed environment with resource limits
- **🧠 Intelligent Planning**: ReAct (default) and Tree of Thoughts
- **🔧 Dynamic Tools**: Generate Python functions on-the-fly
- **📊 Observability**: Metrics, logging, and execution history

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Controller                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Planning   │  │   Context    │  │    State     │      │
│  │  (ReAct/ToT) │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│  Code Generator │ │  Tool Registry  │ │    Sandbox     │
│                 │ │                 │ │   Executor     │
│  - Templates    │ │  - Storage      │ │  - Isolation   │
│  - Validation   │ │  - Search       │ │  - Limits      │
│  - SAST         │ │  - Versioning   │ │  - Policies    │
└─────────────────┘ └─────────────────┘ └────────────────┘
```

## Features

### Core Capabilities

- **Dynamic Tool Creation**: Generate and validate Python tools on-the-fly
- **Safe Execution**: Sandbox isolation with CPU, memory, and time limits
- **Intelligent Planning**: ReAct for standard tasks, ToT for complex reasoning
- **Self-Correction**: Reflexion-based learning from failures
- **Tool Discovery**: Semantic search across registered tools

### Security

- Static code analysis (AST parsing, policy gates, SAST)
- Execution sandboxing with resource limits
- Network and filesystem restrictions
- Audit logging for all operations
- Input validation and output sanitization

### Observability

- RED (Rate, Errors, Duration) metrics
- Structured JSON logging
- Audit trails
- Performance monitoring

## Installation

```bash
# Clone repository
git clone https://github.com/Sushanth-reddyD/EvoMind.git
cd EvoMind

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### Using the CLI

```bash
# Submit a task
python -m evomind.cli submit "Parse JSON and select fields"

# List available tools
python -m evomind.cli list-tools

# Inspect a tool
python -m evomind.cli inspect tool_name_0.1.0 --show-code

# Dry run a tool
python -m evomind.cli dry-run tool_name_0.1.0 --args '{"input": "test"}'

# View metrics
python -m evomind.cli metrics
```

### Using the API

```bash
# Start the API server
python -m evomind.api

# In another terminal, submit a request
curl -X POST http://localhost:8000/agent/request \
  -H "Content-Type: application/json" \
  -d '{"task": "Parse JSON data", "args": {}}'

# List tools
curl http://localhost:8000/tools

# Health check
curl http://localhost:8000/health
```

### Using the Python API

```python
from evomind import AgentController

# Create agent
agent = AgentController()

# Submit request
result = agent.handle_request({
    "task": "Transform data with custom logic"
})

print(result)
```

## Configuration

Configuration can be provided via environment variables or configuration file.

### Environment Variables

```bash
export EVOMIND_CONFIDENCE_THRESHOLD=0.7
export EVOMIND_MAX_RETRIES=3
export EVOMIND_LLM_PROVIDER=openai
export EVOMIND_LLM_MODEL=gpt-4
export EVOMIND_SANDBOX_CPU_LIMIT=30
export EVOMIND_SANDBOX_MEMORY_MB=512
export EVOMIND_LOG_LEVEL=INFO
```

### Configuration File

Create `config.yaml`:

```yaml
confidence_threshold: 0.7
max_retries: 3
llm_provider: openai
llm_model: gpt-4
sandbox_cpu_limit: 30
sandbox_memory_mb: 512
log_level: INFO
```

## Project Structure

```
evomind/
├── agent/              # Agent controller and planning
│   ├── controller.py   # Main agent loop
│   ├── planner.py      # ReAct/ToT planners
│   └── state.py        # State management
├── codegen/            # Code generation
│   ├── generator.py    # Code generator
│   └── validators.py   # Static validation
├── sandbox/            # Execution sandbox
│   ├── executor.py     # Sandbox executor
│   └── policies.py     # Security policies
├── registry/           # Tool registry
│   └── tool_registry.py
├── observability/      # Metrics and logging
│   ├── metrics.py
│   └── logging.py
├── utils/              # Utilities
│   ├── config.py
│   ├── retry.py
│   └── validators.py
├── cli.py              # CLI interface
└── api.py              # REST API
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=evomind --cov-report=html

# Run specific test file
pytest tests/test_agent.py
```

### Code Quality

```bash
# Linting
ruff check evomind/

# Type checking
mypy evomind/

# Security scanning
bandit -r evomind/
```

## Architecture Decisions

### Planning Strategy

- **ReAct (Default)**: Efficient reasoning-acting loop for standard tasks
- **ToT (Escalation)**: Tree of Thoughts for complex tasks requiring exploration
- **Reflexion**: Episodic memory for learning from failures

### Code Generation

- **PAL Approach**: Program-Aided Language model - generates code but lets Python runtime execute
- Reduces hallucination in mathematical/logical operations
- Template-based with LLM fallback for complex cases

### Sandboxing

- **Current**: Subprocess with resource limits
- **Production**: gVisor, nsjail, or Firecracker recommended
- Resource policies: CPU time, memory, disk, network controls

### Tool Registry

- **Storage**: File-based (local development)
- **Production**: OCI artifacts with semantic versioning
- **Discovery**: Lexical + embedding search, metadata indexing

## Roadmap

### Phase 1 (MVP) ✅
- [x] Agent controller with ReAct planning
- [x] Code generation with static validation
- [x] Subprocess-based sandbox
- [x] File-based tool registry
- [x] CLI and API interfaces
- [x] Basic observability

### Phase 2 (Enhancements)
- [ ] ToT planner improvements
- [ ] LLM integration for code generation
- [ ] Enhanced reflexion with vector storage
- [ ] OCI registry support
- [ ] Network policy enforcement
- [ ] Circuit breaker pattern

### Phase 3 (Production)
- [ ] gVisor/nsjail integration
- [ ] Kubernetes deployment configs
- [ ] Distributed tool registry
- [ ] Advanced metrics (OpenTelemetry)
- [ ] Multi-tenant isolation
- [ ] Chaos engineering tests

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - See LICENSE file for details.

## References

- [ReAct: Reasoning and Acting](https://arxiv.org/abs/2210.03629)
- [Tree of Thoughts](https://arxiv.org/abs/2305.10601)
- [PAL: Program-Aided Language Models](https://arxiv.org/abs/2211.10435)
- [Reflexion: Self-Reflection for Agents](https://arxiv.org/abs/2303.11366)
- [gVisor Documentation](https://gvisor.dev/)

## Support

For issues, questions, or contributions, please open an issue on GitHub.