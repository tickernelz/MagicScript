# Contributing to MagicScript

Thank you for your interest in contributing to MagicScript! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Code Contributions](#code-contributions)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [your-email@example.com].

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a branch for your changes

## How to Contribute

### Reporting Bugs

Before submitting a bug report:

1. Check the [issue tracker](https://github.com/yourusername/MagicScript/issues) to see if the issue has already been reported
2. Update your software to the latest version to see if the issue persists

When submitting a bug report, include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots if applicable
- Your operating system and MagicScript version
- Any relevant log output (`magic_script.log`)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

1. Use a clear, descriptive title
2. Provide a detailed description of the suggested enhancement
3. Explain why this enhancement would be useful
4. Include any relevant examples or mockups

### Code Contributions

1. Create a new branch for your feature or bugfix
2. Write your code following the style guidelines
3. Add or update tests as necessary
4. Update documentation to reflect your changes
5. Submit a pull request

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MagicScript.git
   cd MagicScript
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```
   pip install pytest flake8
   ```

4. Run the application:
   ```
   python magic_script.py
   ```

## Pull Request Process

1. Update the README.md and documentation with details of changes if applicable
2. Update the CHANGELOG.md with details of changes
3. The PR should work on Windows 10 and later
4. Ensure all tests pass
5. Your PR will be reviewed by maintainers, who may request changes

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add Random Range from Current Position mouse movement option

This adds a new mouse movement type that creates more natural-looking
movements by randomly moving within a specified range from the current
cursor position.

Fixes #123
```

### Documentation

- Update documentation to reflect your changes
- Use clear, concise language
- Include examples where appropriate

Thank you for contributing to MagicScript!