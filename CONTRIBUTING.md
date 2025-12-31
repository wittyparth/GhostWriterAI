# Contributing to LinkedIn AI Agent

First off, thank you for considering contributing to LinkedIn AI Agent! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Error messages** (if any)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Clear title and description**
- **Use case** - Why is this needed?
- **Proposed solution** (if any)
- **Alternatives considered**

### 🔧 Pull Requests

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/linkedin-ai-agent.git
cd linkedin-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests to verify setup
pytest tests/ -v
```

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Write **docstrings** for all public functions/classes
- Maximum line length: **100 characters**

### Code Formatting

```bash
# Format with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with Ruff
ruff check src/ tests/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Code refactoring
chore: Maintenance tasks
```

### Example:

```
feat(agents): Add sentiment analysis to validator agent

- Added sentiment scoring to validate emotional tone
- Updated system prompt for better analysis
- Added tests for new functionality

Closes #123
```

## Pull Request Process

1. **Ensure tests pass** - Run `pytest tests/ -v`
2. **Update documentation** - If you changed functionality
3. **Update CHANGELOG** - Add entry for your changes
4. **Request review** - Tag maintainers for review

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] Type hints added
- [ ] Docstrings added
- [ ] CHANGELOG updated

## Questions?

Feel free to open an issue with the "question" label!

---

Thank you for contributing! 🚀
