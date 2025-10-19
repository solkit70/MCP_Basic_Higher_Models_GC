import argparse
import asyncio
import json
import os
import sys
from urllib.parse import urlparse

try:
    import websockets  # type: ignore
except Exception:  # pragma: no cover
    websockets = None


async def ws_probe(uri: str, headers_json: str | None, message: str | None, timeout: float):
    if websockets is None:
        print("[WARN] websockets not installed; dry-run only")
        return
    headers = {}
    if headers_json:
        try:
            headers = json.loads(headers_json)
        except Exception as e:
            print(f"[WARN] invalid headers JSON: {e}")
    try:
        async with websockets.connect(uri, extra_headers=headers) as ws:
            print("[OK] Connected to", uri)
            if message is not None:
                try:
                    await asyncio.wait_for(ws.send(message), timeout=timeout)
                    print("[SEND]", message)
                    echoed = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    print("[RECV]", echoed)
                    if echoed == message:
                        print("[OK] Echo matched")
                    else:
                        print("[WARN] Echo mismatch")
                except asyncio.TimeoutError:
                    print("[ERROR] Timeout during send/recv (", timeout, "s)")
            await ws.close()
    except Exception as e:
        print("[ERROR] WS connect failed:", e)


def main():
    parser = argparse.ArgumentParser(description="MCP ws client (connectivity/echo probe)")
    parser.add_argument("uri", help="WebSocket URI, e.g., ws://localhost:9000")
    parser.add_argument("--headers", help="JSON object for headers", default=None)
    parser.add_argument("--message", help="Message to echo and verify", default=None)
    parser.add_argument("--timeout", help="Send/recv timeout seconds", type=float, default=3.0)
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()

    u = urlparse(args.uri)
    if u.scheme not in ("ws", "wss"):
        print("[ERROR] Invalid scheme (expect ws/wss):", u.scheme)
        sys.exit(2)

    if args.dry or websockets is None:
        print("[DRY] Would connect to:", args.uri)
        if args.headers:
            print("[DRY] Headers:", args.headers)
        if args.message:
            print("[DRY] Would send message:", args.message)
        sys.exit(0)

    asyncio.run(ws_probe(args.uri, args.headers, args.message, args.timeout))


if __name__ == "__main__":
    main()
