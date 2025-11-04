# Quick Start Guide

Get Chess From Zero running in 5 minutes!

---

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ Chess.com account
- ✅ Internet connection

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "Chess From Zero"

# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**Expected output**: All packages install successfully, including:
- playwright
- python-chess
- configparser
- numpy

---

## Step 2: Configure Credentials

Create or edit `credentials.txt` in the project root:

```txt
your_chess_com_username
your_chess_com_password
```

⚠️ **Important**: Keep this file private! Add to `.gitignore` if committing to git.

---

## Step 3: Configure Settings (Optional)

Edit `config.ini` to customize:

### For Testing (Safe Mode):
```ini
[play]
mode = Blitz
headless = false          # See the browser
auto_move = true
auto_play = false         # Stop after 1 game
num_games = 1

[engine_settings]
UCI_Elo = 1350           # Casual player strength
```

### For Normal Use:
```ini
[play]
mode = Blitz
headless = true          # Hide browser
auto_move = true
auto_play = true
num_games = 5            # Play 5 games per session

[engine_settings]
UCI_Elo = 1400
```

---

## Step 4: Run the Bot

### Basic Run:
```bash
python chess_assist/main.py
```

### With Debug Logging:
```bash
python chess_assist/main.py --debug
```

### Override Mode:
```bash
python chess_assist/main.py --mode Rapid
```

---

## Step 5: Verify All Phases Are Active

When the bot starts, check the logs for:

```
✓ Browser started with anti-detection features enabled
✓ Randomized window size: 1680x945
✓ Human delays module initialized with exponential distribution
✓ Idle actions enabled: ['random_move', 'piece_hover', 'board_scan']
✓ Human typing enabled: 180.0-350.0 CPM
```

If you see all these messages, all 5 phases are active!

---

## What You Should See

### Phase 1 (Browser Stealth + Bezier Mouse):
- Smooth, curved mouse movements
- Occasional overshoots and corrections
- Natural hand "shake" jitter

### Phase 2 (Thinking Delays):
- Variable thinking time (2-45 seconds)
- Occasional long pauses (deep thought)
- Faster moves in opening, slower in middlegame

### Phase 3 (Idle Actions):
- Mouse movements during opponent's turn
- Hovering over pieces
- Board scanning patterns

### Phase 4 (Viewport):
- Different window size each session
- Slight zoom variation

### Phase 5 (Typing):
- Character-by-character login typing
- Occasional typos with corrections
- Natural pauses between fields

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'src'`
**Solution**: Already fixed! Make sure you pulled the latest commit.

### Error: `playwright._impl._api_types.Error: Playwright executable not found`
**Solution**:
```bash
playwright install chromium
```

### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'credentials.txt'`
**Solution**: Create `credentials.txt` with your Chess.com credentials.

### Bot moves instantly (no delays)
**Solution**: Check `config.ini`:
```ini
[human_delays]
enabled = true    # Make sure this is true
```

### Bot doesn't type credentials naturally
**Solution**: Check `config.ini`:
```ini
[typing_patterns]
enabled = true    # Make sure this is true
```

### Numpy import error
**Solution**:
```bash
pip install numpy
```

---

## Configuration Tips

### Ultra-Safe Mode (Recommended for First Use)
```ini
[play]
mode = Blitz
auto_play = false
num_games = 1

[engine_settings]
UCI_Elo = 1320

[blunder_logic]
enabled = true
min_blunder_chance = 0.20
max_blunder_chance = 0.60

[human_delays]
enabled = true
deep_thought_probability = 0.12
```

### Normal Mode
```ini
[play]
mode = Blitz
auto_play = true
num_games = 3

[engine_settings]
UCI_Elo = 1400

[human_delays]
enabled = true
deep_thought_probability = 0.08
```

### Advanced Mode (Experienced Users)
```ini
[play]
mode = Rapid
auto_play = true
num_games = 5

[engine_settings]
UCI_Elo = 1600

[blunder_logic]
enabled = true
min_blunder_chance = 0.05
max_blunder_chance = 0.30
```

---

## Command Line Options

```bash
# Show help
python chess_assist/main.py --help

# Run with specific mode
python chess_assist/main.py --mode Rapid

# Run with debug logging
python chess_assist/main.py --debug

# Combine options
python chess_assist/main.py --mode Bullet --debug
```

---

## Safety Checklist

Before each session, verify:
- ✅ All 5 phases enabled in config.ini
- ✅ Reasonable UCI_Elo (1300-1600)
- ✅ Blunder logic enabled
- ✅ Limited games per session (3-5)
- ✅ Long delays between games (30-90s)
- ✅ Not running 24/7

---

## Usage Patterns

### Recommended:
- ✅ 3-5 games per session
- ✅ 1-2 sessions per day
- ✅ Vary the times you play
- ✅ Take breaks between sessions
- ✅ Change Elo occasionally

### Avoid:
- ❌ Playing 24/7
- ❌ Always same time of day
- ❌ Too many games per session (>10)
- ❌ Perfect play (disable blunders)
- ❌ Same config always

---

## Monitoring

Watch the logs for:
- `Performing idle action: ...` - Phase 3 working
- `Calculated thinking delay: X.XXs` - Phase 2 working
- `Human-like drag from ...` - Phase 1 working
- `Typed '...' with human-like pattern` - Phase 5 working
- `Randomized window size: ...` - Phase 4 working

---

## Next Steps

After successful testing:
1. ✅ Read [ANTI_DETECTION.md](ANTI_DETECTION.md) for technical details
2. ✅ Review [README.md](README.md) for full configuration options
3. ✅ Adjust config.ini to your preferences
4. ✅ Set up opening books (optional)
5. ✅ Start with conservative settings

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run with `--debug` flag for detailed logs
3. Review [ANTI_DETECTION.md](ANTI_DETECTION.md)
4. Check git issues

---

## Example Session

```bash
$ python chess_assist/main.py --debug

2025-01-04 10:30:15 - INFO - Browser started with anti-detection features enabled
2025-01-04 10:30:15 - INFO - Randomized window size: 1536x864
2025-01-04 10:30:15 - INFO - Human delays module initialized
2025-01-04 10:30:15 - INFO - Idle actions enabled: ['random_move', 'piece_hover', 'board_scan']
2025-01-04 10:30:15 - INFO - Human typing enabled: 180.0-350.0 CPM
2025-01-04 10:30:16 - DEBUG - Logging in...
2025-01-04 10:30:18 - DEBUG - Typed 'username' with human-like pattern
2025-01-04 10:30:20 - DEBUG - Typed '********' with human-like pattern
2025-01-04 10:30:21 - INFO - Login successful
2025-01-04 10:30:22 - INFO - Selecting mode: Blitz
2025-01-04 10:30:25 - INFO - Playing as WHITE
2025-01-04 10:30:27 - INFO - First move delay: 2.8s
2025-01-04 10:30:30 - DEBUG - Human-like drag from e2 to e4
...
```

---

**You're all set! Happy chess playing! ♟️**
