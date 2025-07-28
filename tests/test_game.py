import pathlib
import cv2
import pytest
import time
from implementation.board import Board
from implementation.command import Command
from implementation.mock_img import MockImg
from implementation.piece import Piece
from implementation.piece_factory import PieceFactory
from implementation.publish_subscribe.event_manager import EventManager
from implementation.publish_subscribe.message_display import MessageDisplay
from implementation.publish_subscribe.move_logger_display import MoveLoggerDisplay
from implementation.publish_subscribe.sound_subscriber import SoundSubscriber
from implementation.img import Img
from implementation.game import Game

@pytest.fixture
def setup_game_with_kings():
    board = Board(100,100,7,7,10,10,Img())
    pieces = [
        Piece("KW_0_0", "King", "W", (0,0)),
        Piece("KB_6_6", "King", "B", (6,6)),
        Piece("PW_0_1", "Pawn", "W", (0,1)),
        Piece("PB_1_1", "Pawn", "B", (1,1))
    ]
    event_manager = EventManager()
    background_img = Img()
    move_logger_display = MoveLoggerDisplay(event_manager)
    message_display = MessageDisplay(event_manager)
    sound_subscriber = SoundSubscriber(event_manager)
    piece_factory = PieceFactory(board, pathlib.Path(r"C:\Users\user1\Documents\Bootcamp\KFChess\assets\pieces_resources"))

    game = Game(pieces, board, event_manager, background_img,
                move_logger_display, message_display, sound_subscriber, piece_factory)
    return game

def test_is_win_initial_state(setup_game_with_kings):
    game = setup_game_with_kings
    assert not game._is_win()

def test_is_win_white_wins(setup_game_with_kings):
    game = setup_game_with_kings
    del game.pieces["KB_6_6"] 
    assert game._is_win()

def test_is_win_black_wins(setup_game_with_kings):
    game = setup_game_with_kings
    del game.pieces["KW_0_0"]
    assert game._is_win()

def test_is_win_draw_no_kings(setup_game_with_kings):
    game = setup_game_with_kings
    del game.pieces["KW_0_0"]
    del game.pieces["KB_6_6"]
    assert game._is_win()