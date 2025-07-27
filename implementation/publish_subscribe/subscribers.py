# implementation/publish_subscribe/sound_subscriber.py

from typing import Tuple
import pygame
import pathlib
from .event_manager import EventManager, EventType # וודא ייבוא נכון של EventType

class SoundSubscriber:
    def __init__(self):
        pygame.mixer.init()
        self.sound_folder = pathlib.Path(__file__).parent.parent.parent / "assets" / "sounds"
        
        try:
            self.move_sound = pygame.mixer.Sound(str(self.sound_folder / "move.wav"))
            self.capture_sound = pygame.mixer.Sound(str(self.sound_folder / "capture.wav"))
            self.jump_sound = pygame.mixer.Sound(str(self.sound_folder / "jump.wav"))
            print("SoundSubscriber: Sounds loaded successfully.")
        except pygame.error as e:
            print(f"ERROR: Could not load sound file: {e}")
            self.move_sound = None
            self.capture_sound = None
            self.jump_sound = None

    def on_piece_moved_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        if self.move_sound:
            self.move_sound.play()
            print(f"Sound played for PIECE_MOVED: {piece_type} from {from_coords} to {to_coords}")

    def on_piece_captured_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], captured_piece_type: str, captured_piece_color: str):
        """
        פונקציה זו מטפלת בצליל כאשר כלי נאכל.
        הפרמטרים חייבים להתאים במדויק לפרמטרים שמועברים ב-event_manager.publish.
        """
        if self.capture_sound:
            self.capture_sound.play()
            print(f"Sound played for PIECE_CAPTURED: {piece_type} ({piece_color}) captured {captured_piece_type} ({captured_piece_color})")

    def on_piece_jumped_sound(self, piece_color: str, piece_type: str, cell_coords: Tuple[int, int]):
        """
        פונקציה זו מטפלת בצליל כאשר כלי נכנס למצב קפיצה (jump).
        """
        if self.jump_sound:
            self.jump_sound.play()
            print(f"Sound played for PIECE_JUMPED: {piece_type} ({piece_color}) at {cell_coords}")
class DisplaySubscriber:
    def on_game_start(self):
        print("Game started!")

    def on_game_end(self, winner: str):
        print(f"Game ended! Winner: {winner}")