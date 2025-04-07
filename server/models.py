from typing import List, Dict, Any
import random
import copy
from contextlib import suppress
import os
import json
from pathlib import Path

white_cards: List[Any] = []
black_cards: List[Any] = []

with open(Path(os.path.abspath(".")) / "server" / "allCards.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    white_cards = [card for pack in data for card in pack["white"]]
    black_cards = [card for pack in data for card in pack["black"]]
    random.shuffle(white_cards)
    random.shuffle(black_cards)

class Player:
    def __init__(self) -> None:
        self.cards = []

WaitingRooms: Dict[str, List[str]] = {}
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

    def getCards(self) -> List[Any]:
        temp_cards = []
        for i in range(10):
            self.white_cards.append(self.white_cards[0])
            temp_cards.append(self.white_cards.pop(0))
        return temp_cards

    def removePlayerFromRoom(self, client_id: str) -> None:
        del self.players[client_id]
        with suppress(KeyError):
            del self.commited_cards[client_id]
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

    def getPlayerCards(self, client_id: str) -> List[Any]:
        player = self.players[client_id]
        return player.cards

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
