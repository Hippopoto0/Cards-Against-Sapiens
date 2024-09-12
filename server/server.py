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
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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

import pathlib

parentAbsolutePath = pathlib.Path(__file__).parent.resolve().as_posix()
with open(parentAbsolutePath + "/allCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    white_cards = []
    black_cards = []
    for pack in data:

        # print(pack["white"])
        # white_cards.append(pack["white"])
        [white_cards.append(card) for card in pack["white"]]
        [black_cards.append(card) for card in pack["black"]]
    # print(data)
    # white_cards: List[any] = data["white"]
    random.shuffle(white_cards)
    random.shuffle(black_cards)
    # black_cards: List[any] = data["black"]

    # print(data[0])
    # white_cards = []
    # black_cards = []

    # for pack in data:
    #     white_cards.append(pack["white"])
    #     black_cards.append(pack["black"])

    # random.shuffle(white_cards)
    # random.shuffle(black_cards)


class Player:
    def __init__(self) -> None:
        self.cards = []

WaitingRooms: Dict[str, List[str]] = {

}

ClientToWaitingRoom: Dict[str, str] = {}

ClientToUserName: Dict[str, str] = {}

class Room:
    def __init__(self, id) -> None:
        self.id: str = id
        
        
        self.black_cards = copy.deepcopy(black_cards)
        self.white_cards = copy.deepcopy(white_cards)

        random.shuffle(self.black_cards)
        random.shuffle(self.white_cards)

        self.players: Dict[str, Player] = {}
        self.commited_cards: Dict[str, str] = {}

        self.preferenceCount: Dict[str, int] = {}
        self.preferencesCommited: int = 0

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

    def getExtraCard(self, client_id: str):
        player = self.players[client_id]
        self.white_cards.append(self.white_cards[0])

        card = self.white_cards.pop(0)

        player.cards.append(card)

        return card

    def gotoNextPromptAndReturnPrompt(self):
        self.black_cards.append(self.black_cards[0])

        self.prompt = self.black_cards.pop(0)
        self.prompt = self.prompt["text"].replace("_", "_____")

        return self.prompt

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

    def addUserCardPreference(self, client_id: str, card_client_id: str):
        if card_client_id in self.preferenceCount:
            self.preferenceCount[card_client_id] += 1
        else:
            self.preferenceCount[card_client_id] = 1

        self.preferencesCommited += 1

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
        if self.rooms.get(room_id) == None: return self.create_room(client_id=client_id, room_id=room_id)
        print(f"lets see if this room exists: {str(self.rooms.get(room_id))}")

        room = self.rooms[room_id]
        room.addPlayerToRoom(client_id=client_id)
        room.giveHandToPlayer(client_id=client_id)

    def create_room(self, client_id: str, room_id: str):
        
        # room_id = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(5))
        print("is this room beng created?", flush=True)
        self.rooms[room_id] = Room(id=room_id)

        self.join_room(room_id=room_id, client_id=client_id)

    async def commit_card_and_return_if_full(self, client_id: str, card_text: str, websocket: WebSocket) -> bool:
        client_room = self.socket_to_rooms[client_id]

        isFull = self.get_room(client_id=client_id).commitCardAndReturnIfRoundOver(client_id=client_id, card_text=card_text)

        if isFull:
            return True
        else:
            return False

    def add_to_card_scores_and_return_if_all_commited(self, client_id: str, id_for_card: str) -> bool:
        client_room = self.get_room(client_id=client_id)

        client_room.addUserCardPreference(client_id=client_id, card_client_id=id_for_card)
        if client_room.preferencesCommited >= len(client_room.players):
            return True
        else:
            return False

    def get_winner_data_and_reset_round(self, room: Room):
        # maxClient = max(room.preferenceCount, key=room.preferenceCount.get)
        maxClientID = max(room.preferenceCount, key=room.preferenceCount.get)

        if maxClientID in ClientToUserName:
            maxClientUsername = ClientToUserName[maxClientID]
            maxClientCard = room.commited_cards[maxClientID]
        else:
            maxClientUsername = "Winner Left Room"
            maxClientCard = "Winner Left Room"


        # reset stuff
        room.preferenceCount = {}
        room.preferencesCommited = 0
        room.commited_cards = {}

        print(room.preferenceCount.keys(), flush=True)

        return { "client_id": maxClientID, "client_username": maxClientUsername, "client_card_text": maxClientCard }

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
                roomID = data.split("||")[1]
                print(f"roomID: {roomID}")
                manager.socket_to_rooms[client_id] = roomID
                # manager.rooms[roomID] = Room(id=roomID)
                
                # client_room = manager.rooms[manager.socket_to_rooms[client_id]]
                # client_room.addPlayerToRoom(websocket=websocket)
                # client_room.giveHandToPlayer(websocket=WebSocket)
                manager.join_room(room_id=roomID, client_id=client_id)

                print(f"Rooms after join: {manager.rooms}", flush=True)

                await manager.send_personal_message(f"receive_room||AAAAA", websocket)

            if header == "does_room_exist":
                roomID = data.split("||")[1]

                print(f"checking if room works: {roomID}")
                print(f"rooms: {manager.rooms}")

                if roomID in WaitingRooms:
                    await manager.send_personal_message(f"receive_does_waiting_room_exist||true", websocket=websocket)
                else:
                    await manager.send_personal_message(f"receive_does_waiting_room_exist||false", websocket=websocket)

                if roomID in manager.rooms:

                    await manager.send_personal_message(f"receive_does_game_room_exist||true", websocket=websocket)

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
            if header == "add_score_to_card":
                client_id_of_card = data.split("||")[1]

                are_all_preferences_done = manager.add_to_card_scores_and_return_if_all_commited(client_id=client_id, id_for_card=client_id_of_card)
                print(f"are all done?: {str(are_all_preferences_done)}")

                if are_all_preferences_done:
                    client_room = manager.get_room(client_id=client_id)
                    winner_data = manager.get_winner_data_and_reset_round(room=client_room)

                    print(f"winner data: {json.dumps(winner_data)}")

                    await manager.send_room_message(f"receive_winner||{json.dumps(winner_data)}", room=client_room)
                    prompt = client_room.gotoNextPromptAndReturnPrompt()

                    await manager.send_room_message(f"receive_prompt||{prompt}", room=client_room)

            if header == "request_extra_card":
                latestCard = manager.get_room(client_id=client_id).getExtraCard(client_id=client_id)

                await manager.send_personal_message(f"receive_extra_card||{json.dumps(latestCard)}", websocket=websocket)

            if header == "submit_username":
                username = data.split("||")[1]

                ClientToUserName[client_id] = username

            if header == "add_to_waiting_room":
                id_and_username = data.split("||")[1]

                id_and_username = json.loads(id_and_username)

                roomID = id_and_username["roomID"]
                username = id_and_username["username"]
                
                ClientToUserName[client_id] = username

                if roomID in WaitingRooms:
                    if client_id not in WaitingRooms[roomID]:
                        WaitingRooms[roomID].append(client_id)
                else:
                    WaitingRooms[roomID] = [client_id]

                ClientToWaitingRoom[client_id] = roomID

                clients_in_room = []
                for client in WaitingRooms[roomID]:
                    clients_in_room.append(ClientToUserName[client])

                clients_in_room = json.dumps(clients_in_room)

                print(WaitingRooms[roomID])

                for tempClient in WaitingRooms[roomID]:
                    await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", websocket=manager.ids_to_sockets[tempClient])

            if header == "start_game_from_wait":
                waiting_room = ClientToWaitingRoom[client_id]

                clients_in_waiting_room = WaitingRooms[waiting_room]

                
                for tempClient in clients_in_waiting_room:
                    print(f"client {tempClient} should now go to their game")

                    await manager.send_personal_message(f"receive_goto_game||", websocket=manager.ids_to_sockets[tempClient])
                    await manager.send_personal_message(f"receive_connection||", websocket=manager.ids_to_sockets[tempClient])

                    # delete room contents, its just waste now
                    del ClientToWaitingRoom[tempClient]

                # remove room from waiting room list
                del WaitingRooms[waiting_room]
                
                
            
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)

        if client_id in ClientToUserName: del ClientToUserName[client_id]
        client_room = manager.get_room(client_id=client_id)

        del client_room.players[client_id]

        if client_id in ClientToWaitingRoom:
            print("client should be removed from room", flush=True)
            waiting_room = ClientToWaitingRoom[client_id]

            WaitingRooms[waiting_room].remove(client_id)

            del ClientToWaitingRoom[client_id]
            
            ClientToWaitingRoom[client_id] = roomID

            clients_in_room = json.dumps(WaitingRooms[roomID])

            for tempClient in WaitingRooms[waiting_room]:
                print(f"sending updates waiting to client: {tempClient}")
                await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", websocket=manager.ids_to_sockets[tempClient])

        await manager.broadcast(f"Client #{client_id} left the chat")