"""Interactive Streamlit UI for EvoMind AI Agent System."""

import streamlit as st
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evomind.agent.controller import AgentController
from evomind.llm.gemini_client import GeminiClient
from evomind.codegen.generator import CodeGenerator
from evomind.agent.planner import ReActPlanner
from evomind.utils.config import Config

# Page config
st.set_page_config(
    page_title="EvoMind - AI Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-success {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-error {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .code-block {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'llm_client' not in st.session_state:
    st.session_state.llm_client = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

def initialize_agent(use_llm: bool, api_key: str = None):
    """Initialize the agent with optional LLM."""
    try:
        if use_llm:
            if api_key:
                os.environ['GEMINI_API_KEY'] = api_key
            st.session_state.llm_client = GeminiClient()
            code_generator = CodeGenerator(
                llm_client=st.session_state.llm_client,
                use_llm=True
            )
            planner = ReActPlanner(
                llm_client=st.session_state.llm_client,
                use_llm=True
            )
        else:
            st.session_state.llm_client = None
            code_generator = CodeGenerator(use_llm=False)
            planner = ReActPlanner(use_llm=False)
        
        st.session_state.agent = AgentController(
            code_generator=code_generator
        )
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return False

def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🤖 EvoMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI Agent System with Dynamic Tool Generation</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        use_llm = st.checkbox(
            "Enable Gemini LLM",
            value=False,
            help="Use Gemini for code generation and planning"
        )
        
        api_key = None
        if use_llm:
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                value=os.getenv("GEMINI_API_KEY", ""),
                help="Enter your Gemini API key or set GEMINI_API_KEY environment variable"
            )
            
            if not api_key:
                st.warning("⚠️ Please provide API key to use Gemini")
        
        if st.button("Initialize Agent", type="primary"):
            with st.spinner("Initializing agent..."):
                if initialize_agent(use_llm, api_key):
                    st.success("✅ Agent initialized successfully!")
        
        st.divider()
        
        st.header("📊 Statistics")
        if st.session_state.agent:
            st.metric("Tasks Completed", len(st.session_state.history))
            st.metric("Conversations", len(st.session_state.conversation))
            st.metric("Mode", "LLM" if use_llm else "Template")
        
        st.divider()
        
        if st.button("Clear History"):
            st.session_state.history = []
            st.session_state.conversation = []
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Task Execution",
        "💬 Chat Interface",
        "🔧 Code Generator",
        "📜 History"
    ])
    
    # Tab 1: Task Execution
    with tab1:
        st.header("Task Execution")
        
        if not st.session_state.agent:
            st.info("👆 Please initialize the agent from the sidebar first")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                task_input = st.text_area(
                    "Describe your task:",
                    height=100,
                    placeholder="Example: Create a function to calculate fibonacci numbers"
                )
            
            with col2:
                st.subheader("Options")
                confidence_threshold = st.slider(
                    "Confidence Threshold",
                    0.0, 1.0, 0.7,
                    help="Minimum confidence to proceed"
                )
                max_retries = st.number_input(
                    "Max Retries",
                    1, 5, 3,
                    help="Maximum retry attempts"
                )
            
            if st.button("🚀 Execute Task", type="primary"):
                if task_input:
                    with st.spinner("Processing task..."):
                        try:
                            request = {"task": task_input}
                            result = st.session_state.agent.handle_request(request)
                            
                            # Add to history
                            st.session_state.history.append({
                                "task": task_input,
                                "result": result
                            })
                            
                            # Display result
                            if result.get("status") == "success":
                                st.markdown('<div class="status-success">✅ Task completed successfully!</div>', unsafe_allow_html=True)
                                
                                with st.expander("📋 Result Details", expanded=True):
                                    st.json(result)
                                
                                if "code" in result.get("result", {}):
                                    with st.expander("💻 Generated Code", expanded=True):
                                        st.code(result["result"]["code"], language="python")
                            
                            elif result.get("status") == "degraded":
                                st.warning("⚠️ Task completed with issues")
                                st.markdown(f'**Message:** {result.get("message", "Unknown")}')
                                
                                # Show feedback details
                                with st.expander("🔍 Feedback & Error Details", expanded=True):
                                    feedback = result.get("feedback", [])
                                    for i, fb in enumerate(feedback):
                                        st.write(f"**Issue {i+1}:** {fb.get('category', 'unknown')}")
                                        if 'details' in fb:
                                            details = fb['details']
                                            if 'findings' in details:
                                                st.error("Validation Errors:")
                                                for finding in details['findings']:
                                                    st.write(f"- Line {finding.get('line', '?')}: {finding.get('message', 'error')}")
                                    
                                    st.json(result)
                                
                                # Suggest template mode
                                st.info("💡 **Tip:** If using LLM mode, try:\n1. Simplifying the task description\n2. Disabling LLM to use template mode\n3. Providing more specific requirements")
                            
                            else:
                                st.markdown(f'<div class="status-error">❌ {result.get("message", "Task failed")}</div>', unsafe_allow_html=True)
                                with st.expander("🔍 Details", expanded=True):
                                    st.json(result)
                        
                        except Exception as e:
                            st.error(f"Error: {e}")
                            import traceback
                            with st.expander("Stack Trace"):
                                st.code(traceback.format_exc())
                else:
                    st.warning("Please enter a task description")
    
    # Tab 2: Chat Interface
    with tab2:
        st.header("Chat with EvoMind")
        
        if not st.session_state.llm_client:
            st.info("💡 Enable Gemini LLM in the sidebar to use chat")
        else:
            # Display conversation
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.conversation:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask me anything about code or tasks..."):
                # Add user message
                st.session_state.conversation.append({
                    "role": "user",
                    "content": prompt
                })
                
                # Display user message
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Get response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.llm_client.chat(
                                message=prompt,
                                conversation_history=st.session_state.conversation[:-1]
                            )
                            st.write(response)
                            
                            # Add assistant message
                            st.session_state.conversation.append({
                                "role": "assistant",
                                "content": response
                            })
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    # Tab 3: Code Generator
    with tab3:
        st.header("Direct Code Generator")
        
        if not st.session_state.agent:
            st.info("👆 Please initialize the agent from the sidebar first")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                func_name = st.text_input(
                    "Function Name",
                    "my_function",
                    help="Name of the function to generate"
                )
                
                description = st.text_area(
                    "Description",
                    height=100,
                    placeholder="Describe what the function should do..."
                )
            
            with col2:
                input_type = st.text_input("Input Type", "dict")
                output_type = st.text_input("Output Type", "dict")
                
                timeout = st.number_input("Timeout (s)", 1, 300, 30)
                memory_mb = st.number_input("Memory Limit (MB)", 128, 2048, 512)
            
            if st.button("🔨 Generate Code", type="primary"):
                if description and func_name:
                    with st.spinner("Generating code..."):
                        try:
                            spec = {
                                "name": func_name,
                                "description": description,
                                "io_spec": {
                                    "input": input_type,
                                    "output": output_type
                                },
                                "constraints": {
                                    "timeout": timeout,
                                    "memory_mb": memory_mb
                                },
                                "tests": []
                            }
                            
                            result = st.session_state.agent.code_generator.create_tool(spec)
                            
                            if result.get("status") == "READY":
                                st.success("✅ Code generated successfully!")
                                
                                code = result.get("code", "")
                                st.code(code, language="python")
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Code",
                                    data=code,
                                    file_name=f"{func_name}.py",
                                    mime="text/plain"
                                )
                            else:
                                st.error(f"❌ Generation failed: {result.get('reason')}")
                                with st.expander("Details"):
                                    st.json(result)
                        
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please provide function name and description")
    
    # Tab 4: History
    with tab4:
        st.header("Execution History")
        
        if not st.session_state.history:
            st.info("No execution history yet")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Task {len(st.session_state.history) - i}: {item['task'][:50]}..."):
                    st.write("**Task:**", item['task'])
                    st.write("**Status:**", item['result'].get('status', 'unknown'))
                    st.json(item['result'])

if __name__ == "__main__":
    main()
