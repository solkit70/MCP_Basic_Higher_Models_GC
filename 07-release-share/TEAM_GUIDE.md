# MCP Web Application - Team Guide

Welcome to the MCP Web Application project! This guide will help you get started as a contributor and team member.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Communication](#communication)

## Getting Started

### Prerequisites Knowledge

Before contributing, you should understand:
- **Python 3.11+**: Async/await, type hints, decorators
- **FastAPI**: REST APIs, Pydantic models, dependency injection
- **MCP Protocol**: JSON-RPC, stdio transport, tool/resource concepts
- **Docker**: Containers, images, docker-compose
- **Git**: Branching, pull requests, rebasing

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Python | 3.11+ | [python.org](https://www.python.org/) |
| Git | 2.30+ | [git-scm.com](https://git-scm.com/) |
| Docker | 20.10+ | [docker.com](https://www.docker.com/) |
| VS Code | Latest | [code.visualstudio.com](https://code.visualstudio.com/) |

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "ms-azuretools.vscode-docker"
  ]
}
```

## Development Setup

### 1. Fork and Clone

```bash
# Fork repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/mcp-web-app.git
cd mcp-web-app

# Add upstream remote
git remote add upstream https://github.com/original/mcp-web-app.git
```

### 2. Environment Setup

**Windows:**
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
cd 04-app-integration/simple-webapp
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

**Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
cd 04-app-integration/simple-webapp
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy example configuration
cp 04-app-integration/simple-webapp/config/.env.example config/.env

# Edit .env with your local paths
# MCP_EXEC_PATH=<your python path> <path to file_server.py>
```

### 4. Verify Setup

```bash
# Run application
cd 04-app-integration/simple-webapp
uvicorn app.main:app --reload

# In another terminal, run tests
pytest

# Check health
curl http://localhost:8000/mcp/health
```

### 5. Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Project Structure

```
MCP_Basic_Higher_Models_GC/
├── 01-foundations/              # MCP concepts documentation
├── 02-env-setup/                # Environment setup scripts
├── 03-discover-servers/         # MCP server examples
├── 04-app-integration/          # Main FastAPI application
│   └── simple-webapp/
│       ├── app/
│       │   ├── main.py          # FastAPI app entry point
│       │   ├── routers/         # API routes
│       │   │   └── mcp.py       # MCP endpoints
│       │   └── services/        # Business logic
│       │       └── mcp_client.py # MCP client implementation
│       ├── config/
│       │   └── .env             # Local configuration (git-ignored)
│       ├── tests/               # Test files
│       └── requirements.txt     # Python dependencies
├── 05-build-server/             # Custom MCP servers
│   ├── file_server.py           # File operations MCP server
│   ├── test_direct.py           # Direct server tests
│   └── test_samples/            # Test data
├── 06-deployment/               # Docker deployment files
│   ├── Dockerfile               # Container definition
│   ├── docker-compose.yml       # Service orchestration
│   └── *.ps1                    # Build/test scripts
├── 07-release-share/            # Documentation & templates
│   ├── README.md                # Project overview
│   ├── DEPLOYMENT_GUIDE.md      # Deployment instructions
│   ├── TEAM_GUIDE.md            # This file
│   ├── API_SPEC.md              # API documentation
│   ├── PROJECT_TEMPLATE/        # Reusable template
│   └── EXAMPLES/                # Usage examples
└── docs/                        # Learning documentation
    └── 20251130_*.md            # Dated guides
```

### Key Files

| File | Purpose | Modify Frequency |
|------|---------|------------------|
| `app/main.py` | FastAPI setup | Rarely |
| `app/routers/mcp.py` | API endpoints | Often |
| `app/services/mcp_client.py` | MCP communication | Often |
| `file_server.py` | MCP server | Often |
| `requirements.txt` | Dependencies | Occasionally |
| `Dockerfile` | Container config | Rarely |

## Development Workflow

### Branch Strategy

```
main (protected)
  ├── develop (integration branch)
  │   ├── feature/add-new-tool
  │   ├── feature/improve-error-handling
  │   ├── bugfix/fix-timeout-issue
  │   └── docs/update-api-spec
  └── release/v1.1.0
```

### Creating a Feature

```bash
# Update develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/add-new-tool

# Make changes, commit frequently
git add .
git commit -m "feat: add weather_check tool to MCP server"

# Push to your fork
git push origin feature/add-new-tool

# Create pull request on GitHub
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(mcp): add weather_check tool

Implement new MCP tool for checking weather using OpenWeatherMap API.
Includes error handling and caching.

Closes #42
```

```
fix(client): resolve UTF-8 encoding issue on Windows

Add explicit encoding='utf-8' parameter to subprocess.Popen to fix
JSON-RPC communication errors on Windows systems.

Fixes #38
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **String Quotes**: Double quotes `"` preferred
- **Import Order**: stdlib, third-party, local
- **Type Hints**: Required for all function signatures

### Code Formatting

**Tools:**
- **Black**: Code formatter
- **Ruff**: Linter (replaces flake8, isort, etc.)
- **mypy**: Type checker

**Configuration (pyproject.toml):**
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E203", "E501"]

[tool.mypy]
python_version = "3.11"
strict = true
```

**Run formatters:**
```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy app/
```

### Documentation

**Docstrings (Google style):**
```python
def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read file contents from disk.

    Args:
        path: Absolute or relative path to file.
        encoding: File encoding (default: utf-8).

    Returns:
        File contents as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        PermissionError: If no read permission.
        UnicodeDecodeError: If encoding is incorrect.

    Example:
        >>> content = read_file("/path/to/file.txt")
        >>> print(content)
        Hello, World!
    """
    with open(path, "r", encoding=encoding) as f:
        return f.read()
```

**Type Hints:**
```python
from typing import Optional, Dict, List, Any

def process_tool_call(
    tool_name: str,
    params: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """Process MCP tool call."""
    ...
```

### Error Handling

**Always provide context:**
```python
# Bad
try:
    result = call_tool(name, params)
except Exception as e:
    raise

# Good
try:
    result = call_tool(name, params)
except McpClientError as e:
    raise McpClientError(
        "tool_call_failed",
        f"Failed to call tool '{name}': {e.message}",
        {"tool": name, "params": params}
    )
except Exception as e:
    raise McpClientError(
        "unexpected_error",
        f"Unexpected error during tool call: {str(e)}",
        {"tool": name, "exception_type": type(e).__name__}
    )
```

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_mcp_client.py
│   └── test_file_server.py
├── integration/             # Integration tests (slower)
│   ├── test_api_endpoints.py
│   └── test_mcp_integration.py
└── e2e/                     # End-to-end tests
    └── test_full_workflow.py
```

### Writing Tests

**Unit Test Example:**
```python
import pytest
from app.services.mcp_client import McpClient

def test_client_initialization():
    """Test MCP client initializes correctly."""
    client = McpClient()
    assert client.config.mode == "stdio"
    assert client.config.timeout_default == 10

def test_list_tools_returns_valid_schema():
    """Test list_tools returns valid tool schema."""
    client = McpClient()
    tools = client.list_tools()

    assert isinstance(tools, list)
    assert len(tools) > 0

    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert isinstance(tool["name"], str)
```

**Integration Test Example:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    """Test health endpoint returns 200."""
    response = client.get("/mcp/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_read_file_tool(client):
    """Test read_file tool via API."""
    response = client.post(
        "/mcp/actions/read_file",
        json={"params": {"path": "test_samples/sample1.txt"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "text" in data["data"]
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_mcp_client.py

# Specific test
pytest tests/unit/test_mcp_client.py::test_client_initialization

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Coverage

Minimum coverage requirements:
- **Overall**: 80%
- **Critical paths**: 90% (mcp_client.py, routers)
- **Utilities**: 70%

Check coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

## Pull Request Process

### 1. Before Creating PR

Checklist:
- [ ] Code follows style guide
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with develop

```bash
# Update your branch
git fetch upstream
git rebase upstream/develop

# Run tests
pytest

# Check style
black --check .
ruff check .
mypy app/
```

### 2. Create Pull Request

**PR Title Format:**
```
[type] Brief description (max 72 chars)
```

**PR Description Template:**
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- Describe tests you've added
- How to test the changes

## Checklist
- [ ] Code follows style guide
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #42
```

### 3. Code Review

**For Reviewers:**
- Check code quality and style
- Verify tests are comprehensive
- Test locally if possible
- Provide constructive feedback

**For Authors:**
- Respond to all comments
- Make requested changes
- Re-request review when ready

### 4. Merge

After approval:
- Squash commits if needed
- Update CHANGELOG.md
- Merge to develop (not main directly)

## Communication

### Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, announcements
- **Pull Requests**: Code reviews, implementation discussion
- **Slack/Discord**: (If applicable) Real-time chat

### Issue Templates

**Bug Report:**
```markdown
**Description**
Clear description of the bug.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- OS: Windows 11
- Python: 3.11.5
- Docker: 24.0.6

**Logs**
```
Paste relevant logs
```
**

**Feature Request:**
```markdown
**Problem Statement**
Describe the problem this feature solves.

**Proposed Solution**
Describe your proposed solution.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other relevant information.
```

### Best Practices

**Do:**
- ✅ Ask questions if unclear
- ✅ Provide context in issues/PRs
- ✅ Be respectful and constructive
- ✅ Help others when you can
- ✅ Update documentation

**Don't:**
- ❌ Push directly to main or develop
- ❌ Commit secrets or sensitive data
- ❌ Ignore CI failures
- ❌ Make large PRs without discussion
- ❌ Remove others' code without discussion

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure you're in virtual environment
which python  # Should show .venv path

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Tests Fail Locally**
```bash
# Check you're in correct directory
cd 04-app-integration/simple-webapp

# Run with verbose output
pytest -v

# Check specific failing test
pytest tests/unit/test_mcp_client.py -v
```

**3. Docker Build Fails**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

**4. Git Issues**
```bash
# Reset to clean state (CAUTION: loses uncommitted changes)
git reset --hard HEAD
git clean -fd

# Update from upstream
git fetch upstream
git merge upstream/develop
```

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Docker Docs](https://docs.docker.com/)

### Learning
- `docs/` folder - Internal guides
- `07-release-share/EXAMPLES/` - Code examples
- GitHub Issues - Past discussions

### Tools
- [Black Playground](https://black.vercel.app/)
- [Ruff Documentation](https://beta.ruff.rs/)
- [mypy Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

## Getting Help

1. **Check Documentation**: Start with README, guides, and API specs
2. **Search Issues**: Your question might be answered
3. **Ask in Discussions**: For general questions
4. **Create Issue**: For bugs or feature requests
5. **Slack/Discord**: For real-time help (if available)

## Contribution Examples

### Example 1: Add New MCP Tool

```python
# 1. Add tool to file_server.py
@mcp.tool()
def calculate_sum(a: float, b: float) -> float:
    """Calculate sum of two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b

# 2. Add test
def test_calculate_sum():
    result = calculate_sum(2.5, 3.5)
    assert result == 6.0

# 3. Update documentation
# - Add to API_SPEC.md
# - Update README.md
# - Add example in EXAMPLES/

# 4. Create PR with title:
# feat(mcp): add calculate_sum tool
```

### Example 2: Fix Bug

```python
# 1. Reproduce bug locally
# 2. Add test that fails
def test_unicode_handling():
    # This test currently fails
    result = read_file("file_with_unicode.txt")
    assert "café" in result

# 3. Fix the bug
# Add encoding parameter

# 4. Verify test passes
# 5. Create PR with title:
# fix(server): handle UTF-8 encoding in file reading
```

## Recognition

Contributors are recognized in:
- CHANGELOG.md (release notes)
- README.md (contributors section)
- GitHub contributors page

Thank you for contributing! 🎉

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0
