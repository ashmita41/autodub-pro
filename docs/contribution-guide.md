# Contribution Guide

Thank you for your interest in contributing to AutoDub Pro! This guide will help you understand how to contribute effectively to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
   ```bash
   git clone https://github.com/yourusername/autodub-pro.git
   cd autodub-pro
   ```
3. **Set up upstream remote**
   ```bash
   git remote add upstream https://github.com/original-owner/autodub-pro.git
   ```
4. **Create a branch** for your feature or bugfix
   ```bash
   git checkout -b feature-branch-name
   ```

## Development Environment

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system
- Poetry for dependency management

### Setting Up Development Environment

1. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Install pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

### Virtual Environment

We recommend using Poetry's built-in virtual environment management:

```bash
poetry shell
```

## Coding Standards

We follow PEP 8 guidelines with a few customizations:

### Code Style

- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (enforced by Black)
- Use snake_case for functions and variables
- Use CamelCase for classes
- Use descriptive names for variables, functions, and classes

### Code Quality Tools

We use several tools to ensure code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **Flake8**: For linting
- **mypy**: For type checking

Run the quality checks:

```bash
# Format code
poetry run black .
poetry run isort .

# Check code quality
poetry run flake8
poetry run mypy autodub_pro
```

### Type Hints

Use type hints for all function parameters and return values:

```python
def process_subtitle(text: str, language: str) -> dict[str, str]:
    """
    Process subtitle text for the given language.
    
    Args:
        text: The subtitle text to process
        language: The language code
        
    Returns:
        A dictionary containing processed text
    """
    # Implementation
    return {"processed_text": text}
```

## Testing

We use pytest for testing. All new code should include appropriate tests.

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=autodub_pro

# Run specific test file
poetry run pytest tests/test_subtitle.py
```

### Writing Tests

- Test files should be placed in the `tests/` directory
- Test file names should start with `test_`
- Test function names should start with `test_`
- Use descriptive test names that explain what is being tested

Example test:

```python
def test_subtitle_processor_loads_srt_file(tmp_path):
    """Test that the SubtitleProcessor can load an SRT file."""
    # Create a test file
    test_file = tmp_path / "test.srt"
    test_file.write_text("1\n00:00:01,000 --> 00:00:02,000\nTest subtitle\n\n")
    
    # Test the function
    from autodub_pro.subtitle import SubtitleProcessor
    processor = SubtitleProcessor()
    subtitles = processor.load_from_file(str(test_file))
    
    # Assert the result
    assert len(subtitles) == 1
    assert subtitles[0].text == "Test subtitle"
```

## Pull Request Process

1. **Update your fork** with the latest changes from upstream
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Commit your changes** with clear and descriptive commit messages
   ```bash
   git commit -m "Add feature X to improve Y functionality"
   ```

3. **Push your branch** to your fork
   ```bash
   git push origin feature-branch-name
   ```

4. **Create a Pull Request** from your branch to the upstream repository's main branch

5. **PR Requirements**:
   - PR title should clearly describe the change
   - PR description should explain the purpose and implementation details
   - All tests must pass
   - Code must follow our coding standards
   - New features must include appropriate tests and documentation

6. **Code Review**:
   - Address all review comments
   - Make additional commits to address feedback
   - Once approved, your PR will be merged

## Documentation

Good documentation is crucial. When contributing code:

- Update or add docstrings for all public functions, classes, and modules
- Update the relevant documentation files if needed
- Add examples for new functionality

### Documentation Style

We use Google-style docstrings:

```python
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language.
    
    Args:
        text: The text to translate
        source_lang: The source language code (e.g., 'en')
        target_lang: The target language code (e.g., 'es')
        
    Returns:
        The translated text
        
    Raises:
        TranslationError: If translation fails
    """
    # Implementation
```

## Release Process

Our release process follows these steps:

1. Version bump following semantic versioning
2. Changelog update
3. Release creation on GitHub
4. PyPI package publication

Contributors aren't responsible for releases, but should be aware of the versioning system:

- **MAJOR** version for incompatible API changes
- **MINOR** version for functionality added in a backward-compatible manner
- **PATCH** version for backward-compatible bug fixes

## Community

- **Discussions**: Use GitHub Discussions for questions and ideas
- **Issues**: Report bugs or request features through GitHub Issues
- **Discord**: Join our Discord server for real-time communication

## Need Help?

If you need help at any point in the contribution process:

- Check the documentation
- Look for similar issues on GitHub
- Ask in the community Discord channel
- Reach out to the maintainers

Thank you for contributing to AutoDub Pro! 