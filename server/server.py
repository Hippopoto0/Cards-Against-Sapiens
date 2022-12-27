from typing import List, Dict
from dataclasses import dataclass
import json
import os
import random
import datetime
import copy
from contextlib import suppress

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

class Player:
    def __init__(self) -> None:
        self.cards = []

class Room:
    def __init__(self, id) -> None:
        self.id: str = id
        
        self.black_cards = copy.deepcopy(black_cards)
        self.white_cards = copy.deepcopy(white_cards)

        self.players: Dict[str, Player] = {}
        self.commited_cards: Dict[str, str] = {}

        self.prompt: str = random.choice(self.black_cards)["text"].replace("_", "_____")

    def getCards(self) -> List[any]:
        temp_cards = []

        for i in range(10):
            self.white_cards.append(white_cards[0])
            temp_cards.append(white_cards.pop(0))

        return temp_cards

    def removePlayerFromRoom(self, client_id: str) -> None:
        """Removes client id from players dict and their commited cards from commited dict"""
        del self.players[client_id]

        with suppress(KeyError): del self.commited_cards[client_id]

        print(f"clients: {self.players.keys()}")

    def addPlayerToRoom(self, client_id: str) -> None:
        self.players[client_id] = Player()

    def giveHandToPlayer(self, client_id: str) -> None:
        player = self.players[client_id]
        for _ in range(10):
            self.white_cards.append(self.white_cards[0])
            player.cards.append(self.white_cards.pop(0))


    def getPlayerCards(self, client_id: str) -> List[any]:
        player = self.players[client_id]

        return player.cards

    # Returns 1 if the number of commited cards matches the length of players
    def commitCardAndReturnIfRoundOver(self, client_id: str, card_text: str) -> bool:
        self.commited_cards[client_id] = card_text
        print(f"Players present in commit cards func: {self.players.keys()}")   

        if len(self.commited_cards.keys()) == len(self.players.keys()):
            print("this is printing if commit cards is true")
            return True
        else:
            return False

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

        self.ids_to_sockets: Dict[str, WebSocket] = {}
        
        self.rooms: Dict[str, Room] = {
            "AAAAA": Room(id="AAAAA")
        }

        self.socket_to_rooms: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.ids_to_sockets[client_id] = websocket

        await websocket.send_text("receive_connection||")

    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections.remove(websocket)
        del self.ids_to_sockets[client_id]

        if client_id in self.socket_to_rooms:
            self.get_room(client_id).removePlayerFromRoom(client_id=client_id)
            del self.socket_to_rooms[client_id]

    def get_room(self, client_id: str) -> Room:
        return self.rooms[self.socket_to_rooms[client_id]]

    def join_room(self, room_id: str, client_id: str):
        if self.rooms.get(room_id) == None: return self.create_room(client_id=client_id)

        room = self.rooms["AAAAA"]
        room.addPlayerToRoom(client_id=client_id)
        room.giveHandToPlayer(client_id=client_id)

    async def create_room(self, client_id: str):
        
        room_id = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(5))

        self.rooms[room_id] = Room(id=room_id)

        self.join_room(room_id=room_id, client_id=client_id)

    async def commit_card_and_return_if_full(self, client_id: str, card_text: str, websocket: WebSocket) -> bool:
        client_room = self.socket_to_rooms[client_id]

        isFull = self.get_room(client_id=client_id).commitCardAndReturnIfRoundOver(client_id=client_id, card_text=card_text)

        if isFull:
            return True
        else:
            return False

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_room_message(self, message: str, room: Room):
        for id_of_client in room.players.keys():
            socket = self.ids_to_sockets[id_of_client]

            await socket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            header = data.split("||")[0]
            
            print(header, flush=True)
            if header == "join_room":
                manager.socket_to_rooms[client_id] = "AAAAA"
                
                client_room = manager.rooms[manager.socket_to_rooms[client_id]]
                # client_room.addPlayerToRoom(websocket=websocket)
                # client_room.giveHandToPlayer(websocket=WebSocket)
                manager.join_room("AAAAA", client_id=client_id)

                await manager.send_personal_message(f"receive_room||AAAAA", websocket)

            if header == "get_prompt":
                await manager.send_personal_message(f"receive_prompt||{manager.get_room(client_id).prompt}", websocket)
            if header == "get_answers":
                await manager.send_personal_message(f"receive_answers||{json.dumps(manager.get_room(client_id).getPlayerCards(client_id=client_id))}", websocket)
            if header == "commit_card":
                card_text = data.split("||")[1]

                areAllCardsCommited = await manager.commit_card_and_return_if_full(client_id=client_id, card_text=card_text, websocket=websocket)
                
                if areAllCardsCommited:
                    print(manager.get_room(client_id).commited_cards.items())
                    client_room = manager.get_room(client_id)
                    await manager.send_room_message(f"receive_goto_selection||{json.dumps(client_room.commited_cards)}", room=client_room)
            
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        await manager.broadcast(f"Client #{client_id} left the chat")