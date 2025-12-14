"""Quick test to check API responses"""
import requests
import json

base_url = "http://localhost:8000"

# Test 1: Health
print("=== Test 1: Health ===")
response = requests.get(f"{base_url}/mcp/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# Test 2: List Tools
print("\n=== Test 2: List Tools ===")
try:
    response = requests.get(f"{base_url}/mcp/tools")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Tools: {len(data.get('tools', []))}")
        for tool in data.get('tools', []):
            print(f"  - {tool['name']}: {tool.get('description', 'N/A')}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Call read_file tool
print("\n=== Test 3: Call read_file Tool ===")
try:
    response = requests.post(
        f"{base_url}/mcp/actions/read_file",
        json={"params": {"path": "C:\\AI_study\\Projects\\MCP\\MCP_Basic_Higher_Models_GC\\05-build-server\\test_samples\\sample1.txt"}}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        print(f"Data keys: {list(data.get('data', {}).keys())}")
        text_data = data.get('data', {}).get('text', '')
        print(f"Text length: {len(text_data)}")
        print(f"First 100 chars: {text_data[:100]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
