# Anti-Detection System Architecture

This document details the 5-phase anti-detection system implemented in Chess From Zero to make the bot indistinguishable from human players.

---

## Overview

The anti-detection system uses a layered approach to mimic human behavior at multiple levels:
- **Browser Level**: Stealth mode, fingerprint randomization
- **Interaction Level**: Mouse movements, typing patterns
- **Behavioral Level**: Thinking delays, idle actions

---

## Phase 1: Browser Stealth + Bezier Mouse Movement

### Browser Stealth
**Location**: [src/browser.py](src/browser.py#L60-L95)

Implements comprehensive browser anti-detection:
- Removes `navigator.webdriver` property
- Spoofs Chrome user agent
- Adds realistic plugin array
- Implements chrome runtime object
- Overrides permissions API

### Bezier Curve Mouse Movement
**Location**: [src/automove.py](src/automove.py#L16-L82)

Uses cubic Bezier curves for natural mouse movement:
- Dynamic step calculation based on distance
- Randomized control points for curve variation
- Micro-jitter simulation (human hand shake)
- Variable speed (slower at endpoints, faster in middle)
- 15% chance of overshoot + correction

**Mathematical Model**:
```python
# Cubic Bezier: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
x = ((1-t)**3 * from_x +
     3*(1-t)**2*t * control_x1 +
     3*(1-t)*t**2 * control_x2 +
     t**3 * to_x)
```

---

## Phase 2: Human-like Thinking Delays

**Location**: [src/human_delays.py](src/human_delays.py)

### Exponential Distribution
Uses exponential distribution to model realistic thinking patterns:

```python
delay = base_delay * np.random.exponential(1.0 / lambda)
```

This creates a distribution where:
- **Many moves**: Quick (2-5 seconds)
- **Some moves**: Medium (5-15 seconds)
- **Few moves**: Long (15-30 seconds)
- **Rare**: Deep thought (15-45 seconds)

### Phase Multipliers
- **Opening**: 0.7x (faster, theory moves)
- **Middlegame**: 1.2x (slower, tactical complexity)
- **Endgame**: 1.0x (normal calculation)

### Complexity Adjustments
```python
move_complexity = 1.0
if num_legal_moves > 30: complexity = 1.5  # Complex
elif num_legal_moves < 10: complexity = 0.8  # Simple
```

### Configuration
```ini
[human_delays]
enabled = true
min_base_thinking_time = 2.0
max_base_thinking_time = 8.0
exponential_lambda = 0.5
deep_thought_probability = 0.08
min_deep_thought_duration = 15.0
max_deep_thought_duration = 45.0
```

---

## Phase 3: Idle Actions During Opponent's Turn

**Location**: [src/idle_actions.py](src/idle_actions.py)

Simulates human behavior while waiting for opponent:

### Action Types

1. **Random Mouse Movement** (25% probability)
   - Moves mouse to random screen position
   - Simulates looking away or checking other tabs

2. **Piece Hovering** (25% probability)
   - Hovers over random pieces
   - Simulates analyzing position

3. **Board Scanning** (25% probability)
   - Sweeps mouse across board in patterns:
     - Diagonal (a1→h8)
     - Horizontal (entire rank)
     - Vertical (entire file)
   - Visits 3-5 squares along path

4. **Tab Checking** (optional)
   - Moves mouse to top tab area
   - Pauses 1-3 seconds
   - Returns to board

### Configuration
```ini
[idle_actions]
enabled = true
action_probability = 0.25
action_types = random_move,piece_hover,board_scan
```

---

## Phase 4: Viewport Randomization

**Location**: [src/browser.py](src/browser.py#L20-L57)

Prevents browser fingerprinting through viewport diversity:

### Window Size Randomization
Each session gets unique window dimensions:
- **Width**: 1366-1920 pixels
- **Height**: 768-1080 pixels

Common resolutions included:
- 1366x768 (most common laptop)
- 1440x900
- 1536x864
- 1600x900
- 1920x1080 (Full HD)

### Zoom Level Randomization
Random zoom between 90-110%:
```python
zoom_level = random.uniform(0.9, 1.1)
document.body.style.zoom = zoom_level
```

This creates unique visual fingerprints for each session.

### Configuration
```ini
[viewport]
randomize_window_size = true
min_window_width = 1366
max_window_width = 1920
min_window_height = 768
max_window_height = 1080
randomize_zoom = true
```

---

## Phase 5: Human-like Typing Patterns

**Location**: [src/human_typing.py](src/human_typing.py)

Simulates realistic typing during login and interactions:

### Variable Typing Speed
Based on human typing research:
- **Slow typist**: 180 CPM (3 chars/sec)
- **Average typist**: 250 CPM (4.2 chars/sec)
- **Fast typist**: 350 CPM (5.8 chars/sec)

```python
delay = 60.0 / random.uniform(min_cpm, max_cpm)
```

### Typo Simulation (5% probability)
When typo occurs:
1. Type adjacent key from QWERTY layout
2. Pause (realize mistake): 0.3-1.2s
3. Backspace to delete
4. Type correct character

**QWERTY Adjacency Map**:
```python
keyboard_layout = {
    'q': ['w', 'a'],
    'w': ['q', 'e', 's'],
    'e': ['w', 'r', 'd'],
    # ... etc
}
```

### Natural Pauses
- **Between characters**: Variable (±30% from base)
- **Occasional long pause**: +0.3-1.0s (5% chance)
- **After typing**: 0.2-0.6s before submit

### Configuration
```ini
[typing_patterns]
enabled = true
min_typing_speed_cpm = 180
max_typing_speed_cpm = 350
typo_probability = 0.05
min_correction_delay = 0.3
max_correction_delay = 1.2
```

---

## Integration Points

All phases integrate seamlessly into the game flow:

### Login Flow
```python
# Phase 5: Human typing
browser.human_typing.type_text(page, username_field, username)
browser.human_typing.pause_before_action(0.3, 0.8)
browser.human_typing.type_text(page, password_field, password)
```

### Move Execution Flow
```python
# Phase 2: Thinking delay
game.human_delays.apply_thinking_delay(game_phase, move_complexity)

# Phase 1: Bezier mouse movement
automove.execute_move(best_move)
```

### Opponent Turn Flow
```python
# Phase 3: Idle actions
while waiting_for_opponent:
    game.idle_actions.perform_idle_action()
```

---

## Safety Recommendations

For maximum safety and human-like behavior:

1. **Enable ALL phases** in config.ini
2. **Use moderate settings**:
   - UCI_Elo: 1300-1500 (casual player range)
   - Blunder enabled with 10-60% chance
   - Deep thought probability: 5-10%

3. **Limit play sessions**:
   - num_games: 2-5 per session
   - Long delays between games (60-120s)
   - Take breaks between sessions

4. **Vary your settings**:
   - Change Elo target occasionally
   - Use different opening books
   - Adjust thinking time ranges

---

## Performance Impact

| Phase | CPU Impact | Memory Impact | Delay Added |
|-------|-----------|---------------|-------------|
| Phase 1 | Low | Negligible | 0.5-2s per move |
| Phase 2 | Negligible | Negligible | 2-45s per move |
| Phase 3 | Low | Negligible | 0-3s per wait |
| Phase 4 | Negligible | Negligible | One-time |
| Phase 5 | Negligible | Negligible | 2-10s per login |

**Total overhead**: Minimal - the delays are intentional and create the human-like behavior.

---

## Detection Resistance Analysis

### What We Defeat

✅ **Bot Detection Systems**:
- Webdriver detection (Phase 1)
- Mouse movement analysis (Phase 1)
- Timing pattern analysis (Phase 2)
- Browser fingerprinting (Phase 4)
- Typing pattern analysis (Phase 5)

✅ **Behavioral Analysis**:
- Perfect play detection (Blunder Logic + Elo limiting)
- Consistent timing detection (Phase 2: Exponential distribution)
- Inhuman precision (Phase 1: Bezier curves + jitter)
- Idle behavior analysis (Phase 3)

✅ **Statistical Outliers**:
- Always same thinking time (Phase 2: Exponential)
- Instant moves (Phase 2: First move delays)
- Perfect mouse paths (Phase 1: Bezier + overshoot)
- No idle movements (Phase 3)

### Best Practices

1. **Never use the same config for extended periods**
2. **Randomize between sessions**:
   - Change Elo target
   - Adjust delay ranges
   - Vary blunder probability

3. **Natural usage patterns**:
   - Don't play 24/7
   - Take breaks
   - Vary game modes

4. **Monitor and adapt**:
   - Check account status regularly
   - Adjust if warnings occur
   - Use conservative settings initially

---

## Testing the System

To verify all phases are working:

```bash
# Test imports
python -c "from src.human_delays import HumanDelays; from src.idle_actions import IdleActions; from src.human_typing import HumanTyping; print('All modules OK')"

# Run with verbose logging
python chess_assist/main.py --mode Rapid

# Check logs for:
# - "Human delays module initialized"
# - "Idle actions enabled"
# - "Human typing enabled"
# - "Randomized window size"
# - "Performing idle action"
# - "Calculated thinking delay"
```

---

## Future Enhancements

Potential additions for even better stealth:

- **Session fingerprinting**: Unique patterns per session
- **Learning behavior**: Adapt to opponent's style
- **Chat interactions**: Random chat messages
- **Time of day patterns**: Play slower when "tired"
- **Emotional variance**: Faster moves when winning/losing
- **Browser history simulation**: Navigate to chess resources
- **Cookie management**: Realistic browser state

---

## Credits

This anti-detection system combines techniques from:
- Browser automation research
- Human-computer interaction studies
- Behavioral analysis literature
- Real player timing data analysis

Built with love using Python, Playwright, and Stockfish.
