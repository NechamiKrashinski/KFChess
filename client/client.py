# client/client.py
import asyncio
import websockets
import json

async def run_client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        color = None
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            if data["type"] == "assign_color":
                color = data["color"]
                print(f"אני משחק בצבע: {color}")
            elif data["type"] == "update":
                print(f"לוח מעודכן: {data['board']}")
                # תעדכן תצוגה

            # כאן דוגמה לשליחת פקודת Move
            cmd = {
                "type": "command",
                "command": {
                    "timestamp": 123456,
                    "piece_id": "Q" + color,
                    "type": "Move",
                    "params": [4, 5],
                }
            }
            await websocket.send(json.dumps(cmd))
            await asyncio.sleep(5)

asyncio.run(run_client())
