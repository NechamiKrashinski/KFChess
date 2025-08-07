# KFChess ♟️

KFChess is a **revolutionary simultaneous chess game** implemented in Python with an OpenCV-based graphics engine. Unlike classical chess, here **both players act simultaneously** without turns! The game features special mechanics like jump moves, animated state systems, and dual input systems enabling real-time simultaneous interaction.

## Features ✨

- **Simultaneous Gameplay:** Both players can play at the same time - White player with mouse, Black player with keyboard
- **Jump System:** Special mechanic allowing pieces to perform tactical jumps to the same square
- **Advanced Animations:** Each piece can be in different states (idle, move, jump, rest) with animated sprites
- **Cooldown System:** Waiting mechanism between moves that adds tactical depth
- **Sound & Effects:** Dynamic sound system with effects for different moves
- **Pawn Promotion:** Pawns automatically promote to Queen when reaching the end of the board
- **Message System:** Visual tracking of moves and captures with on-screen display

## Project Structure 📂

The project consists of the following modules:

### Main Files:
*   `main.py`: Main entry point of the game 🚀
*   `requirements.txt`: List of required dependencies 📦

### implementation/ Directory - The Technical Core:
*   `game.py`: Main game engine, game logic and input handling ♟️
*   `board.py`: Board and square representation 🏁
*   `piece.py`: Base piece class with states and animations 👑
*   `moves.py`: Classical chess move logic 🎯
*   `physics.py` & `physics_factory.py`: Physics engine and positioning 🔧
*   `graphics.py` & `graphics_factory.py`: Graphics engine and sprites 🎨
*   `state.py`: State system with transitions and timers ⚙️
*   `game_builder.py`: Builder pattern for game creation 🏗️
*   `command.py`: Command system for moves 📝
*   `img.py`: Advanced image processing with OpenCV 🖼️

### publish_subscribe/ Directory - Event System:
*   `event_manager.py`: Central event manager 📡
*   `message_display.py`: On-screen message display 💬
*   `move_logger_display.py`: Move logging and display 📊
*   `sound_subscriber.py`: Sound system 🔊

### assets/ Directory - Game Resources:
*   `board.csv`: Initial board layout with piece positions 🗺️
*   `board.png` & `background.png`: Background and board images 🖼️
*   `pieces_resources/`: Directory with all pieces, each piece contains:
    - `config.json`: Piece settings and states
    - `moves.txt`: Allowed movement rules
    - `states/`: Folders with sprites for each state (idle, move, jump, rest)

### tests/ Directory - Automated Testing:
*   Comprehensive tests for every system component with pytest 🧪
*   Full code coverage with htmlcov/ 📈

## Installation & Running 🏁

### Prerequisites:
1. **Python 3.7+** (tested with Python 3.13)
2. **Required packages:**
   ```bash
   pip install opencv-python pygame python-dotenv pytest
   ```

### Installation Instructions:
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd KFChess
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

## How to Play 🕹️

### White Player (Mouse) 🖱️:
1. Click on a white piece to select it
2. Click on target square to move
3. Double-click on the same square to perform a Jump

### Black Player (Keyboard) ⌨️:
1. Use arrow keys to move the red cursor
2. [Exact key mappings require further investigation in source]

### Special Features:
- **Jump Mode:** Allows a piece to jump to a square and capture pieces that arrive there
- **Cooldown:** After a move, the piece enters rest state and cannot move temporarily
- **Pawn Promotion:** Pawn reaching the end of the board automatically becomes a Queen

## Advanced Technical Information 🔧

### Architecture:
- **Factory Pattern** for creating pieces and graphics
- **State Machine** for managing piece states
- **Observer Pattern** for the event system
- **Command Pattern** for managing game commands

### Graphics System:
- OpenCV for image processing and display
- Changing sprite system for animations
- Dynamic drawing of board and pieces
- Visual cursors and indicators for selections and piece states

### Testing:
```bash
# Run all tests
pytest

# Generate coverage report
pytest --cov=implementation --cov-report=html
```

## What Else Is Here? 🎮

This project is much more than just a "basic chess game". It's a complete game engine featuring:
- Custom physics and graphics systems
- Visual animations and effects
- Dynamic sound system
- Well-designed code following SOLID principles
- Comprehensive test coverage

This is a project demonstrating advanced programming capabilities and quality software design.

## Technical Implementation Details 🛠️

### Simultaneous Chess Mechanics:
The game implements a unique simultaneous chess variant where:
- Both players can select and move pieces at any time
- No turn-based restrictions
- Special jump mechanic for tactical positioning
- Collision detection when pieces meet at the same square
- State-based cooldown system preventing rapid consecutive moves

### Real-Time Features:
- **Live Input Processing:** Mouse and keyboard inputs processed in real-time
- **Event-Driven Architecture:** Publish-subscribe pattern for game events
- **State Synchronization:** All piece states updated continuously
- **Visual Feedback:** Immediate visual response to player actions

This represents a novel approach to chess gameplay, combining traditional chess rules with real-time strategy elements.
