# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project using Python 3.9 with a virtual environment already configured.

## Development Environment

### Virtual Environment
- The project uses a Python 3.9 virtual environment located in `venv/`
- Always activate the virtual environment before running Python commands:
  ```bash
  source venv/bin/activate
  ```

### Python Version
- Python 3.9

## Common Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Install a new package
pip install <package-name>

# Save dependencies
pip freeze > requirements.txt
```

### Running Python Scripts
```bash
# Run a Python script
python <script_name>.py

# Run a module
python -m <module_name>
```

## Project Structure

Currently, this is a newly initialized project with minimal structure. As the project grows, update this section with the main components and their purposes.

## Notes

- The project is currently in its initial state with only a README.md file and virtual environment
- When adding new functionality, consider creating appropriate package structure (e.g., `src/`, `tests/`, etc.)
- Remember to update requirements.txt when adding new dependencies