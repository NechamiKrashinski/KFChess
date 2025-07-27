from enum import Enum
from typing import Callable

import pygame

class EventType(Enum):
    PIECE_EATEN = 1
    GAME_START = 2
    GAME_END = 3
    # הוסף עוד סוגי אירועים לפי הצורך

class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: EventType, subscriber: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(subscriber)

    def publish(self, event_type: EventType, *args, **kwargs):
        if event_type in self.subscribers:
            for subscriber in self.subscribers[event_type]:
                subscriber(*args, **kwargs)

class SoundSubscriber:
    def __init__(self):
        pygame.mixer.init()
        self.eat_sound = pygame.mixer.Sound(r"C:\Users\user1\Documents\Bootcamp\KFChess\erase4.wav")

    def on_piece_eaten(self, piece_id: str):
        print(f"Playing sound for piece {piece_id} being eaten")
        self.eat_sound.play()

class DisplaySubscriber:
    def on_game_start(self):
        print("Game started!")

    def on_game_end(self, winner: str):
        print(f"Game ended! Winner: {winner}")
