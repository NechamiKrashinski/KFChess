import pathlib
from typing import Tuple
import pygame

from .event_manager import EventManager, EventType


class SoundSubscriber:
    def __init__(self, event_manager: EventManager):
        pygame.mixer.init()
        self.sound_folder = pathlib.Path(__file__).parent.parent.parent / "assets" / "sounds"
        
        try:
            self.move_sound = pygame.mixer.Sound(str(self.sound_folder / "move.wav"))
            self.capture_sound = pygame.mixer.Sound(str(self.sound_folder / "capture.wav"))
            self.jump_sound = pygame.mixer.Sound(str(self.sound_folder / "jump.wav"))
            self.illegal_move_sound = pygame.mixer.Sound(str(self.sound_folder / "illegal.mp3"))
        except pygame.error as e:
            self.move_sound = None
            self.capture_sound = None
            self.jump_sound = None
            self.illegal_move_sound = None

        event_manager.subscribe(EventType.PIECE_MOVED, self.on_piece_moved_sound)
        event_manager.subscribe(EventType.PIECE_CAPTURED, self.on_piece_captured_sound)
        event_manager.subscribe(EventType.PIECE_JUMPED, self.on_piece_jumped_sound)
        event_manager.subscribe(EventType.ILLEGAL_MOVE, self.on_illegal_move)

    def on_piece_moved_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        if self.move_sound:
            self.move_sound.play()

    def on_piece_captured_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], captured_piece_type: str, captured_piece_color: str):
        if self.capture_sound:
            self.capture_sound.play()

    def on_piece_jumped_sound(self, piece_color: str, piece_type: str, cell_coords: Tuple[int, int]):
        if self.jump_sound:
            self.jump_sound.play()

    def on_illegal_move(self):
        if self.illegal_move_sound:
            self.illegal_move_sound.play()