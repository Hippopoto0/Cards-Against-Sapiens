import pytest
import json
from handlers import handlers
from connection_manager import manager
from models import WaitingRooms, ClientToWaitingRoom, ClientToUserName, Room

class DummyWebSocket:
    def __init__(self):
        self.sent_messages = []

    async def send_text(self, message: str):
        self.sent_messages.append(message)

@pytest.fixture(autouse=True)
def reset_state():
    manager.active_connections = []
    manager.ids_to_sockets = {}
    manager.rooms = {"AAAAA": Room("AAAAA")}
    manager.socket_to_rooms = {}
    WaitingRooms.clear()
    ClientToWaitingRoom.clear()
    ClientToUserName.clear()
    yield

@pytest.mark.asyncio
async def test_handle_join_room():
    dummy_ws = DummyWebSocket()
    client_id = "client1"
    payload = ["ROOM1"]
    await handlers["join_room"](client_id, payload, dummy_ws)
    assert manager.socket_to_rooms.get(client_id) == "ROOM1"
    assert "ROOM1" in manager.rooms
    assert "receive_room||AAAAA" in dummy_ws.sent_messages

@pytest.mark.asyncio
async def test_handle_does_room_exist():
    dummy_ws = DummyWebSocket()
    client_id = "client2"
    payload = ["ROOM2"]
    await handlers["does_room_exist"](client_id, payload, dummy_ws)
    assert "receive_does_waiting_room_exist||false" in dummy_ws.sent_messages
    WaitingRooms["ROOM2"] = ["clientX"]
    manager.rooms["ROOM2"] = Room("ROOM2")
    dummy_ws.sent_messages.clear()
    await handlers["does_room_exist"](client_id, payload, dummy_ws)
    assert "receive_does_waiting_room_exist||true" in dummy_ws.sent_messages
    assert "receive_does_game_room_exist||true" in dummy_ws.sent_messages

@pytest.mark.asyncio
async def test_handle_get_prompt():
    dummy_ws = DummyWebSocket()
    client_id = "client3"
    manager.socket_to_rooms[client_id] = "AAAAA"
    prompt = manager.rooms["AAAAA"].prompt
    await handlers["get_prompt"](client_id, [], dummy_ws)
    assert f"receive_prompt||{prompt}" in dummy_ws.sent_messages

@pytest.mark.asyncio
async def test_handle_get_answers():
    dummy_ws = DummyWebSocket()
    client_id = "client4"
    manager.socket_to_rooms[client_id] = "AAAAA"
    room = manager.rooms["AAAAA"]
    room.addPlayerToRoom(client_id)
    room.giveHandToPlayer(client_id)
    answers = room.getPlayerCards(client_id)
    await handlers["get_answers"](client_id, [], dummy_ws)
    expected = f"receive_answers||{json.dumps(answers)}"
    assert expected in dummy_ws.sent_messages

@pytest.mark.asyncio
async def test_handle_commit_card():
    dummy_ws = DummyWebSocket()
    client_id = "client5"
    manager.socket_to_rooms[client_id] = "AAAAA"
    room = manager.rooms["AAAAA"]
    room.addPlayerToRoom(client_id)
    payload = ["Test Card"]
    await handlers["commit_card"](client_id, payload, dummy_ws)
    found = any("receive_goto_selection||" in msg for msg in dummy_ws.sent_messages)
    assert found

@pytest.mark.asyncio
async def test_handle_add_score_to_card():
    dummy_ws = DummyWebSocket()
    client_id = "client6"
    manager.socket_to_rooms[client_id] = "AAAAA"
    room = manager.rooms["AAAAA"]
    room.addPlayerToRoom(client_id)
    payload = ["client6"]
    await handlers["add_score_to_card"](client_id, payload, dummy_ws)
    msgs = " ".join(dummy_ws.sent_messages)
    assert "receive_winner||" in msgs
    assert "receive_prompt||" in msgs

@pytest.mark.asyncio
async def test_handle_request_extra_card():
    dummy_ws = DummyWebSocket()
    client_id = "client7"
    manager.socket_to_rooms[client_id] = "AAAAA"
    room = manager.rooms["AAAAA"]
    room.addPlayerToRoom(client_id)
    payload = []
    await handlers["request_extra_card"](client_id, payload, dummy_ws)
    found = any("receive_extra_card||" in msg for msg in dummy_ws.sent_messages)
    assert found

@pytest.mark.asyncio
async def test_handle_submit_username():
    dummy_ws = DummyWebSocket()
    client_id = "client8"
    payload = ["Alice"]
    await handlers["submit_username"](client_id, payload, dummy_ws)
    assert ClientToUserName.get(client_id) == "Alice"

@pytest.mark.asyncio
async def test_handle_add_to_waiting_room():
    dummy_ws = DummyWebSocket()
    client_id = "client9"
    payload = [json.dumps({"roomID": "WAIT1", "username": "Bob"})]
    await handlers["add_to_waiting_room"](client_id, payload, dummy_ws)
    assert ClientToWaitingRoom.get(client_id) == "WAIT1"
    assert client_id in WaitingRooms.get("WAIT1", [])
    found = any("receive_waiting_players||" in msg for msg in dummy_ws.sent_messages)
    assert found

@pytest.mark.asyncio
async def test_handle_start_game_from_wait():
    dummy_ws1 = DummyWebSocket()
    dummy_ws2 = DummyWebSocket()
    client_id1 = "client10"
    client_id2 = "client11"
    WaitingRooms["WAIT2"] = [client_id1, client_id2]
    ClientToWaitingRoom[client_id1] = "WAIT2"
    ClientToWaitingRoom[client_id2] = "WAIT2"
    manager.ids_to_sockets[client_id1] = dummy_ws1
    manager.ids_to_sockets[client_id2] = dummy_ws2
    payload = []
    await handlers["start_game_from_wait"](client_id1, payload, dummy_ws1)
    assert "WAIT2" not in WaitingRooms
    found1 = any("receive_goto_game||" in msg for msg in dummy_ws1.sent_messages)
    found2 = any("receive_goto_game||" in msg for msg in dummy_ws2.sent_messages)
    assert found1 and found2
