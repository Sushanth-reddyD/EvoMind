# Contributing to EvoMind

Thank you for your interest in contributing to EvoMind! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/EvoMind.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest`
6. Commit: `git commit -m "Description of changes"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov ruff mypy bandit

# Run tests
pytest

# Run linting
ruff check evomind/

# Run type checking
mypy evomind/
```

## Code Style

- Follow PEP 8 style guide
- Use type hints for function signatures
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add docstrings for public APIs

## Testing

- Write tests for new features
- Maintain or improve test coverage
- Run all tests before submitting PR
- Include both unit and integration tests

## Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG if applicable
5. Request review from maintainers

## Code Review

- Be respectful and constructive
- Address all review comments
- Keep PRs focused and small
- Respond promptly to feedback

## Security

- Report security issues privately to maintainers
- Do not create public issues for security vulnerabilities
- Follow secure coding practices

## Questions?

Open an issue or reach out to maintainers.

Thank you for contributing!
