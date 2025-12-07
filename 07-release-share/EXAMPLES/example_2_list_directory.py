"""
Example 2: List Directory Contents

This example demonstrates using the list_files tool with pattern filtering.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def list_files(directory: str, pattern: str = "*"):
    """List files in a directory with optional pattern filter."""
    response = requests.post(
        f"{BASE_URL}/mcp/actions/list_files",
        json={
            "params": {
                "directory": directory,
                "pattern": pattern
            }
        }
    )
    response.raise_for_status()
    result = response.json()

    # Parse JSON string in result
    files = json.loads(result['data']['text'])
    latency = result['latency_ms']

    return files, latency

def format_size(size_bytes):
    """Format byte size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    print("=" * 60)
    print("Example 2: List Directory Contents")
    print("=" * 60)
    print()

    directory = "/app/test_samples"

    # Example 1: List all files
    print(f"[1] Listing all files in {directory}")
    try:
        files, latency = list_files(directory, "*")
        print(f"    Found {len(files)} items (latency: {latency} ms)")
        print()

        for file in files:
            size_str = format_size(file['size'])
            type_icon = "📁" if file['type'] == 'directory' else "📄"
            print(f"    {type_icon} {file['name']:<20} {size_str:>10}")

        print()
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # Example 2: List only text files
    print(f"[2] Listing only .txt files in {directory}")
    try:
        files, latency = list_files(directory, "*.txt")
        print(f"    Found {len(files)} .txt files (latency: {latency} ms)")
        print()

        for file in files:
            size_str = format_size(file['size'])
            print(f"    📄 {file['name']:<20} {size_str:>10}")

        print()
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # Example 3: List JSON files
    print(f"[3] Listing only .json files in {directory}")
    try:
        files, latency = list_files(directory, "*.json")
        print(f"    Found {len(files)} .json files (latency: {latency} ms)")
        print()

        if files:
            for file in files:
                size_str = format_size(file['size'])
                print(f"    📄 {file['name']:<20} {size_str:>10}")
        else:
            print("    No JSON files found")

        print()
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # Example 4: Calculate total size
    print("[4] Calculating total directory size")
    try:
        files, _ = list_files(directory, "*")
        total_size = sum(f['size'] for f in files if f['type'] == 'file')
        file_count = sum(1 for f in files if f['type'] == 'file')
        dir_count = sum(1 for f in files if f['type'] == 'directory')

        print(f"    Total files: {file_count}")
        print(f"    Total directories: {dir_count}")
        print(f"    Total size: {format_size(total_size)}")
        print()
    except Exception as e:
        print(f"    ERROR: {e}")

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
