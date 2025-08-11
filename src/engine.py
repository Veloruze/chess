
import chess
import chess.engine
import logging

def _parse_config_value(value_str):
    """
    Parses a config string that might contain a comment (e.g., 'value ; comment').
    Returns the value before the first semicolon or hash, stripped of whitespace.
    """
    if ';' in value_str:
        value_str = value_str.split(';')[0]
    if '#' in value_str:
        value_str = value_str.split('#')[0]
    return value_str.strip()

import random

class StockfishEngine:
    """
    A wrapper for the Stockfish chess engine.
    """
    def __init__(self, config):
        self.config = config
        self.engine = chess.engine.SimpleEngine.popen_uci("engine/stockfish.exe")
        
        engine_settings = {}
        if self.config.has_section("engine_settings"):
            for name, value in self.config.items("engine_settings"):
                # Correctly handle boolean and integer types from config
                if value.lower() in ["true", "false"]:
                    engine_settings[name] = self.config.getboolean("engine_settings", name)
                elif value.isdigit():
                    engine_settings[name] = self.config.getint("engine_settings", name)
                else:
                    engine_settings[name] = _parse_config_value(value)
        
        if engine_settings:
            # configparser lowercases all option names, so we need to handle case-sensitive options manually.
            # Set MultiPV, which is required for blunder logic.
            if 'multipv' in engine_settings:
                try:
                    self.engine.options["MultiPV"] = int(engine_settings['multipv'])
                    del engine_settings['multipv'] # Remove it so we don't try to configure it again
                except Exception as e:
                    logging.error(f"Failed to set MultiPV option: {e}")

            # The rest of the options are passed to configure.
            # Note: configure is case-insensitive for option names.
            if engine_settings:
                self.engine.configure(engine_settings)
                logging.info(f"Engine configured with: {engine_settings}")

    def get_best_move(self, board, game_phase="middlegame"):
        """
        Gets the best move from the engine with dynamic depth, nodes limit, and blunder logic from config.
        """
        # 1. Dynamic Depth from config
        depth_min = self.config.getint("dynamic_depth", f"{game_phase}_min", fallback=10)
        depth_max = self.config.getint("dynamic_depth", f"{game_phase}_max", fallback=15)
        depth = random.randint(depth_min, depth_max)

        # 2. Nodes Limit from config
        nodes_min = self.config.getint("nodes_limit", "min", fallback=2000000)
        nodes_max = self.config.getint("nodes_limit", "max", fallback=8000000)
        nodes = random.randint(nodes_min, nodes_max)

        limit = chess.engine.Limit(depth=depth, nodes=nodes)

        # 3. Get top moves (MultiPV is now set in __init__)
        try:
            info = self.engine.analyse(board, limit=limit)
        except Exception as e:
            logging.error(f"Engine analysis failed: {e}. Falling back to simpler search.")
            info = self.engine.analyse(board, limit=chess.engine.Limit(depth=10))

        if not info:
            logging.error("Engine analysis failed completely.")
            return None, []

        # Ensure info is a list, as it can be a single dict if MultiPV=1
        if isinstance(info, dict):
            info = [info]

        # Sort moves by score
        moves_with_scores = []
        for pv in info:
            if "pv" in pv and pv["pv"]:
                move = pv["pv"][0]
                score = pv["score"].white().score(mate_score=10000)
                moves_with_scores.append((move, score))

        is_black_turn = not board.turn
        moves_with_scores.sort(key=lambda x: x[1], reverse=not is_black_turn)

        if not moves_with_scores:
            logging.error("Engine returned no moves.")
            return None, []

        best_move = moves_with_scores[0][0]
        
        # 4. Blunder Logic from config
        if self.config.getboolean("blunder_logic", "enabled") and len(moves_with_scores) > 1:
            best_score = moves_with_scores[0][1]
            second_best_move = moves_with_scores[1][0]
            second_best_score = moves_with_scores[1][1]

            score_diff = abs(best_score - second_best_score)
            max_diff = self.config.getint("blunder_logic", "max_score_diff_cp", fallback=20)

            if score_diff <= max_diff:
                min_chance = self.config.getfloat("blunder_logic", "min_blunder_chance", fallback=0.05)
                max_chance = self.config.getfloat("blunder_logic", "max_blunder_chance", fallback=0.10)
                blunder_chance = random.uniform(0, 1)
                
                if blunder_chance < random.uniform(min_chance, max_chance):
                    logging.info(f"Choosing second best move. Score diff: {score_diff/100.0} pawns.")
                    best_move = second_best_move

        return best_move, moves_with_scores

    def close(self):
        """
        Closes the engine.
        """
        self.engine.quit()
