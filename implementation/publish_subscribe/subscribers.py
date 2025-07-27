import pygame



import pygame
from typing import Tuple # נוסיף אימפורט ל-Tuple

class SoundSubscriber:
    def __init__(self):
        pygame.mixer.init()
        self.eat_sound = pygame.mixer.Sound(r"C:\Users\user1\Documents\Bootcamp\KFChess\erase4.wav")
        self.move_sound = pygame.mixer.Sound(r"C:\Users\user1\Documents\Bootcamp\KFChess\move_piece.wav")
        print("SoundSubscriber initialized with sounds.")

    # שימו לב: הפונקציה on_piece_eaten שונתה
    # כעת היא מקבלת את אותם פרמטרים כמו _on_piece_captured ב-MoveLoggerDisplay
    def on_piece_captured_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int], captured_piece_type: str, captured_piece_color: str):
        print(f"Playing sound for {captured_piece_color} {captured_piece_type} being captured by {piece_color} {piece_type}")
        self.eat_sound.play()

    # שימו לב: הפונקציה on_piece_moved_sound שונתה
    # כעת היא מקבלת את אותם פרמטרים כמו _on_piece_moved ב-MoveLoggerDisplay
    def on_piece_moved_sound(self, piece_color: str, piece_type: str, from_coords: Tuple[int, int], to_coords: Tuple[int, int]):
        print(f"Playing sound for {piece_color} {piece_type} moving from {from_coords} to {to_coords}")
        self.move_sound.play()


class DisplaySubscriber:
    def on_game_start(self):
        print("Game started!")

    def on_game_end(self, winner: str):
        print(f"Game ended! Winner: {winner}")