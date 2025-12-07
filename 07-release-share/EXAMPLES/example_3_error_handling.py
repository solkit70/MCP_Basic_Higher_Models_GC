"""
Example 3: Error Handling and Retry Logic

This example demonstrates proper error handling, retry logic, and timeout management.
"""

import requests
import time
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
REQUEST_TIMEOUT = 10  # seconds

class MCPClient:
    """Simple MCP API client with error handling."""

    def __init__(self, base_url: str, timeout: int = REQUEST_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout

    def call_tool_with_retry(
        self,
        tool_name: str,
        params: Dict[str, Any],
        max_retries: int = MAX_RETRIES
    ) -> Optional[Dict[str, Any]]:
        """
        Call MCP tool with automatic retry on failure.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters
            max_retries: Maximum number of retry attempts

        Returns:
            Tool response or None on failure
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                print(f"    Attempt {attempt}/{max_retries}...")

                response = requests.post(
                    f"{self.base_url}/mcp/actions/{tool_name}",
                    json={"params": params},
                    timeout=self.timeout
                )

                # Check for HTTP errors
                response.raise_for_status()

                result = response.json()

                # Check for MCP-level success
                if result.get('success', True):
                    print(f"    SUCCESS (latency: {result.get('latency_ms', 0)} ms)")
                    return result
                else:
                    print(f"    FAILED: {result.get('error', 'Unknown error')}")
                    last_error = result.get('error', 'Unknown error')

            except requests.Timeout:
                print(f"    TIMEOUT after {self.timeout}s")
                last_error = "Request timeout"

            except requests.ConnectionError:
                print(f"    CONNECTION ERROR")
                last_error = "Connection failed"

            except requests.HTTPError as e:
                print(f"    HTTP ERROR: {e.response.status_code}")
                try:
                    error_detail = e.response.json()
                    print(f"    Detail: {error_detail}")
                    last_error = error_detail
                except:
                    last_error = str(e)

            except Exception as e:
                print(f"    UNEXPECTED ERROR: {e}")
                last_error = str(e)

            # Wait before retry (except on last attempt)
            if attempt < max_retries:
                print(f"    Waiting {RETRY_DELAY}s before retry...")
                time.sleep(RETRY_DELAY)

        print(f"    FAILED after {max_retries} attempts")
        print(f"    Last error: {last_error}")
        return None

def main():
    print("=" * 60)
    print("Example 3: Error Handling and Retry Logic")
    print("=" * 60)
    print()

    client = MCPClient(BASE_URL)

    # Test 1: Successful call
    print("[Test 1] Successful file read")
    result = client.call_tool_with_retry(
        "read_file",
        {"path": "/app/test_samples/sample1.txt"}
    )
    if result:
        content_length = len(result['data']['text'])
        print(f"    Result: Read {content_length} bytes")
    print()

    # Test 2: File not found error
    print("[Test 2] File not found error")
    result = client.call_tool_with_retry(
        "read_file",
        {"path": "/app/test_samples/nonexistent.txt"},
        max_retries=1  # No need to retry for non-existent files
    )
    if result is None:
        print("    Expected: File not found handled correctly")
    print()

    # Test 3: Invalid tool name
    print("[Test 3] Invalid tool name")
    result = client.call_tool_with_retry(
        "invalid_tool",
        {"param": "value"},
        max_retries=1
    )
    if result is None:
        print("    Expected: Invalid tool handled correctly")
    print()

    # Test 4: Directory instead of file
    print("[Test 4] Directory instead of file")
    result = client.call_tool_with_retry(
        "read_file",
        {"path": "/app/test_samples"},
        max_retries=1
    )
    if result is None:
        print("    Expected: Directory error handled correctly")
    print()

    # Test 5: List files with invalid directory
    print("[Test 5] List files with invalid directory")
    result = client.call_tool_with_retry(
        "list_files",
        {
            "directory": "/nonexistent/directory",
            "pattern": "*"
        },
        max_retries=1
    )
    if result is None:
        print("    Expected: Invalid directory handled correctly")
    print()

    # Test 6: Timeout simulation (if server is slow)
    print("[Test 6] Short timeout test")
    short_timeout_client = MCPClient(BASE_URL, timeout=0.001)  # Very short timeout
    result = short_timeout_client.call_tool_with_retry(
        "read_file",
        {"path": "/app/test_samples/sample1.txt"},
        max_retries=2
    )
    if result is None:
        print("    Expected: Timeout handled correctly")
    print()

    print("=" * 60)
    print("Error Handling Examples Completed!")
    print("=" * 60)
    print()
    print("Key Takeaways:")
    print("  1. Always use try-except for API calls")
    print("  2. Implement retry logic for transient failures")
    print("  3. Set appropriate timeouts")
    print("  4. Handle specific error types differently")
    print("  5. Log errors with context for debugging")

if __name__ == "__main__":
    main()
