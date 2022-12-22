from typing import List
from dataclasses import dataclass
import json
import os
import random
import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.logger import logger
import uvicorn

app = FastAPI()

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
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

global white_cards
global black_cards

with open("server/allCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)[4]
    white_cards: List[any] = data["white"]
    random.shuffle(white_cards)
    black_cards: List[any] = data["black"]

class Room:
    def __init__(self) -> None:
        self.id = ""
        self.players = []
        self.game = GameInstance()

    def removePlayerFromRoom(self) -> None:
        pass

    def addPlayerToRoom(self) -> None:
        pass
    

class RoomManager:
    def __init__(self) -> None:
        rooms = []

class GameInstance:
    def __init__(self) -> None:
        self.prompt = random.choice(black_cards)["text"].replace("_", "_____")

    def getCards(self) -> List[any]:
        temp_cards = []
        for _ in range(10): temp_cards.append(white_cards.pop())
        return temp_cards

class ConnectionManager:
    def __init__(self, game: GameInstance):
        self.active_connections: List[WebSocket] = []
        self.game = game

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_text("receive_connection||")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


game = GameInstance()
manager = ConnectionManager(game)

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            header = data.split("||")[0]
            print(header, flush=True)
            if header == "get_prompt":
                await manager.send_personal_message(f"receive_prompt||{manager.game.prompt}", websocket)
            if header == "get_answers":
                await manager.send_personal_message(f"receive_answers||{json.dumps(manager.game.getCards())}", websocket)
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")