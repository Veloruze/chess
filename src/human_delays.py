"""
Phase 2: Human-like Thinking Delays
Implements exponential distribution for realistic thinking patterns
"""
import logging
import random
import time
import numpy as np


class HumanDelays:
    """
    Manages human-like thinking delays with exponential distribution
    and occasional deep thought pauses.
    """

    def __init__(self, config):
        self.config = config
        self.enabled = config.getboolean("human_delays", "enabled", fallback=False)

        if self.enabled:
            self.min_base_thinking = config.getfloat("human_delays", "min_base_thinking_time", fallback=2.0)
            self.max_base_thinking = config.getfloat("human_delays", "max_base_thinking_time", fallback=8.0)
            self.exponential_lambda = config.getfloat("human_delays", "exponential_lambda", fallback=0.5)
            self.deep_thought_prob = config.getfloat("human_delays", "deep_thought_probability", fallback=0.08)
            self.min_deep_thought = config.getfloat("human_delays", "min_deep_thought_duration", fallback=15.0)
            self.max_deep_thought = config.getfloat("human_delays", "max_deep_thought_duration", fallback=45.0)

            logging.info("Human delays module initialized with exponential distribution")

    def get_thinking_delay(self, game_phase="middlegame", move_complexity=1.0, game_mode="Blitz"):
        """
        Calculate human-like thinking delay using exponential distribution.

        Args:
            game_phase: Opening, middlegame, or endgame
            move_complexity: Multiplier for complex positions (1.0 = normal)
            game_mode: Game mode (Bullet, Blitz, Rapid) for time-appropriate delays

        Returns:
            Delay in seconds
        """
        if not self.enabled:
            return 0

        # Define maximum delays based on game mode (OPTIMIZED FOR SPEED)
        mode_limits = {
            "Bullet": {"max": 1.5, "deep_thought_max": 2.5},   # 1 min games - ULTRA FAST
            "Blitz": {"max": 4.0, "deep_thought_max": 6.0},    # 3 min games - fast play
            "Rapid": {"max": 15.0, "deep_thought_max": 30.0}   # 10+ min games - normal thinking
        }

        limits = mode_limits.get(game_mode, mode_limits["Blitz"])

        # Check for deep thought pause (rare but realistic)
        # Probability reduced for faster time controls
        deep_thought_prob = self.deep_thought_prob
        if game_mode == "Bullet":
            deep_thought_prob *= 0.1  # Very rare in bullet (0.8%)
        elif game_mode == "Blitz":
            deep_thought_prob *= 0.3  # Less frequent in blitz (2.4%)

        if random.random() < deep_thought_prob:
            # Use mode-appropriate deep thought duration
            delay = random.uniform(
                limits["max"] * 0.5,  # At least half of max
                limits["deep_thought_max"]
            )
            logging.info(f"Deep thought pause: {delay:.1f}s (mode: {game_mode})")
            return delay

        # Use exponential distribution for base thinking time
        # This creates realistic variation: many quick moves, some longer ones
        base_delay = random.uniform(self.min_base_thinking, self.max_base_thinking)

        # Apply exponential curve (creates natural human-like distribution)
        exponential_factor = np.random.exponential(1.0 / self.exponential_lambda)
        delay = base_delay * exponential_factor

        # Adjust based on game phase
        phase_multipliers = {
            "opening": 0.5,      # Much faster in opening (theory moves)
            "middlegame": 1.0,   # Normal in middlegame (tactical)
            "endgame": 0.8       # Faster in endgame (fewer pieces)
        }
        delay *= phase_multipliers.get(game_phase, 1.0)

        # Apply complexity multiplier
        delay *= move_complexity

        # Clamp to mode-appropriate bounds
        min_delay = 0.5 if game_mode != "Bullet" else 0.3
        delay = max(min_delay, min(limits["max"], delay))

        logging.debug(f"Calculated thinking delay: {delay:.2f}s (mode: {game_mode}, phase: {game_phase}, complexity: {move_complexity:.1f})")
        return delay

    def apply_thinking_delay(self, game_phase="middlegame", move_complexity=1.0, game_mode="Blitz"):
        """
        Apply the calculated thinking delay with micro-variations.

        Args:
            game_phase: Current game phase
            move_complexity: Position complexity multiplier
            game_mode: Game mode for time-appropriate delays
        """
        if not self.enabled:
            return

        delay = self.get_thinking_delay(game_phase, move_complexity, game_mode)

        # Split delay into chunks to simulate human "thinking process"
        # e.g., look at board, think, check clock, think more
        chunks = random.randint(2, 5)
        for i in range(chunks):
            chunk_delay = delay / chunks
            # Add micro-variation to each chunk
            actual_chunk = chunk_delay * random.uniform(0.8, 1.2)
            time.sleep(actual_chunk)

            # Small micro-pauses between thinking chunks (0.1-0.5s)
            if i < chunks - 1:
                time.sleep(random.uniform(0.1, 0.5))

    def get_first_move_delay(self, game_mode="Blitz"):
        """
        Special delay for the very first move (usually faster).

        Args:
            game_mode: Game mode to determine appropriate first move delay

        Returns:
            Delay in seconds
        """
        if not self.enabled:
            return random.uniform(1, 3)

        # First moves are typically faster (opening theory)
        # Mode-specific delays
        if game_mode == "Bullet":
            return random.uniform(0.5, 1.5)  # Very fast in Bullet
        elif game_mode == "Blitz":
            return random.uniform(1.0, 2.5)  # Fast in Blitz
        else:  # Rapid
            return random.uniform(1.5, 4.0)  # Normal in Rapid

    def get_premove_delay(self):
        """
        Delay for positions where a premove might occur.
        Very short delay simulating instant response.

        Returns:
            Delay in seconds
        """
        if not self.enabled:
            return 0.5

        # Occasional instant premove (10% chance)
        if random.random() < 0.10:
            return random.uniform(0.1, 0.3)

        # Normal quick response
        return random.uniform(0.5, 2.0)
