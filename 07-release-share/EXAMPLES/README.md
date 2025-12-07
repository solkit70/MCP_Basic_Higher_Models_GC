# MCP Web Application - Usage Examples

This directory contains example scripts demonstrating how to use the MCP Web Application API.

## Prerequisites

```bash
# Install required package
pip install requests
```

## Examples

### Example 1: Simple File Query
**File:** `example_1_simple_query.py`

Demonstrates basic usage:
- Health check
- Listing available tools
- Reading file contents

**Run:**
```bash
python example_1_simple_query.py
```

### Example 2: List Directory Contents
**File:** `example_2_list_directory.py`

Demonstrates file listing with:
- Pattern filtering (*.txt, *.json)
- Size formatting
- Directory statistics

**Run:**
```bash
python example_2_list_directory.py
```

### Example 3: Error Handling
**File:** `example_3_error_handling.py`

Demonstrates robust error handling:
- Retry logic
- Timeout management
- Different error types
- Connection failures

**Run:**
```bash
python example_3_error_handling.py
```

## Common Patterns

### Health Check
```python
import requests

response = requests.get("http://localhost:8000/mcp/health")
health = response.json()
print(health['status'])  # 'ok'
```

### List Tools
```python
import requests

response = requests.get("http://localhost:8000/mcp/tools")
tools = response.json()['tools']

for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

### Call Tool
```python
import requests

response = requests.post(
    "http://localhost:8000/mcp/actions/read_file",
    json={
        "params": {
            "path": "/app/test_samples/sample1.txt"
        }
    }
)

result = response.json()
content = result['data']['text']
print(content)
```

### Error Handling
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/mcp/actions/read_file",
        json={"params": {"path": "/nonexistent.txt"}},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
except requests.Timeout:
    print("Request timed out")
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
    print(e.response.json())
except Exception as e:
    print(f"Error: {e}")
```

## Tips

1. **Always check health first** before making tool calls
2. **Use timeouts** to prevent hanging requests
3. **Implement retry logic** for production use
4. **Handle specific errors** appropriately (file not found vs server error)
5. **Log errors with context** for easier debugging

## Next Steps

- Review [API_SPEC.md](../API_SPEC.md) for complete API documentation
- Check [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for deployment options
- See [TEAM_GUIDE.md](../TEAM_GUIDE.md) for contribution guidelines

---

**Last Updated**: 2025-12-07
