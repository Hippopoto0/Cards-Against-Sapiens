from typing import List, Dict
from fastapi import WebSocket
from fastapi.logger import logger
from .models import Room, WaitingRooms, ClientToWaitingRoom, ClientToUserName

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ids_to_sockets: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Room] = {"AAAAA": Room(id="AAAAA")}
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
        if self.rooms.get(room_id) == None:
            return self.create_room(client_id=client_id, room_id=room_id)
        print(f"lets see if this room exists: {str(self.rooms.get(room_id))}")
        room = self.rooms[room_id]
        room.addPlayerToRoom(client_id=client_id)
        room.giveHandToPlayer(client_id=client_id)

    def create_room(self, client_id: str, room_id: str):
        print("is this room beng created?", flush=True)
        self.rooms[room_id] = Room(id=room_id)
        self.join_room(room_id=room_id, client_id=client_id)

    async def commit_card_and_return_if_full(self, client_id: str, card_text: str, websocket: WebSocket) -> bool:
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
        maxClientID = max(room.preferenceCount, key=room.preferenceCount.get)
        if maxClientID in ClientToUserName:
            maxClientUsername = ClientToUserName[maxClientID]
            maxClientCard = room.commited_cards[maxClientID]
        else:
            maxClientUsername = "Winner Left Room"
            maxClientCard = "Winner Left Room"
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
