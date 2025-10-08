#!/bin/bash

# EvoMind Quick Start Script

echo "🤖 EvoMind AI Agent System"
echo "============================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set"
    echo "You can:"
    echo "  1. Set it now: export GEMINI_API_KEY='your_key_here'"
    echo "  2. Enter it in the UI sidebar"
    echo "  3. Run without LLM (template mode)"
    echo ""
fi

echo "🚀 Starting EvoMind UI..."
echo "The app will open at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run ui/app.py
