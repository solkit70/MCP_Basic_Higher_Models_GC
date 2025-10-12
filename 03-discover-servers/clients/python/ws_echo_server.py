import asyncio
import argparse

try:
    import websockets  # type: ignore
except Exception:
    websockets = None

async def echo(ws):
    try:
        async for msg in ws:
            await ws.send(msg)
    except Exception:
        pass

async def main(host: str, port: int):
    async with websockets.serve(echo, host, port):
        print(f"[OK] Echo server listening on ws://{host}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    if websockets is None:
        print("[ERROR] websockets not installed")
        raise SystemExit(2)
    asyncio.run(main(args.host, args.port))
