#!/usr/bin/env python3
"""
Simple WebSocket test script for notifications endpoint.

Usage:
    python scripts/test_websocket.py YOUR_JWT_TOKEN
    python scripts/test_websocket.py YOUR_JWT_TOKEN management
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Please install websockets: pip install websockets")
    sys.exit(1)


async def test_notifications_websocket(token: str, user_type: str = "user"):
    """Test the notifications WebSocket endpoint."""
    uri = f"ws://localhost:5500/api/v1/ws/notifications?token={token}&user_type={user_type}"

    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")

            # Receive welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            print(f"\n✓ Welcome message received:")
            print(json.dumps(welcome_data, indent=2))

            # Send a ping
            print("\n→ Sending ping...")
            await websocket.send("ping")

            # Receive pong
            pong_msg = await websocket.recv()
            pong_data = json.loads(pong_msg)
            print(f"✓ Pong received:")
            print(json.dumps(pong_data, indent=2))

            print("\n✓ WebSocket is working correctly!")
            print("\nListening for notifications... (Press Ctrl+C to stop)")

            # Keep connection alive and listen for messages
            async def send_periodic_ping():
                """Send ping every 30 seconds to keep connection alive."""
                while True:
                    await asyncio.sleep(30)
                    try:
                        await websocket.send("ping")
                        print("→ Ping sent (keepalive)")
                    except Exception as e:
                        print(f"✗ Error sending ping: {e}")
                        break

            # Start ping task
            ping_task = asyncio.create_task(send_periodic_ping())

            try:
                # Listen for messages
                async for message in websocket:
                    data = json.loads(message)
                    print(f"\n✓ Message received:")
                    print(json.dumps(data, indent=2))

                    if data.get("type") == "notification":
                        print(
                            f"\n🔔 NEW NOTIFICATION: {data['data'].get('title', 'No title')}"
                        )
            finally:
                ping_task.cancel()

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"\n✗ Connection failed with status {e.status_code}")
        if e.status_code == 403:
            print("  → Invalid or expired token")
        elif e.status_code == 401:
            print("  → Unauthorized - check your token")
        else:
            print(f"  → {e}")
    except websockets.exceptions.WebSocketException as e:
        print(f"\n✗ WebSocket error: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Disconnected by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_websocket.py YOUR_JWT_TOKEN [user_type]")
        print('  user_type: "user" (default) or "management"')
        sys.exit(1)

    token = sys.argv[1]
    user_type = sys.argv[2] if len(sys.argv) > 2 else "user"

    print(f"Testing WebSocket notifications endpoint")
    print(f"User type: {user_type}")
    print("-" * 60)

    asyncio.run(test_notifications_websocket(token, user_type))


if __name__ == "__main__":
    main()
