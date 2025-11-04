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

    def get_thinking_delay(self, game_phase="middlegame", move_complexity=1.0):
        """
        Calculate human-like thinking delay using exponential distribution.

        Args:
            game_phase: Opening, middlegame, or endgame
            move_complexity: Multiplier for complex positions (1.0 = normal)

        Returns:
            Delay in seconds
        """
        if not self.enabled:
            return 0

        # Check for deep thought pause (rare but realistic)
        if random.random() < self.deep_thought_prob:
            delay = random.uniform(self.min_deep_thought, self.max_deep_thought)
            logging.info(f"Deep thought pause: {delay:.1f}s")
            return delay

        # Use exponential distribution for base thinking time
        # This creates realistic variation: many quick moves, some longer ones
        base_delay = random.uniform(self.min_base_thinking, self.max_base_thinking)

        # Apply exponential curve (creates natural human-like distribution)
        exponential_factor = np.random.exponential(1.0 / self.exponential_lambda)
        delay = base_delay * exponential_factor

        # Adjust based on game phase
        phase_multipliers = {
            "opening": 0.7,      # Faster in opening (theory moves)
            "middlegame": 1.2,   # Longer in middlegame (tactical)
            "endgame": 1.0       # Normal in endgame
        }
        delay *= phase_multipliers.get(game_phase, 1.0)

        # Apply complexity multiplier
        delay *= move_complexity

        # Clamp to reasonable bounds (1-60 seconds)
        delay = max(1.0, min(60.0, delay))

        logging.debug(f"Calculated thinking delay: {delay:.2f}s (phase: {game_phase}, complexity: {move_complexity:.1f})")
        return delay

    def apply_thinking_delay(self, game_phase="middlegame", move_complexity=1.0):
        """
        Apply the calculated thinking delay with micro-variations.

        Args:
            game_phase: Current game phase
            move_complexity: Position complexity multiplier
        """
        if not self.enabled:
            return

        delay = self.get_thinking_delay(game_phase, move_complexity)

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

    def get_first_move_delay(self):
        """
        Special delay for the very first move (usually faster).

        Returns:
            Delay in seconds
        """
        if not self.enabled:
            return random.uniform(1, 3)

        # First moves are typically faster (opening theory)
        return random.uniform(1.5, 4.0)

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
