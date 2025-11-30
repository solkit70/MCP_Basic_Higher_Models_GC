# WorkLog: M6 - Custom MCP Server Development

**Date**: 2025-11-30
**Milestone**: M6 - Custom MCP Server Implementation
**Duration**: ~3 hours
**Status**: ✅ Complete

## Overview

M6 milestone focused on developing a custom MCP server from scratch and integrating it with the existing FastAPI application. The server provides file system operations (read_file, list_files) to demonstrate practical MCP server development.

## Objectives

1. Understand MCP server architecture and design principles
2. Implement a custom file operations MCP server
3. Integrate the custom server with FastAPI
4. Test all functionality end-to-end

## Implementation Summary

### Phase 1: Concept Learning & Planning (30 min)

**Created Documentation:**
- [`20251130_M6_MCP_서버_구조_분석.md`](20251130_M6_MCP_서버_구조_분석.md) - Comprehensive server architecture guide
- [`20251130_MCP_데코레이터_상세_가이드.md`](20251130_MCP_데코레이터_상세_가이드.md) - @mcp.tool() decorator deep dive
- [`20251130_JSON-RPC_개념_가이드.md`](20251130_JSON-RPC_개념_가이드.md) - JSON-RPC 2.0 protocol explanation
- [`20251130_stdio_transport_타입힌트_가이드.md`](20251130_stdio_transport_타입힌트_가이드.md) - stdio transport and type hints

**Key Learnings:**
- MCP server structure: Server instance → Tools (via decorators) → Transport (stdio/ws)
- @mcp.tool() decorator automatically generates JSON Schema from Python type hints
- JSON-RPC 2.0 provides the communication protocol layer
- stdio transport uses stdin/stdout for IPC
- Type hints are critical for automatic schema generation

### Phase 2: Server Implementation (60 min)

**Files Created:**

1. **[`05-build-server/file_server.py`](../05-build-server/file_server.py)** (121 lines)
   - Implemented using `mcp.server.fastmcp.FastMCP` from the official MCP SDK
   - Two tools:
     - `read_file(path: str) -> str` - Reads file contents with error handling
     - `list_files(directory: str, pattern: str = "*") -> str` - Lists directory contents with glob filtering
   - Returns JSON-formatted responses
   - Proper error handling for FileNotFoundError, IsADirectoryError, PermissionError

2. **Test Samples** (`05-build-server/test_samples/`)
   - `sample1.txt` - Multi-language UTF-8 test file (218 bytes)
   - `sample2.txt` - Test data file (202 bytes)
   - `config.json` - JSON configuration (130 bytes)

3. **[`05-build-server/test_direct.py`](../05-build-server/test_direct.py)**
   - Independent test client using official MCP SDK
   - Tests: initialize, list_tools, read_file, list_files
   - **Result**: ✅ All 4 tests passed

**Key Decisions:**
- Used `mcp.server.fastmcp.FastMCP` instead of standalone `fastmcp` package for compatibility
- Removed `version` parameter (not supported in SDK's FastMCP)
- Used `json.dumps()` for list_files response to match MCP text content format

### Phase 3: FastAPI Integration (40 min)

**Files Modified:**

1. **[`04-app-integration/simple-webapp/.env`](../04-app-integration/simple-webapp/.env)** (Line 9)
   ```ini
   # Changed from echo.py to file_server.py
   MCP_EXEC_PATH=C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\.venv\Scripts\python.exe C:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC\05-build-server\file_server.py
   ```

2. **[`04-app-integration/simple-webapp/app/services/mcp_client.py`](../04-app-integration/simple-webapp/app/services/mcp_client.py)** (Line 170)
   - Added `encoding='utf-8'` to subprocess.Popen()
   - **Critical fix**: Windows defaults to 'charmap' encoding which caused UnicodeDecodeError with MCP JSON-RPC messages

**Test Scripts Created:**
- [`scripts/test_file_server_http.ps1`](../04-app-integration/simple-webapp/scripts/test_file_server_http.ps1) - PowerShell HTTP integration tests
- [`test_api.py`](../04-app-integration/simple-webapp/test_api.py) - Python test script for debugging

**Integration Test Results:**
- ✅ GET `/mcp/health` - Returns `{"status": "ok", "server_type": "stdio"}`
- ✅ GET `/mcp/tools` - Returns 2 tools with descriptions
- ✅ POST `/mcp/actions/read_file` - Reads 218 bytes from sample1.txt
- ✅ POST `/mcp/actions/list_files` - Lists directory contents

### Phase 4: Documentation & Commit (20 min)

**Files Renamed** (for consistency):
- `MCP_실전_개발_가이드.md` → [`20251123_MCP_실전_개발_가이드.md`](20251123_MCP_실전_개발_가이드.md)
- `MCP_데코레이터_상세_가이드.md` → [`20251130_MCP_데코레이터_상세_가이드.md`](20251130_MCP_데코레이터_상세_가이드.md)
- `M6_MCP_서버_구조_분석.md` → [`20251130_M6_MCP_서버_구조_분석.md`](20251130_M6_MCP_서버_구조_분석.md)

**Documentation Created:**
- This WorkLog (WorkLog_M6_CustomServer.md)

## Issues Encountered & Solutions

### Issue 1: Package Import Confusion
**Problem**: Used standalone `fastmcp` package initially, which had different API and behavior
**Solution**: Switched to `mcp.server.fastmcp.FastMCP` from official MCP SDK
**Impact**: Server now compatible with stdio adapter that worked with echo.py

### Issue 2: Server Closes Immediately on Startup
**Problem**: FastAPI's _StdioAdapter received EOF when reading initialize response
**Symptoms**: `McpClientError: EOF: Server closed connection`
**Root Cause**: Different FastMCP implementations have different startup behaviors
**Solution**: Used SDK's FastMCP which has consistent stdio protocol implementation

### Issue 3: Unicode Encoding Error
**Problem**: `'charmap' codec can't decode byte 0x9d in position 88`
**Root Cause**: Windows subprocess.Popen defaults to 'charmap' encoding, but MCP uses UTF-8
**Solution**: Added `encoding='utf-8'` parameter to Popen call in [mcp_client.py:170](../04-app-integration/simple-webapp/app/services/mcp_client.py#L170)
**Impact**: ✅ Fixed all 400 errors, server now communicates properly

### Issue 4: FastMCP Version Parameter
**Problem**: `TypeError: FastMCP.__init__() got an unexpected keyword argument 'version'`
**Root Cause**: SDK's FastMCP doesn't accept version parameter (unlike standalone package)
**Solution**: Removed `version="1.0.0"` parameter
**Impact**: Server initializes correctly, version comes from SDK (v1.22.0)

## Key Takeaways

### Technical Insights
1. **UTF-8 Encoding is Critical**: Always specify `encoding='utf-8'` for subprocess communication on Windows
2. **Package Compatibility**: Use `mcp.server.fastmcp.FastMCP` from official SDK for consistency with official examples
3. **stdio Protocol**: Subprocess stdin/stdout must be line-buffered text streams
4. **Type Hints**: Python type annotations enable automatic JSON Schema generation
5. **Error Handling**: MCP tools should handle and report errors gracefully

### Best Practices Established
- ✅ Never use `print()` in stdio mode servers (pollutes stdout)
- ✅ Always test servers independently before integration
- ✅ Use UTF-8 encoding explicitly for cross-platform compatibility
- ✅ Provide clear docstrings for auto-generated tool descriptions
- ✅ Return structured JSON for complex data (like file lists)

### Architecture Understanding
```
FastAPI App
    ↓ HTTP Request
[Router] → [McpClient]
                ↓ creates
          [_StdioAdapter]
                ↓ spawns subprocess
          [file_server.py]
                ↓ FastMCP Server
          [read_file, list_files tools]
                ↓ JSON-RPC over stdio
          [Response] → [HTTP Response]
```

## Files Changed

### Created
- `05-build-server/file_server.py`
- `05-build-server/test_direct.py`
- `05-build-server/test_samples/sample1.txt`
- `05-build-server/test_samples/sample2.txt`
- `05-build-server/test_samples/config.json`
- `04-app-integration/simple-webapp/scripts/test_file_server_http.ps1`
- `04-app-integration/simple-webapp/test_api.py`
- `docs/20251130_M6_MCP_서버_구조_분석.md`
- `docs/20251130_MCP_데코레이터_상세_가이드.md`
- `docs/20251130_JSON-RPC_개념_가이드.md`
- `docs/20251130_stdio_transport_타입힌트_가이드.md`
- `docs/WorkLog_M6_CustomServer.md` (this file)

### Modified
- `04-app-integration/simple-webapp/.env` (Line 9: Updated MCP_EXEC_PATH)
- `04-app-integration/simple-webapp/app/services/mcp_client.py` (Line 170: Added encoding='utf-8')

### Renamed
- `docs/MCP_실전_개발_가이드.md` → `docs/20251123_MCP_실전_개발_가이드.md`
- `docs/MCP_데코레이터_상세_가이드.md` → `docs/20251130_MCP_데코레이터_상세_가이드.md`
- `docs/M6_MCP_서버_구조_분석.md` → `docs/20251130_M6_MCP_서버_구조_분석.md`

## Test Results

### Direct Server Test (test_direct.py)
```
✅ [1] Initialize - Server: File Operations Server v1.22.0
✅ [2] List tools - Found 2 tools: read_file, list_files
✅ [3] read_file test - Read 218 bytes from sample1.txt
✅ [4] list_files test - Found 3 files/folders
```

### HTTP Integration Test (via FastAPI)
```
✅ Test 1: Health Check - Status: ok, Server Type: stdio
✅ Test 2: List Tools - Found 2 tools with descriptions
✅ Test 3: Read File - File read successful, Latency: 8-14ms
✅ Test 4: List Files - Files listed successfully, Latency: 7-13ms
✅ Test 5: List Files (pattern filter) - Pattern filtering works
✅ Test 6: Error handling - Server gracefully handles errors
```

## Next Steps (M7)

Potential future enhancements:
1. Add write operations (write_file, delete_file)
2. Implement resource endpoints (file:///path/to/file)
3. Add prompts for common file operations
4. Implement WebSocket transport option
5. Add authentication/authorization
6. Create monitoring and logging

## Conclusion

M6 successfully demonstrated:
- ✅ Custom MCP server development from scratch
- ✅ Tool implementation with proper type hints and error handling
- ✅ stdio transport communication
- ✅ FastAPI integration
- ✅ End-to-end testing

**Key Achievement**: Built a production-ready file operations MCP server integrated with FastAPI, handling Unicode properly across Windows subprocess boundaries.

**Time Spent**: ~3 hours (matched estimate)
**Lines of Code**: ~400 lines (server + tests + docs)
**Tests**: 10 tests, 100% passing
**Documentation**: 5 comprehensive guides created

---

**Completed**: 2025-11-30
**Next Milestone**: TBD (potential M7: Advanced Features or Real-world Use Case)
