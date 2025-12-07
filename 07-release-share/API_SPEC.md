# MCP Web Application - API Specification

Complete API documentation for the MCP Web Application RESTful endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. For production deployment, implement:
- API Keys
- OAuth 2.0
- JWT tokens

## Common Headers

```
Content-Type: application/json
Accept: application/json
```

## Response Format

### Success Response

```json
{
  "tool": "tool_name",
  "data": {
    "text": "result data"
  },
  "latency_ms": 12,
  "success": true
}
```

### Error Response

```json
{
  "detail": {
    "code": "error_code",
    "message": "Human-readable error message",
    "detail": {}
  }
}
```

## Endpoints

### Health Check

Get server health status.

**Endpoint:** `GET /mcp/health`

**Response:**
```json
{
  "status": "ok",
  "server_type": "stdio"
}
```

**Example:**
```bash
curl http://localhost:8000/mcp/health
```

---

### List Tools

Get all available MCP tools.

**Endpoint:** `GET /mcp/tools`

**Response:**
```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "파일 내용을 읽어서 반환합니다..."
    },
    {
      "name": "list_files",
      "description": "디렉토리 내의 파일과 폴더 목록을 조회합니다..."
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/mcp/tools
```

---

### Read File

Read contents of a file.

**Endpoint:** `POST /mcp/actions/read_file`

**Request Body:**
```json
{
  "params": {
    "path": "/path/to/file.txt"
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute or relative file path |

**Response (Success):**
```json
{
  "tool": "read_file",
  "data": {
    "text": "File contents here..."
  },
  "latency_ms": 15,
  "success": true
}
```

**Response (Error - File Not Found):**
```json
{
  "detail": {
    "code": "tool_not_found",
    "message": "파일을 찾을 수 없습니다: /path/to/file.txt"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/actions/read_file \
  -H "Content-Type: application/json" \
  -d '{"params": {"path": "/app/test_samples/sample1.txt"}}'
```

---

### List Files

List files and directories.

**Endpoint:** `POST /mcp/actions/list_files`

**Request Body:**
```json
{
  "params": {
    "directory": "/path/to/directory",
    "pattern": "*.txt"
  }
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `directory` | string | Yes | Directory path |
| `pattern` | string | No | Glob pattern (default: "*") |

**Response (Success):**
```json
{
  "tool": "list_files",
  "data": {
    "text": "[{\"name\":\"file1.txt\",\"type\":\"file\",\"size\":1234}]"
  },
  "latency_ms": 10,
  "success": true
}
```

**Parsed Response:**
```json
[
  {
    "name": "file1.txt",
    "type": "file",
    "size": 1234
  },
  {
    "name": "subdir",
    "type": "directory",
    "size": 0
  }
]
```

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/actions/list_files \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "directory": "/app/test_samples",
      "pattern": "*.txt"
    }
  }'
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `connection_error` | 400 | MCP server connection failed |
| `timeout` | 408 | Request timeout |
| `tool_not_found` | 404 | Tool does not exist |
| `tool_call_failed` | 400 | Tool execution failed |
| `initialization_error` | 500 | MCP client initialization failed |

## Rate Limiting

Currently not implemented. For production:
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Examples

### Python (requests)

```python
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/mcp/health")
print(response.json())

# List tools
response = requests.get(f"{base_url}/mcp/tools")
tools = response.json()["tools"]

# Read file
response = requests.post(
    f"{base_url}/mcp/actions/read_file",
    json={"params": {"path": "/app/test_samples/sample1.txt"}}
)
content = response.json()["data"]["text"]
```

### JavaScript (fetch)

```javascript
const baseUrl = "http://localhost:8000";

// Read file
const response = await fetch(`${baseUrl}/mcp/actions/read_file`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    params: {
      path: "/app/test_samples/sample1.txt"
    }
  })
});

const data = await response.json();
console.log(data.data.text);
```

### PowerShell

```powershell
$baseUrl = "http://localhost:8000"

# Read file
$body = @{
    params = @{
        path = "/app/test_samples/sample1.txt"
    }
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/mcp/actions/read_file" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

Write-Host $response.data.text
```

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0
