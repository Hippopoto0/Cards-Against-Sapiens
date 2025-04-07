import json
from fastapi import WebSocket
from .connection_manager import manager
from .models import WaitingRooms, ClientToWaitingRoom, ClientToUserName

async def handle_join_room(client_id: str, payload: list, websocket: WebSocket):
    roomID = payload[0]
    print(f"roomID: {roomID}")
    manager.socket_to_rooms[client_id] = roomID
    manager.join_room(room_id=roomID, client_id=client_id)
    print(f"Rooms after join: {manager.rooms}", flush=True)
    await manager.send_personal_message("receive_room||AAAAA", websocket)

async def handle_does_room_exist(client_id: str, payload: list, websocket: WebSocket):
    roomID = payload[0]
    print(f"checking if room works: {roomID}")
    print(f"rooms: {manager.rooms}")
    if roomID in WaitingRooms:
        await manager.send_personal_message("receive_does_waiting_room_exist||true", websocket)
    else:
        await manager.send_personal_message("receive_does_waiting_room_exist||false", websocket)
    if roomID in manager.rooms:
        await manager.send_personal_message("receive_does_game_room_exist||true", websocket)

async def handle_get_prompt(client_id: str, payload: list, websocket: WebSocket):
    await manager.send_personal_message(f"receive_prompt||{manager.get_room(client_id).prompt}", websocket)

async def handle_get_answers(client_id: str, payload: list, websocket: WebSocket):
    await manager.send_personal_message(f"receive_answers||{json.dumps(manager.get_room(client_id).getPlayerCards(client_id=client_id))}", websocket)

async def handle_commit_card(client_id: str, payload: list, websocket: WebSocket):
    card_text = payload[0]
    areAllCardsCommited = await manager.commit_card_and_return_if_full(client_id=client_id, card_text=card_text, websocket=websocket)
    if areAllCardsCommited:
        client_room = manager.get_room(client_id)
        print(manager.get_room(client_id).commited_cards.items())
        await manager.send_room_message(f"receive_goto_selection||{json.dumps(client_room.commited_cards)}", client_room)

async def handle_add_score_to_card(client_id: str, payload: list, websocket: WebSocket):
    client_id_of_card = payload[0]
    are_all_preferences_done = manager.add_to_card_scores_and_return_if_all_commited(client_id=client_id, id_for_card=client_id_of_card)
    print(f"are all done?: {str(are_all_preferences_done)}")
    if are_all_preferences_done:
        client_room = manager.get_room(client_id)
        winner_data = manager.get_winner_data_and_reset_round(room=client_room)
        print(f"winner data: {json.dumps(winner_data)}")
        await manager.send_room_message(f"receive_winner||{json.dumps(winner_data)}", client_room)
        prompt = client_room.gotoNextPromptAndReturnPrompt()
        await manager.send_room_message(f"receive_prompt||{prompt}", client_room)

async def handle_request_extra_card(client_id: str, payload: list, websocket: WebSocket):
    latestCard = manager.get_room(client_id).getExtraCard(client_id=client_id)
    await manager.send_personal_message(f"receive_extra_card||{json.dumps(latestCard)}", websocket)

async def handle_submit_username(client_id: str, payload: list, websocket: WebSocket):
    username = payload[0]
    ClientToUserName[client_id] = username

async def handle_add_to_waiting_room(client_id: str, payload: list, websocket: WebSocket):
    id_and_username = json.loads(payload[0])
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
        await manager.send_personal_message(f"receive_waiting_players||{clients_in_room}", manager.ids_to_sockets[tempClient])

async def handle_start_game_from_wait(client_id: str, payload: list, websocket: WebSocket):
    waiting_room = ClientToWaitingRoom[client_id]
    clients_in_waiting_room = WaitingRooms[waiting_room]
    for tempClient in clients_in_waiting_room:
        print(f"client {tempClient} should now go to their game")
        await manager.send_personal_message("receive_goto_game||", manager.ids_to_sockets[tempClient])
        await manager.send_personal_message("receive_connection||", manager.ids_to_sockets[tempClient])
        del ClientToWaitingRoom[tempClient]
    del WaitingRooms[waiting_room]

handlers = {
    "join_room": handle_join_room,
    "does_room_exist": handle_does_room_exist,
    "get_prompt": handle_get_prompt,
    "get_answers": handle_get_answers,
    "commit_card": handle_commit_card,
    "add_score_to_card": handle_add_score_to_card,
    "request_extra_card": handle_request_extra_card,
    "submit_username": handle_submit_username,
    "add_to_waiting_room": handle_add_to_waiting_room,
    "start_game_from_wait": handle_start_game_from_wait
}
