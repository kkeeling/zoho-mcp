# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

IMPORTANT: Install all dependencies in the `zoho-mcp` conda environment.

## Build and Test Commands
- Activate conda environment: `conda activate zoho-mcp`
- Install dependencies: `pip install -r requirements.txt`
- Run server: `python server.py`
- Run all tests: `pytest`
- Run specific test: `pytest tests/test_file.py::TestClass::test_function`
- Run tests with coverage: `pytest --cov=zoho_mcp`
- Lint code: `flake8 zoho_mcp tests`
- Type check: `mypy zoho_mcp`

## Code Style Guidelines
- Python 3.9+ with type hints throughout
- Follow PEP 8 style guidelines
- Maximum line length: 100 characters
- Use docstrings for all functions, classes, and modules
- Imports: standard library first, then third-party, then local modules
- Class naming: PascalCase
- Function/variable naming: snake_case
- Constants: UPPER_SNAKE_CASE
- Error handling: use specific exceptions with contextual messages
- Logging: use structured logging with appropriate log levels
- Testing: use pytest with proper fixtures and mocking

## Must-Follow Instructions
- Always read the table of contents for the documentation at `specs/docs/toc.md` to understand what documentation exists and is relevant to the task at hand.