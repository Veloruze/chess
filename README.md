# ♟️ Chess From Zero

**An advanced AI-powered Chess.com bot with human-like behavior and anti-detection capabilities**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://shields.io/)

---

## ⚡ Features

### 🤖 Intelligent Gameplay
- **Stockfish Engine**: Powered by the world's strongest chess engine
- **Dynamic Elo Rating**: Configure target playing strength (800-3000 Elo)
- **Opening Book Support**: Polyglot (`.bin`) format with random selection
- **Blunder Logic**: Intentional mistakes to simulate human imperfection
- **Dynamic Depth & Nodes**: Adaptive analysis based on game phase

### 🛡️ 5-Phase Anti-Detection System

| Phase | Feature | Description |
|-------|---------|-------------|
| **1** | Browser Stealth | Playwright stealth mode + Bezier curve mouse movement |
| **2** | Human Delays | Exponential thinking time with occasional deep thought pauses |
| **3** | Idle Actions | Random mouse movements during opponent's turn |
| **4** | Viewport Randomization | Randomized window size (1366-1920px) and zoom (90-110%) |
| **5** | Human Typing | Variable typing speed (180-350 CPM) with typos |

### ⏱️ Time Management

**Adaptive delays based on game mode and remaining time:**

#### Bullet Mode (1 minute)
- Normal: 0.5-1.5s thinking time
- Time pressure (<60s): Instant moves (0.1-0.3s)
- Fast mouse mode: Linear movement (0.03s vs 1.5s)

#### Blitz Mode (3 minutes)
- Normal: 0.5-4.0s thinking time
- Time pressure (<60s): Fast moves (0.3-0.8s)
- Deep thought: Rare (1.5% chance, max 6s)

#### Rapid Mode (10+ minutes)
- Normal: 0.5-15s thinking time
- Deep thought: 5% chance, up to 30s
- Full human-like delays enabled

### 🎯 Automation
- **Auto-play**: Continuous game mode with configurable delays
- **Headless Mode**: Run browser in background
- **Auto-move**: Automatic piece movement
- **Game Loop**: Handles game-over modal and restarts automatically

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Git**
- **Internet connection**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Veloruze/chess.git
cd chess

# 2. Create virtual environment (recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Setup

1. **Create credentials file** (`credentials.txt` in root directory):
```text
your_chess_com_username
your_chess_com_password
```

2. **Add opening books** (optional):
   - Download Polyglot `.bin` files
   - Place them in `opening_books/` directory
   - Bot will randomly select one per game

3. **Configure settings** (edit `config.ini`):
```ini
[play]
mode = Blitz              # Bullet, Blitz, or Rapid
headless = false          # true = background, false = visible
auto_move = true          # Automatic piece movement
auto_play = true          # Play multiple games
num_games = 0             # 0 = unlimited

[engine_settings]
UCI_Elo = 1500           # Target playing strength (800-3000)
```

### Run

```bash
python chess_assist/main.py
```

---

## ⚙️ Configuration Guide

### Game Settings (`[play]`)

| Parameter | Values | Description |
|-----------|--------|-------------|
| `mode` | `Bullet`, `Blitz`, `Rapid` | Time control mode |
| `headless` | `true`, `false` | Run browser in background |
| `auto_move` | `true`, `false` | Automatic piece movement |
| `auto_play` | `true`, `false` | Play multiple games |
| `num_games` | `0-999` | Number of games (0 = unlimited) |
| `advanced_time_management` | `true`, `false` | Dynamic time allocation |

### Engine Settings (`[engine_settings]`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `UCI_LimitStrength` | `true` | Enable Elo-based strength |
| `UCI_Elo` | `1500` | Target Elo rating (800-3000) |
| `Skill Level` | `20` | Stockfish skill (0-20) |
| `Contempt` | `10` | Draw reluctance (-100 to 100) |
| `Threads` | `4` | CPU cores to use |
| `Hash` | `128` | Memory in MB (16-4096) |
| `MultiPV` | `3` | Lines to analyze (≥2 for blunders) |

### Dynamic Depth (`[dynamic_depth]`)

Search depth adjusts by game phase:

| Phase | Min Depth | Max Depth | Description |
|-------|-----------|-----------|-------------|
| Opening | 8 | 12 | Book moves + tactical awareness |
| Middlegame | 10 | 15 | Full analysis, complex tactics |
| Endgame | 12 | 18 | Precise calculation required |

### Blunder Logic (`[blunder_logic]`)

Simulate human mistakes:

```ini
enabled = true
max_score_diff_cp = 100          # Max centipawn loss
min_blunder_chance = 0.05        # 5% minimum probability
max_blunder_chance = 0.15        # 15% maximum probability
```

**How it works:**
- Analyzes top 3 moves (requires `MultiPV ≥ 2`)
- Randomly chooses suboptimal move 5-15% of the time
- Only if score difference < 100 centipawns (1 pawn)

### Human Delays (`[human_delays]`)

Exponential distribution for realistic thinking:

```ini
enabled = true
min_base_thinking_time = 0.5     # Minimum delay (seconds)
max_base_thinking_time = 2.5     # Maximum delay (seconds)
exponential_lambda = 0.7         # Distribution shape
deep_thought_probability = 0.05  # 5% chance of long pause
```

**Mode-specific limits:**
- Bullet: Max 1.5s normal, 2.5s deep thought
- Blitz: Max 4.0s normal, 6.0s deep thought
- Rapid: Max 15s normal, 30s deep thought

### Idle Actions (`[idle_actions]`)

Random mouse movement during opponent's turn:

```ini
enabled = true
action_probability = 0.25              # 25% chance per turn
action_types = random_move,piece_hover,board_scan
```

### Between-Game Delays (`[delays]`)

Delays before starting next game:

```ini
min_rapid_delay_seconds = 15
max_rapid_delay_seconds = 45
min_blitz_delay_seconds = 10
max_blitz_delay_seconds = 30
min_bullet_delay_seconds = 5
max_bullet_delay_seconds = 15
```

---

## 📊 Performance Optimization

### Time Pressure Handling

When remaining time < 60 seconds:

1. **Instant thinking** (0.1-0.8s based on urgency)
2. **Fast mouse mode** enabled:
   - Normal: 30 steps, 50ms delay = 1.5s
   - Fast: 5 steps, 2ms delay = 0.03s (**98% faster**)
3. **No deep thought pauses**

When remaining time < 30 seconds:
- Ultra-fast moves (0.1-0.3s)
- Minimal mouse animation

### Time Format Parsing

Chess.com uses two formats:

| Time Remaining | Format | Example | Parsing |
|----------------|--------|---------|---------|
| > 20 seconds | `mm:ss` | `0:59`, `1:30` | Split by `:` |
| < 20 seconds | `ss.d` | `19.2`, `01.4` | Parse float, strip leading zeros |

---

## 🐛 Troubleshooting

### Common Issues

**1. Module Import Error**
```
ModuleNotFoundError: No module named 'src'
```
**Solution:** This is already fixed. Make sure you're running the latest version.

**2. Play Button Not Found**
```
Exception: Play button not found
```
**Solution:** Updated to use `data-cy='new-game-index-play'`. Pull latest changes.

**3. Timeout in Blitz Games**
**Solution:** Delays are optimized for each mode. Ensure `advanced_time_management = true` in config.

**4. "Play a Friend" Instead of Online Mode**
**Solution:** Fixed - bot now explicitly selects "Online" mode before starting.

**5. Invalid Time Format**
```
invalid literal for int() with base 10: '01.4'
```
**Solution:** Already fixed - handles leading zeros in time format.

### Debug Mode

Enable detailed logging:

```bash
# Windows
set PYTHONUNBUFFERED=1
python chess_assist/main.py

# Linux/macOS
PYTHONUNBUFFERED=1 python chess_assist/main.py
```

Check log files in project root for detailed error traces.

---

## 🏗️ Project Structure

```
chess-from-zero/
├── chess_assist/
│   └── main.py              # Entry point
├── src/
│   ├── browser.py           # Playwright automation + stealth
│   ├── game.py              # Game logic + time management
│   ├── engine.py            # Stockfish interface
│   ├── automove.py          # Mouse movement (Bezier curves)
│   ├── human_delays.py      # Phase 2: Thinking delays
│   ├── human_typing.py      # Phase 5: Typing patterns
│   ├── idle_actions.py      # Phase 3: Mouse movements
│   ├── selectors.py         # CSS selectors for Chess.com
│   └── utils.py             # Helper functions
├── engine/
│   └── stockfish.exe        # Chess engine
├── opening_books/           # Polyglot .bin files
├── config.ini               # Main configuration
├── credentials.txt          # Chess.com login (gitignored)
└── requirements.txt         # Python dependencies
```

---

## 🔒 Security & Ethics

### ⚠️ Disclaimer

This project is for **educational purposes only**. Using automated bots on Chess.com violates their [Terms of Service](https://www.chess.com/legal/user-agreement) and may result in:
- Account suspension
- Permanent ban
- Rating/title revocation

**Use at your own risk.** The developers assume no responsibility for account penalties.

### Responsible Use

If you choose to use this bot:
1. **Never use on your main account**
2. **Don't use in rated games** (practice only)
3. **Respect fair play guidelines**
4. **Don't ruin the experience for others**

The purpose of this project is to demonstrate:
- Browser automation techniques
- Anti-detection strategies
- Chess engine integration
- Human behavior simulation

---

## 🛠️ Advanced Usage

### Custom Elo Curve

For more realistic progression, modify `UCI_Elo` over time:

```python
# In main.py
game_number = 1
base_elo = 1200

for game in range(10):
    current_elo = base_elo + (game_number * 25)  # +25 Elo per game
    config.set('engine_settings', 'UCI_Elo', str(current_elo))
    # ... play game
    game_number += 1
```

### Conditional Blunders

Increase blunder rate when winning:

```python
# In game.py
if score > 200:  # Winning by 2 pawns
    blunder_chance *= 2  # Double the mistake rate
```

### Custom Opening Repertoire

Organize books by color/opening:

```
opening_books/
├── white_e4/
│   ├── italian.bin
│   └── spanish.bin
├── white_d4/
│   └── queens_gambit.bin
└── black/
    ├── sicilian.bin
    └── french.bin
```

---

## 📈 Recent Updates

### v1.2.0 (2025-11-04)
- ✅ Fixed time parsing for formats with leading zeros (`01.4`)
- ✅ Optimized auto-play loop (skip mode selection for game 2+)
- ✅ Updated selectors for "Start Game" and "New Game" buttons
- ✅ Removed unnecessary selector fallbacks for cleaner code

### v1.1.0 (2025-11-04)
- ✅ Implemented fast mouse mode for time pressure (<60s)
- ✅ Fixed double delay issue (thinking + mouse animation)
- ✅ Added Chess.com dual time format support (<20s vs >20s)
- ✅ Optimized delays for Bullet/Blitz/Rapid modes

### v1.0.0 (2025-11-03)
- ✅ Complete 5-phase anti-detection system
- ✅ Human-like delays with exponential distribution
- ✅ Idle actions during opponent's turn
- ✅ Viewport randomization
- ✅ Human typing patterns with typos

---

## 🤝 Contributing

Contributions welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black src/ chess_assist/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Stockfish](https://stockfishchess.org/)** - The world's strongest chess engine
- **[Playwright](https://playwright.dev/)** - Reliable browser automation
- **[python-chess](https://python-chess.readthedocs.io/)** - Chess library for Python

---

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/Veloruze/chess/issues)
- **Discussions**: [Ask questions](https://github.com/Veloruze/chess/discussions)

---

<div align="center">

**Made with ♟️ by [Veloruze](https://github.com/Veloruze)**

*If you found this useful, give it a ⭐!*

</div>
