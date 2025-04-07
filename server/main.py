from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from .connection_manager import manager
from .handlers import handlers
import os
from pathlib import Path
import random

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://cards-against-sapiens.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now();
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            header, *payload = data.split("||")
            print(header, flush=True)
            handler = handlers.get(header)
            if handler:
                await handler(client_id, payload, websocket)
            else:
                print(f"Unhandled header: {header}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        from models import ClientToUserName, WaitingRooms, ClientToWaitingRoom
        if client_id in ClientToUserName:
            del ClientToUserName[client_id]
        client_room = manager.get_room(client_id=client_id)
        del client_room.players[client_id]
        if client_id in ClientToWaitingRoom:
            print("client should be removed from room", flush=True)
            waiting_room = ClientToWaitingRoom[client_id]
            WaitingRooms[waiting_room].remove(client_id)
            del ClientToWaitingRoom[client_id]
            clients_in_room = json.dumps(WaitingRooms[waiting_room])
            for tempClient in WaitingRooms[waiting_room]:
                print(f"sending updates waiting to client: {tempClient}")
                await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", manager.ids_to_sockets[tempClient])
        await manager.broadcast(f"Client #{client_id} left the chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
