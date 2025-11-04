<div align="center">

```
  _____ _    _  ______ _____  _____ ______ _____  ______ _____  
 / ____| |  | |/ __  // ____|/ ____|  ____|  __ \|  ____|  __ \ 
| |    | |__| | |  | | |    | (___ | |__  | |__) | |__  | |__) |
| |    |  __  | |  | | |     \___ \|  __| |  _  /|  __| |  _  / 
| |____| |  | | |__| | |____ ____) | |____| | \ \| |____| | \ \
 \_____|_|  |_|\_____/ \_____|_____/|______|_|  \_\______|_|  \_\
                                                               
```

**Your AI-Powered Chess.com Assistant**

</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://shields.io/)

</div>

---

### **Elevate Your Game to the Next Level. Automatically.**

**Chess From Zero** is not just a chess bot. It's an intelligent, Python-based assistant designed to be your sparring partner, analysis tool, and right hand on Chess.com. Powered by the **Stockfish** engine and sophisticated browser automation, this bot is engineered to play with a remarkably human-like style, allowing you to explore new strategies and dominate the game while staying under the radar.

---

## ✨ Key Features

*   **♟️ Hyper-Realistic Playstyle:** Forget rigid bots. With **Dynamic Depth & Nodes**, **Blunder Logic**, and **Advanced Time Management**, this bot mimics the thought process, inconsistencies, and even the subtle mistakes of a human player, making it nearly indistinguishable from a real person.

*   **🛡️ Advanced Anti-Detection (5-Phase System):**
    *   **Phase 1:** Browser stealth mode + Bezier curve mouse movement
    *   **Phase 2:** Exponential thinking delays with occasional "deep thought" pauses
    *   **Phase 3:** Idle actions during opponent's turn (random mouse movements, piece hovering)
    *   **Phase 4:** Randomized viewport size and zoom levels
    *   **Phase 5:** Human-like typing patterns with occasional typos and corrections

*   **📚 Dynamic Opening Book:** Never play the same opening twice. Simply drop your Polyglot (`.bin`) opening book files into the `opening_books` directory, and the bot will automatically detect and randomly choose one for each game.

*   **⚙️ Full Control at Your Fingertips:** Every engine parameter, from the **target Elo** to the level of "aggressiveness" (`Contempt`), is easily configurable through a single, well-documented `config.ini` file. You are the coach.

*   **🕹️ Full Automation:** Enable `auto_play` and let the bot handle game after game, complete with configurable, mode-dependent delays between matches to simulate a human taking a break.

*   **👻 Stealth Mode:** Run the bot in `headless` mode to hide the browser window, allowing you to focus on other tasks while the bot works in the background.

<!-- 
##  See It In Action

<div align="center">

**[YOUR-GIF-HERE]**

*Replace this with a GIF of the bot in action: logging in, selecting a mode, making moves, etc. This will dramatically increase the README's appeal.*

</div>
-->

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.8+**
- **Git**
- **Stockfish:** Already included in the `engine/` folder.

### 2. Installation

```bash
# 1. Clone this repository
git clone https://github.com/your-username/chess-from-zero.git
cd chess-from-zero

# 2. (Highly Recommended) Create and activate a virtual environment
python -m venv venv
# On Windows: .\venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# 3. Install all required dependencies
pip install -r requirements.txt
playwright install
```

### 3. Setup

1.  **Create `credentials.txt`:** In the root directory, create a file named `credentials.txt` and fill it with the following format:
    ```text
    your_chess_com_username
    your_chess_com_password
    ```

2.  **Populate `opening_books/`:** Download your desired Polyglot (`.bin`) opening book files from the internet (e.g., search for "*Baron polyglot book*" or "*Komodo opening book*") and place them into the `opening_books/` directory.

3.  **Customize `config.ini`:** Open `config.ini` and tweak the settings to match your desired playstyle. A full explanation is below.

---

## ⚙️ Full Configuration (`config.ini`)

Click on each section to expand and see a detailed explanation of every parameter.

<details>
<summary><strong>[play] - General Gameplay Settings</strong></summary>

-   `mode`: The time control to play (`Rapid`, `Blitz`, or `Bullet`).
-   `headless`: Run in the background (`true`) or show the browser (`false`).
-   `auto_move`: The bot will automatically make moves (`true`) or only highlight them (`false`).
-   `auto_play`: Automatically start a new game (`true`) or stop after one game (`false`).
-   `num_games`: Number of games to play automatically (`0` for unlimited).
-   `advanced_time_management`: Use the dynamic time management system (`true`/`false`).

</details>

<details>
<summary><strong>[opening_book] - Opening Book Settings</strong></summary>

-   `enabled`: Enable (`true`) or disable (`false`) the use of opening books.
-   `directory`: The folder where your `.bin` files are located.

</details>

<details>
<summary><strong>[delays] - Between-Game Delay Settings</strong></summary>

-   `min/max_rapid_delay_seconds`: Delay range (in seconds) after a Rapid game.
-   `min/max_blitz_delay_seconds`: Delay range (in seconds) after a Blitz game.
-   `min/max_bullet_delay_seconds`: Delay range (in seconds) after a Bullet game.

</details>

<details>
<summary><strong>[engine_settings] - Core Engine Configuration</strong></summary>

-   `UCI_LimitStrength`: Must be `true` to enable Elo-based strength limitation.
-   `UCI_Elo`: The target playing strength equivalent to this Elo rating.
-   `Skill Level`: The engine's internal skill level (0-20). Keep at `20` for the best analysis quality.
-   `Contempt`: The engine's reluctance to accept a draw. Positive values are more aggressive.
-   `Threads`: Number of CPU cores for the engine to use.
-   `Hash`: Memory (in MB) allocated for the transposition table (position cache).
-   `MultiPV`: Number of best moves to analyze (must be `>= 2` for blunder logic to work).

</details>

<details>
<summary><strong>[dynamic_depth] - Dynamic Search Depth Settings</strong></summary>

-   `opening_min/max`: Depth range for the opening phase.
-   `middlegame_min/max`: Depth range for the middlegame phase.
-   `endgame_min/max`: Depth range for the endgame phase.

</details>

<details>
<summary><strong>[nodes_limit] - Position Analysis Limit Settings</strong></summary>

-   `min/max`: The range of positions (`nodes`) to analyze per move, adding variety.

</details>

<details>
<summary><strong>[blunder_logic] - Human-like Mistake Settings</strong></summary>

-   `enabled`: Enable (`true`) or disable (`false`) this feature.
-   `max_score_diff_cp`: The maximum score difference (in centipawns) to consider making a "blunder."
-   `min/max_blunder_chance`: The probability range (e.g., `0.05` = 5%) of making a blunder if the score difference is within the limit.

</details>

<details>
<summary><strong>[human_delays] - Phase 2: Human-like Thinking Delays</strong></summary>

-   `enabled`: Enable exponential distribution for thinking time (`true`/`false`).
-   `min/max_base_thinking_time`: Base thinking time range in seconds.
-   `exponential_lambda`: Lambda parameter for exponential distribution (higher = faster decay).
-   `deep_thought_probability`: Probability of occasional long pauses (0.0-1.0).
-   `min/max_deep_thought_duration`: Duration range for deep thought pauses in seconds.

</details>

<details>
<summary><strong>[idle_actions] - Phase 3: Random Mouse Movements</strong></summary>

-   `enabled`: Enable idle actions during opponent's turn (`true`/`false`).
-   `action_probability`: Probability of performing an idle action (0.0-1.0).
-   `action_types`: Comma-separated list of action types (random_move, piece_hover, board_scan, tab_check).

</details>

<details>
<summary><strong>[viewport] - Phase 4: Viewport Randomization</strong></summary>

-   `randomize_window_size`: Randomize window size on each session (`true`/`false`).
-   `min/max_window_width`: Allowed window width range in pixels.
-   `min/max_window_height`: Allowed window height range in pixels.
-   `randomize_zoom`: Randomize viewport zoom level 90-110% (`true`/`false`).

</details>

<details>
<summary><strong>[typing_patterns] - Phase 5: Human-like Typing</strong></summary>

-   `enabled`: Enable human-like typing patterns (`true`/`false`).
-   `min/max_typing_speed_cpm`: Characters per minute range (average human speed).
-   `typo_probability`: Probability of making a typo (0.0-1.0).
-   `min/max_correction_delay`: Delay before correcting typo in seconds.

</details>

---

## 🎮 How to Run

Make sure you are in the project's root directory, then run:

```bash
python chess_assist/main.py
```

You can also override certain settings directly from the command line:

```bash
python chess_assist/main.py --mode Rapid --headless true
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository, make your changes, and open a Pull Request.

## 📄 License

This project is licensed under the MIT License.