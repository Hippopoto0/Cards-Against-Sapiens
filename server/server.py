# ----------------- SERVER ENTRY POINT NOW IN MAIN.PY --------------------
# from typing import List, Dict, Any
# from dataclasses import dataclass
# import json
# import os
# import random
# import datetime
# import copy
# from contextlib import suppress
# from pathlib import Path

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
# from fastapi.logger import logger
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# from .models import Room, Player, ClientToUserName, ClientToWaitingRoom

# app = FastAPI()

# origins = [
#     "http://localhost:5173",
#     "https://cards-against-sapiens.onrender.com"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <h2>Your ID: <span id="ws-id"></span></h2>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off"/>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#             var client_id = Date.now();
#             document.querySelector("#ws-id").textContent = client_id;
#             var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages');
#                 var message = document.createElement('li');
#                 var content = document.createTextNode(event.data);
#                 message.appendChild(content);
#                 messages.appendChild(message);
#             };
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText");
#                 ws.send(input.value);
#                 input.value = '';
#                 event.preventDefault();
#             }
#         </script>
#     </body>
# </html>
# """

# with open(Path(os.path.abspath(".")) / "server" / "allCards.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     white_cards: List[Any] = [card for pack in data for card in pack["white"]]
#     black_cards: List[Any] = [card for pack in data for card in pack["black"]]
#     random.shuffle(white_cards)
#     random.shuffle(black_cards)


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []
#         self.ids_to_sockets: Dict[str, WebSocket] = {}
#         self.rooms: Dict[str, Room] = {"AAAAA": Room(id="AAAAA")}
#         self.socket_to_rooms: Dict[str, str] = {}

#     async def connect(self, websocket: WebSocket, client_id: str):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         self.ids_to_sockets[client_id] = websocket
#         await websocket.send_text("receive_connection||")

#     def disconnect(self, websocket: WebSocket, client_id: str):
#         self.active_connections.remove(websocket)
#         del self.ids_to_sockets[client_id]
#         if client_id in self.socket_to_rooms:
#             self.get_room(client_id).removePlayerFromRoom(client_id=client_id)
#             del self.socket_to_rooms[client_id]

#     def get_room(self, client_id: str) -> Room:
#         return self.rooms[self.socket_to_rooms[client_id]]

#     def join_room(self, room_id: str, client_id: str):
#         if self.rooms.get(room_id) == None:
#             return self.create_room(client_id=client_id, room_id=room_id)
#         print(f"lets see if this room exists: {str(self.rooms.get(room_id))}")
#         room = self.rooms[room_id]
#         room.addPlayerToRoom(client_id=client_id)
#         room.giveHandToPlayer(client_id=client_id)

#     def create_room(self, client_id: str, room_id: str):
#         print("is this room beng created?", flush=True)
#         self.rooms[room_id] = Room(id=room_id)
#         self.join_room(room_id=room_id, client_id=client_id)

#     async def commit_card_and_return_if_full(self, client_id: str, card_text: str, websocket: WebSocket) -> bool:
#         isFull = self.get_room(client_id=client_id).commitCardAndReturnIfRoundOver(client_id=client_id, card_text=card_text)
#         if isFull:
#             return True
#         else:
#             return False

#     def add_to_card_scores_and_return_if_all_commited(self, client_id: str, id_for_card: str) -> bool:
#         client_room = self.get_room(client_id=client_id)
#         client_room.addUserCardPreference(client_id=client_id, card_client_id=id_for_card)
#         if client_room.preferencesCommited >= len(client_room.players):
#             return True
#         else:
#             return False

#     def get_winner_data_and_reset_round(self, room: Room):
#         maxClientID = max(room.preferenceCount, key=room.preferenceCount.get)
#         if maxClientID in ClientToUserName:
#             maxClientUsername = ClientToUserName[maxClientID]
#             maxClientCard = room.commited_cards[maxClientID]
#         else:
#             maxClientUsername = "Winner Left Room"
#             maxClientCard = "Winner Left Room"
#         room.preferenceCount = {}
#         room.preferencesCommited = 0
#         room.commited_cards = {}
#         print(room.preferenceCount.keys(), flush=True)
#         return { "client_id": maxClientID, "client_username": maxClientUsername, "client_card_text": maxClientCard }

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def send_room_message(self, message: str, room: Room):
#         for id_of_client in room.players.keys():
#             socket = self.ids_to_sockets[id_of_client]
#             await socket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()

# @app.get("/")
# async def get():
#     return HTMLResponse(html)

# async def handle_join_room(client_id: str, payload: List[str], websocket: WebSocket):
#     roomID = payload[0]
#     print(f"roomID: {roomID}")
#     manager.socket_to_rooms[client_id] = roomID
#     manager.join_room(room_id=roomID, client_id=client_id)
#     print(f"Rooms after join: {manager.rooms}", flush=True)
#     await manager.send_personal_message(f"receive_room||AAAAA", websocket)

# async def handle_does_room_exist(client_id: str, payload: List[str], websocket: WebSocket):
#     roomID = payload[0]
#     print(f"checking if room works: {roomID}")
#     print(f"rooms: {manager.rooms}")
#     if roomID in WaitingRooms:
#         await manager.send_personal_message(f"receive_does_waiting_room_exist||true", websocket)
#     else:
#         await manager.send_personal_message(f"receive_does_waiting_room_exist||false", websocket)
#     if roomID in manager.rooms:
#         await manager.send_personal_message(f"receive_does_game_room_exist||true", websocket)

# async def handle_get_prompt(client_id: str, payload: List[str], websocket: WebSocket):
#     await manager.send_personal_message(f"receive_prompt||{manager.get_room(client_id).prompt}", websocket)

# async def handle_get_answers(client_id: str, payload: List[str], websocket: WebSocket):
#     await manager.send_personal_message(f"receive_answers||{json.dumps(manager.get_room(client_id).getPlayerCards(client_id=client_id))}", websocket)

# async def handle_commit_card(client_id: str, payload: List[str], websocket: WebSocket):
#     card_text = payload[0]
#     areAllCardsCommited = await manager.commit_card_and_return_if_full(client_id=client_id, card_text=card_text, websocket=websocket)
#     if areAllCardsCommited:
#         client_room = manager.get_room(client_id)
#         print(manager.get_room(client_id).commited_cards.items())
#         await manager.send_room_message(f"receive_goto_selection||{json.dumps(client_room.commited_cards)}", client_room)

# async def handle_add_score_to_card(client_id: str, payload: List[str], websocket: WebSocket):
#     client_id_of_card = payload[0]
#     are_all_preferences_done = manager.add_to_card_scores_and_return_if_all_commited(client_id=client_id, id_for_card=client_id_of_card)
#     print(f"are all done?: {str(are_all_preferences_done)}")
#     if are_all_preferences_done:
#         client_room = manager.get_room(client_id)
#         winner_data = manager.get_winner_data_and_reset_round(room=client_room)
#         print(f"winner data: {json.dumps(winner_data)}")
#         await manager.send_room_message(f"receive_winner||{json.dumps(winner_data)}", client_room)
#         prompt = client_room.gotoNextPromptAndReturnPrompt()
#         await manager.send_room_message(f"receive_prompt||{prompt}", client_room)

# async def handle_request_extra_card(client_id: str, payload: List[str], websocket: WebSocket):
#     latestCard = manager.get_room(client_id).getExtraCard(client_id=client_id)
#     await manager.send_personal_message(f"receive_extra_card||{json.dumps(latestCard)}", websocket)

# async def handle_submit_username(client_id: str, payload: List[str], websocket: WebSocket):
#     username = payload[0]
#     ClientToUserName[client_id] = username

# async def handle_add_to_waiting_room(client_id: str, payload: List[str], websocket: WebSocket):
#     id_and_username = json.loads(payload[0])
#     roomID = id_and_username["roomID"]
#     username = id_and_username["username"]
#     ClientToUserName[client_id] = username
#     if roomID in WaitingRooms:
#         if client_id not in WaitingRooms[roomID]:
#             WaitingRooms[roomID].append(client_id)
#     else:
#         WaitingRooms[roomID] = [client_id]
#     ClientToWaitingRoom[client_id] = roomID
#     clients_in_room = []
#     for client in WaitingRooms[roomID]:
#         clients_in_room.append(ClientToUserName[client])
#     clients_in_room = json.dumps(clients_in_room)
#     print(WaitingRooms[roomID])
#     for tempClient in WaitingRooms[roomID]:
#         await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", manager.ids_to_sockets[tempClient])

# async def handle_start_game_from_wait(client_id: str, payload: List[str], websocket: WebSocket):
#     waiting_room = ClientToWaitingRoom[client_id]
#     clients_in_waiting_room = WaitingRooms[waiting_room]
#     for tempClient in clients_in_waiting_room:
#         print(f"client {tempClient} should now go to their game")
#         await manager.send_personal_message(f"receive_goto_game||", manager.ids_to_sockets[tempClient])
#         await manager.send_personal_message(f"receive_connection||", manager.ids_to_sockets[tempClient])
#         del ClientToWaitingRoom[tempClient]
#     del WaitingRooms[waiting_room]

# handlers = {
#     "join_room": handle_join_room,
#     "does_room_exist": handle_does_room_exist,
#     "get_prompt": handle_get_prompt,
#     "get_answers": handle_get_answers,
#     "commit_card": handle_commit_card,
#     "add_score_to_card": handle_add_score_to_card,
#     "request_extra_card": handle_request_extra_card,
#     "submit_username": handle_submit_username,
#     "add_to_waiting_room": handle_add_to_waiting_room,
#     "start_game_from_wait": handle_start_game_from_wait
# }

# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     await manager.connect(websocket, client_id)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             header, *payload = data.split("||")
#             print(header, flush=True)
#             handler = handlers.get(header)
#             if handler:
#                 await handler(client_id, payload, websocket)
#             else:
#                 print(f"Unhandled header: {header}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket, client_id)
#         if client_id in ClientToUserName:
#             del ClientToUserName[client_id]
#         client_room = manager.get_room(client_id=client_id)
#         del client_room.players[client_id]
#         if client_id in ClientToWaitingRoom:
#             print("client should be removed from room", flush=True)
#             waiting_room = ClientToWaitingRoom[client_id]
#             WaitingRooms[waiting_room].remove(client_id)
#             del ClientToWaitingRoom[client_id]
#             clients_in_room = json.dumps(WaitingRooms[waiting_room])
#             for tempClient in WaitingRooms[waiting_room]:
#                 print(f"sending updates waiting to client: {tempClient}")
#                 await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", manager.ids_to_sockets[tempClient])
#         await manager.broadcast(f"Client #{client_id} left the chat")
