import pytest
from unittest.mock import Mock
from implementation.publish_subscribe.event_manager import EventManager, EventType
from implementation.publish_subscribe.move_logger_display import MoveLoggerDisplay

@pytest.fixture
def event_manager():
    return EventManager()

def test_subscribe(event_manager):
    mock_subscriber = Mock()
    event_manager.subscribe(EventType.GAME_START, mock_subscriber)
    assert EventType.GAME_START in event_manager.subscribers
    assert len(event_manager.subscribers[EventType.GAME_START]) == 1

def test_publish_event_with_no_subscribers(event_manager, capsys):
    event_manager.publish(EventType.GAME_START)
    captured = capsys.readouterr().out
    # בודקים שהפלט כולל בדיוק את ההודעה
    assert "DEBUG: No listeners registered for event type GAME_START (Value: 1)" in captured

def test_publish_event_with_subscriber(event_manager):
    mock_subscriber = Mock()
    event_manager.subscribe(EventType.GAME_START, mock_subscriber)
    event_manager.publish(EventType.GAME_START)
    mock_subscriber.assert_called_once()

def test_publish_event_with_wrong_arguments(event_manager, capsys):
    mock_subscriber = Mock(side_effect=TypeError)
    setattr(mock_subscriber, '__name__', 'mock_subscriber')  # NEW: להגדיר __name__ למוק
    event_manager.subscribe(EventType.GAME_START, mock_subscriber)
    try:
        event_manager.publish(EventType.GAME_START, "wrong_arg")
    except TypeError:
        pass  # לא צפוי להזריק, הקוד מטפל בשגיאה
    captured = capsys.readouterr().out
    # נוודא שהפלט מכיל את המחרוזת הרלוונטית
    assert "for GAME_START failed with arguments ('wrong_arg',), {}." in captured

@pytest.fixture
def move_logger(event_manager):
    return MoveLoggerDisplay(event_manager)

def test_on_game_start(move_logger):
    move_logger._on_game_start()
    assert move_logger.moves_history == []
    assert move_logger.white_score == 0
    assert move_logger.black_score == 0

def test_on_piece_moved(move_logger):
    move_logger._on_piece_moved('white', 'pawn', (1, 2), (1, 3))
    assert len(move_logger.moves_history) == 1
    assert move_logger.moves_history[0]['move_desc'] == 'Pawn a7-a8'

def test_on_piece_captured(move_logger):
    move_logger._on_piece_captured('white', 'pawn', (1, 2), (1, 3), 'knight', 'black')
    assert len(move_logger.moves_history) == 1
    # כעת ההודעה נוצרת כ"Pawn a7xa8 (Knight)" (ללא רווח אחרי ה־x)
    assert move_logger.moves_history[0]['move_desc'] == 'Pawn a7xa8 (Knight)'

def test_on_piece_jumped(move_logger):
    move_logger._on_piece_jumped('black', 'knight', (2, 3))
    assert len(move_logger.moves_history) == 1
    assert move_logger.moves_history[0]['move_desc'] == 'Knight enters Jump state at c6'
