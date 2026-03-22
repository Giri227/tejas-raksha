# Contributing to Agriculture Web Portal Security Scanner

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Follow ethical security practices

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - Scanner version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs
   - Operating system and Python version

### Suggesting Features

1. Check if the feature has been requested
2. Describe the use case
3. Explain the expected behavior
4. Consider implementation complexity

### Contributing Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Update documentation
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agri-scanner.git
cd agri-scanner

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black mypy
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Check types with mypy
mypy src/
```

### Documentation

- Document all public APIs
- Include examples in docstrings
- Update relevant documentation files
- Add inline comments for complex logic

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scanner.py

# Run specific test
pytest tests/test_scanner.py::test_scan_workflow
```

### Writing Tests

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Mock external dependencies

Example:
```python
import pytest
from src.scanner import Scanner

@pytest.mark.asyncio
async def test_scanner_handles_invalid_url():
    """Test that scanner handles invalid URLs gracefully."""
    config = ScanConfig(target_url="invalid-url")
    scanner = Scanner(config)
    
    with pytest.raises(ValueError):
        await scanner.run()
```

## Adding Security Checks

See [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) for detailed instructions.

Quick checklist:
- [ ] Inherit from BaseCheck
- [ ] Implement metadata property
- [ ] Implement execute method
- [ ] Use safe, non-destructive testing
- [ ] Include comprehensive docstrings
- [ ] Write unit tests
- [ ] Update documentation

## Pull Request Process

### Before Submitting

1. **Test your changes**
   ```bash
   pytest
   ```

2. **Format your code**
   ```bash
   black src/ tests/
   ```

3. **Check types**
   ```bash
   mypy src/
   ```

4. **Update documentation**
   - README.md if needed
   - Relevant docs/ files
   - Inline code comments

5. **Update CHANGELOG.md**
   - Add entry under "Unreleased"
   - Describe your changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Code formatted with black
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Automated checks must pass
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Project Structure

```
agri-scanner/
├── src/                    # Source code
│   ├── checks/            # Security check plugins
│   ├── cli/               # Command-line interface
│   ├── crawler/           # Web crawler
│   ├── models/            # Data models
│   ├── reporter/          # Report generators
│   ├── utils/             # Utilities
│   └── scanner.py         # Main controller
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
└── reports/               # Generated reports
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add CORS misconfiguration check
fix: Handle malformed HTML gracefully
docs: Update plugin development guide
test: Add tests for rate limiter
refactor: Simplify URL normalization logic
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security@example.com
2. Include detailed description
3. Provide steps to reproduce
4. Allow time for fix before disclosure

### Security Guidelines

- Never commit credentials
- Use safe test payloads only
- Don't exploit vulnerabilities
- Follow responsible disclosure
- Respect privacy and data

## Documentation

### Types of Documentation

1. **Code Documentation**
   - Docstrings for all public APIs
   - Inline comments for complex logic
   - Type hints

2. **User Documentation**
   - README.md
   - USER_MANUAL.md
   - Configuration examples

3. **Developer Documentation**
   - ARCHITECTURE.md
   - PLUGIN_DEVELOPMENT.md
   - This file (CONTRIBUTING.md)

### Documentation Standards

- Clear and concise
- Include examples
- Keep up to date
- Use proper formatting

## Release Process

1. Update version in `src/__init__.py`
2. Update CHANGELOG.md
3. Create git tag
4. Build distribution
5. Publish to PyPI (if applicable)
6. Create GitHub release

## Getting Help

- Read the documentation
- Check existing issues
- Ask in discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Contact maintainers

Thank you for contributing to make web applications more secure!
