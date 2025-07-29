# server/server.py
import asyncio
import websockets
import json
from implementation.game_builder import GameBuilder
import pathlib

clients = {}  # {websocket: 'W' or 'B'}

async def register_player(websocket):
    if 'W' not in clients.values():
        clients[websocket] = 'W'
        return 'W'
    elif 'B' not in clients.values():
        clients[websocket] = 'B'
        return 'B'
    else:
        await websocket.send(json.dumps({"error": "Server full"}))
        await websocket.close()
        return None

async def broadcast_to_all(msg_dict):
    for ws in clients.keys():
        await ws.send(json.dumps(msg_dict))

async def handle_client(websocket):
    color = await register_player(websocket)
    if not color:
        return

    await websocket.send(json.dumps({"type": "assign_color", "color": color}))

    # נבנה משחק אחד לכולם (פעם אחת בלבד)
    if len(clients) == 1:
        ROOT = pathlib.Path(__file__).parent.parent / "assets"
        builder = GameBuilder(ROOT, 8, 8, 85, 85, "board.png", "background.png", 800, 800)
        global game
        game = builder.build_game("board.csv")

    async for msg in websocket:
        data = json.loads(msg)

        if data["type"] == "command":
            cmd_dict = data["command"]
            from implementation.command import Command

            cmd = Command(**cmd_dict)
            game._process_input(cmd, game.game_time_ms())  # מפעיל פקודה

            # שליחת לוח מעודכן לכולם
            board_state = {}  # תכניס כאן את מבנה הלוח המתאים
            await broadcast_to_all({
                "type": "update",
                "board": board_state,
                "last_command": cmd_dict,
            })

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server is running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
