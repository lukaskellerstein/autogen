import asyncio
import json
import websockets
from typing import Dict, Any
import threading

connected_users: Dict[str, websockets.WebSocketServerProtocol] = {}

async def send_message(message: Any):
    """
    Send a message to the specified receivers.
    """
    sender = message.get("sender")
    receivers = message.get("receivers")
    messageJson = json.dumps(message)

    tasks = []
    if "all" in receivers:  # broadcast to all users
        tasks = [asyncio.create_task(user.send(messageJson)) for username, user in connected_users.items() if username != sender]
    else:
        for receiver in receivers:
            if receiver in connected_users:
                tasks.append(asyncio.create_task(connected_users[receiver].send(messageJson)))
    
    # If there are any tasks, then run them
    if tasks:
        await asyncio.wait(tasks)

async def register_user(username: str, websocket: websockets.WebSocketServerProtocol):
    if username in connected_users:
        await websocket.send(json.dumps({"error": f"Username {username} is already taken."}))
        return False  # Indicate that registration failed
    else:
        connected_users[username] = websocket
        print(f"{username} has joined the chat.")
        # message = json.dumps({"send_message": f"{username} has joined the chat."})
        # await send_message(username, ["all"], message)
        return True  # Indicate successful registration

async def unregister_user(username: str):
    """
    Unregister a user and notify others about the disconnection.
    """
    if username in connected_users:
        del connected_users[username]
        print(f"{username} has left the chat.")
        # message = json.dumps({"send_message": f"{username} has left the chat."})
        # await send_message(username, ["all"], message)

async def chat_handler(websocket: websockets.WebSocketServerProtocol, path):
    """
    Handle incoming messages and user actions.
    """
    try:
        async for message in websocket:
            # print(f"[Server] Message from {username}: {message}")
            try:
                data = json.loads(message)
                action = data.get("action")
                payload = data.get("payload")

                if action == "register":
                    username = payload
                    await register_user(username, websocket)
                elif action == "send_message":
                    await send_message(payload)
                else:
                    await websocket.send(json.dumps({"error": "Unknown action"}))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON format"}))
            except KeyError:
                await websocket.send(json.dumps({"error": "Invalid message format"}))
    except websockets.ConnectionClosed:
        print(f"Connection closed")
    finally:
        if username:
            await unregister_user(username)

async def message_broker():
    print("[message_broker] thread name: ", threading.current_thread())
    print("[message_broker] event loop: ", asyncio.get_event_loop())

    async with websockets.serve(chat_handler, "localhost", 8000):
        print("ws server started 2")
        await asyncio.Future()  # run forever
