# EvoMind UI

Interactive web interface for the EvoMind AI Agent System.

## Features

- **Task Execution**: Submit natural language tasks for automatic tool generation and execution
- **Chat Interface**: Interactive chat with Gemini LLM for coding assistance
- **Code Generator**: Direct code generation with custom specifications
- **Execution History**: Track all tasks and results

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Gemini API key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Or enter it in the UI sidebar.

## Running the UI

### Streamlit (Recommended)

```bash
streamlit run ui/app.py
```

The UI will open at `http://localhost:8501`

### Without LLM (Template Mode)

You can run the UI without an API key - it will use template-based code generation:

```bash
streamlit run ui/app.py
```

Just don't enable "Use Gemini LLM" in the sidebar.

## Usage

1. **Initialize Agent**: Click "Initialize Agent" in the sidebar
2. **Choose Mode**: 
   - Enable "Use Gemini LLM" for AI-powered generation
   - Leave it off for template-based generation
3. **Execute Tasks**: Go to "Task Execution" tab and describe your task
4. **Chat**: Use the "Chat Interface" tab to ask questions
5. **Generate Code**: Use "Code Generator" for direct function generation

## Configuration Options

- **Confidence Threshold**: Minimum confidence to proceed with a task (0.0-1.0)
- **Max Retries**: Maximum retry attempts if task fails (1-5)
- **Timeout**: Maximum execution time for generated code (seconds)
- **Memory Limit**: Maximum memory usage for code execution (MB)

## Example Tasks

- "Create a function to calculate fibonacci numbers"
- "Generate a JSON parser that validates schema"
- "Build a function to sort a list of dictionaries by a key"
- "Create a data transformer that converts CSV to JSON"

## Troubleshooting

### API Key Issues
- Make sure `GEMINI_API_KEY` is set in environment or entered in UI
- Check that the API key is valid and has access to Gemini models

### Import Errors
- Run from the project root directory
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Port Already in Use
- Change the port: `streamlit run ui/app.py --server.port 8502`
