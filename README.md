# ♟️ Chess From Zero: Your AI-Powered Chess.com Assistant

## Unleash Your Inner Grandmaster (with a little help from AI!)

**Chess From Zero** is an intelligent Python-based assistant designed to elevate your Chess.com experience. Seamlessly integrating with the Stockfish chess engine and leveraging browser automation, this bot helps you play stronger, learn faster, and even mimic human-like playstyles. Whether you're looking to improve your game, analyze positions, or simply enjoy a new way to interact with Chess.com, Chess From Zero is your ultimate companion.

---

## ✨ Features

*   **Stockfish Integration:** Harness the power of one of the world's strongest chess engines to find optimal moves in real-time.
*   **Automated Gameplay:** Configure the bot to automatically make moves on Chess.com, allowing for hands-free play or analysis.
*   **Human-like Play (Configurable):**
    *   **Opening Book:** Utilizes a predefined opening book for natural, human-like initial moves, avoiding immediate engine-like play.
    *   **Contextual Thinking Time:** Introduces variable delays before moves, simulating human thought processes, especially in complex positions.
    *   **Advanced Time Management:** Adapts thinking time based on remaining clock time, mimicking how human players manage their clock under pressure.
*   **Color Detection:** Automatically detects your assigned color (White or Black) at the start of a game.
*   **Move Tracking:** Monitors and updates the internal board state based on both your moves and your opponent's moves.
*   **Configurable Settings:** Customize engine depth, auto-move behavior, and more via a simple `config.ini` file.
*   **Cross-Platform:** Built with Python and Playwright, it's designed to run on various operating systems.

---

## 🚀 Getting Started

Follow these steps to get Chess From Zero up and running on your machine.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/).
*   **Git**: For cloning the repository. Download from [git-scm.com](https://git-scm.com/downloads).
*   **Stockfish Chess Engine**: The `stockfish.exe` (or equivalent for Linux/macOS) is included in the `engine/` directory. No separate download is usually needed unless you want a different version.
*   **Browser (Chromium/Firefox/WebKit)**: Playwright will automatically download the necessary browser binaries, but ensure you have a compatible browser installed on your system.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/chess-from-zero.git
    cd chess-from-zero
    ```
    *(Replace `https://github.com/your-username/chess-from-zero.git` with your actual repository URL if you fork it.)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

### Configuration (`config.ini`)

The `config.ini` file in the root directory allows you to customize the bot's behavior.

```ini
[play]
mode = Blitz ; Game mode (e.g., Bullet, Blitz, Rapid). Affects the time control for finding opponents.
headless = false ; Whether to run the browser in headless mode (without a visible UI). Set to 'true' for background operation.
engine_depth = 15 ; Engine search depth (0-10 recommended for 'safe' botting to mimic human play and reduce detection risk. Higher depth = better moves, more CPU time).
auto_move = true ; Enable or disable automatic move execution by the bot. Set to 'true' to allow the bot to make moves.
auto_play = true ; Enable or disable automatic re-queuing for new games after a game ends.
num_games = 0 ; Number of games to play automatically (0 for unlimited).

; Contextual Thinking Time:
; This feature introduces a variable delay before the bot makes a move, simulating human thinking time.
; The delay is longer for "complex" positions where the engine's top moves are very close in evaluation.
complex_position_delay = 0.5 ; Additional delay (in seconds) added when a complex position is detected.
complex_position_threshold = 0.05 ; Threshold for score difference (in pawn units) between the best and second-best move.
                                  ; If the absolute difference is below this threshold, the position is considered complex.

; Advanced Time Management:
; This feature allows the bot to adjust its thinking time based on the remaining time on the clock.
; It will think longer when it has plenty of time and speed up when time is low, mimicking human time pressure.
advanced_time_management = true
```

**Key settings to adjust:**

*   `mode`: Set your preferred game mode (e.g., `Blitz`, `Rapid`).
*   `headless`: Set to `true` to run the browser in the background without a visible window.
*   `engine_depth`: Controls Stockfish's analysis depth. Higher values mean stronger play but consume more CPU.
*   `auto_move`: Set to `true` for the bot to automatically make moves.
*   `auto_play`: Set to `true` for the bot to automatically start new games after one finishes.
*   `num_games`: Set to `0` for unlimited games, or a specific number.
*   `complex_position_delay` & `complex_position_threshold`: Fine-tune the "human-like" thinking delays.
*   `advanced_time_management`: Enable/disable time-aware thinking.

### Credentials (`credentials.txt`)

Create a file named `credentials.txt` in the root directory with your Chess.com username and password, each on a new line:

```
your_username
your_password
```
**Important:** Keep this file secure and do not share it or commit it to public repositories.

---

## 🎮 Usage

To start the Chess From Zero assistant, run the `main.py` script:

```bash
python -m chess_assist.main
```

The bot will:
1.  Log in to Chess.com.
2.  Navigate to the play page.
3.  Start a game based on your `config.ini` settings.
4.  Analyze the board and make moves (if `auto_move` is enabled).
5.  Handle game endings and start new games (if `auto_play` is enabled).

You can also override `config.ini` settings via command-line arguments:

```bash
python chess_assist/main.py --mode Rapid --engine-depth 18 --headless True
```

---

## 🧠 How it Works: A Deep Dive into the Codebase

Chess From Zero operates through a carefully orchestrated interaction of several Python modules, each with a distinct responsibility. Here's a breakdown of the architecture and the flow of operations:

### Core Architecture

The project is structured into a `chess_assist/` directory (containing the main entry point) and a `src/` directory (housing the core logic modules).

*   **`chess_assist/main.py`**: The brain of the operation. It's the entry point that initializes the configuration, sets up logging, handles command-line arguments, manages the game loop, and orchestrates interactions between the `ChessBrowser` and `Game` classes.
*   **`src/browser.py`**: The bot's eyes and hands on the web. This module encapsulates all Playwright-related browser automation. It's responsible for launching the browser, logging into Chess.com, navigating to game pages, and interacting with UI elements (like clicking buttons, filling forms, and waiting for elements).
*   **`src/game.py`**: The chess intelligence and game state manager. This class maintains the internal `chess.Board()` representation, detects the player's color, tracks moves made by both players, and decides the bot's next move using the `StockfishEngine`. It also incorporates human-like delays and time management.
*   **`src/engine.py`**: The direct interface to the Stockfish chess engine. It manages the Stockfish process, sends commands (like `go depth`), receives analysis results, and extracts the best moves and their evaluations.
*   **`src/automove.py`**: The physical mover. This module takes the calculated best move and translates it into browser actions (simulated drag-and-drop) to execute the move on the Chess.com board. It includes logic for human-like mouse movements.
*   **`src/selectors.py`**: A centralized repository for all CSS selectors used to identify elements on Chess.com. This makes the code cleaner and easier to maintain if Chess.com's HTML structure changes.
*   **`src/utils.py`**: Contains helper functions, such as `_parse_config_value`, used across different modules for common tasks.

### Operational Flow

1.  **Initialization (`chess_assist/main.py`):**
    *   The script starts by parsing command-line arguments, allowing users to override settings from `config.ini`.
    *   It reads `config.ini` to load various operational parameters (e.g., `mode`, `headless`, `engine_depth`, `auto_move`, `auto_play`, `num_games`, `complex_position_delay`, `complex_position_threshold`, `advanced_time_management`).
    *   Logging is configured based on the `debug` argument.
    *   User credentials are retrieved from `credentials.txt` (or prompted if not found).
    *   Instances of `ChessBrowser` and `Game` are created, passing the loaded configuration and browser instance.

2.  **Browser Setup & Login (`src/browser.py`):**
    *   `browser.start()`: Launches a Chromium browser instance using Playwright. The `headless` setting from `config.ini` determines if the browser UI is visible.
    *   `browser.login(username, password)`: Navigates to Chess.com's login page, fills in credentials, and clicks the login button. It includes robust error handling and waits for the home page to load successfully.

3.  **Game Loop (`chess_assist/main.py`):**
    *   The `main` function enters a `while True` loop, which continues until `num_games` is reached or `auto_play` is disabled after one game.
    *   `browser.select_mode()`: Navigates to the Chess.com play page, clicks the time control dropdown, and selects the game mode specified in `config.ini` (e.g., Blitz, Rapid). It then clicks the "Play" button to start a new game.
    *   `game.start()`: Initializes the internal `chess.Board()` object, detects the player's color (White or Black) by checking the "flipped" class on the board element, and then calls `game.play_best_move()` if the bot is playing as White (to make the first move).
    *   `game.track_moves()`: This is the core loop for active gameplay. It continuously monitors the Chess.com UI for new moves made by the opponent.
        *   It waits for a new move element to appear in the move list (using XPath based on the current ply).
        *   It parses the opponent's move (SAN format) and pushes it to the internal `chess.Board()`.
        *   If it's the bot's turn (`self.board.turn == self.color`), it calls `game.play_best_move()`.
        *   It also includes logic to detect if the game is over (e.g., checkmate, stalemate, or game over modal).

4.  **Determining the Best Move (`src/game.py` & `src/engine.py`):**
    *   `game.play_best_move()`:
        *   First, it checks if the current board position exists in the `OPENING_BOOK`. If a legal opening move is found, it randomly selects one and uses it. This adds a human-like variability to openings.
        *   If no opening book move is available, it calls `self.engine.get_best_move(self.board)` to query Stockfish.
        *   **Human-like Delays:** Before executing the move, it calculates an `additional_delay`. This delay is influenced by:
            *   `complex_position_threshold` and `complex_position_delay`: If the score difference between the best and second-best move is small (indicating a complex position), an additional delay is added.
            *   `advanced_time_management`: If enabled, the bot adjusts its thinking time based on the remaining time on its clock, thinking longer with more time and speeding up when time is low.
        *   It then proceeds to highlight the squares (though the highlighting script is in `highlight.js`, its execution is triggered here via `browser.page.evaluate`).
        *   Finally, it calls `self.automove.execute_move()` to perform the move on the Chess.com UI.
    *   `engine.py` (`StockfishEngine`):
        *   `get_best_move(board, depth)`: This method sends the current board state to the Stockfish engine.
        *   It uses the `engine_depth` from `config.ini` to set the search depth for Stockfish.
        *   It analyzes the position (`engine.analyse`) and returns the best move found by Stockfish, along with a list of top moves and their scores (used for contextual thinking time).

5.  **Executing the Move (`src/automove.py`):**
    *   `automove.execute_move(move, letak_gerakan, is_flipped)`:
        *   Checks the `auto_move` setting from `config.ini`. If `false`, it does nothing.
        *   Applies a random delay based on the `mode` and `letak_gerakan` (move number), simulating human reaction times that vary with game phase and time control.
        *   Calculates the pixel coordinates for the `from_square` and `to_square` on the Chess.com board, taking into account whether the board is flipped.
        *   Uses Playwright's `page.mouse.move`, `page.mouse.down`, and `page.mouse.up` to simulate a human-like drag-and-drop action. This includes small random offsets and delays during the mouse movement to make it less robotic.

6.  **Game End & Re-queuing (`chess_assist/main.py`):**
    *   When `game.track_moves()` returns (indicating the game is over), `main.py` checks the `auto_play` setting.
    *   If `auto_play` is `true`, it calls `handle_game_over_modal()` to find and click the "New Game" button within the game over modal, effectively starting a new game. The button text is determined by the `mode` setting.
    *   The `games_played` counter is incremented, and the loop continues until `num_games` is reached.

7.  **Cleanup (`src/browser.py`):**
    *   `browser.close()`: Ensures the Playwright browser instance is properly closed when the script finishes or encounters an error.

---

## 📂 Project Structure

```
.
├── config.ini              # Main configuration file for the bot
├── credentials.txt         # Your Chess.com login credentials (KEEP SECURE!)
├── README.md               # This file!
├── requirements.txt        # Python dependencies
├── chess_assist/
│   ├── __init__.py
│   └── main.py             # Main entry point for the bot
├── engine/
│   └── stockfish.exe       # Stockfish chess engine executable
└── src/
    ├── __init__.py
    ├── automove.py         # Handles automated move execution on the browser with human-like mouse movements.
    ├── browser.py          # Manages Playwright browser interactions (launch, login, navigation, UI clicks).
    ├── engine.py           # Interfaces with the Stockfish engine to get best moves and analysis.
    ├── game.py             # Manages internal chess board state, game logic, move tracking, and AI decision-making.
    ├── highlight.js        # JavaScript for highlighting squares on the Chess.com UI (executed via Playwright).
    ├── parse.py            # (Currently unused, but could be for parsing game data or specific UI elements.)
    ├── selectors.py        # Stores CSS selectors for Chess.com elements to ensure robust UI interaction.
    └── utils.py            # Contains utility functions, like parsing config values.
```

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or new features, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
*(Note: You might need to create a `LICENSE` file if you haven't already.)*

---

## 📞 Support & Contact

If you encounter any issues or have questions, please open an issue on the GitHub repository.