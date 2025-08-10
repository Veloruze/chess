
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
        self.engine.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": 2500,
            "Skill Level": 20,
            "Contempt": 10,
            "Threads": 4,
            "Hash": 256,
        })

    def get_best_move(self, board, game_phase="middlegame"):
        """
        Gets the best move from the engine with dynamic depth, nodes limit, and blunder logic.
        """
        # 1. Dynamic Depth based on game phase
        if game_phase == "opening":
            depth = random.randint(10, 14)
        elif game_phase == "endgame":
            depth = random.randint(12, 16)
        else: # middlegame
            depth = random.randint(14, 18)

        # 2. Nodes Limit
        nodes = random.randint(2000000, 8000000)

        limit = chess.engine.Limit(depth=depth, nodes=nodes)

        # 3. Get top 2 moves
        try:
            info = self.engine.analyse(board, limit=limit, multipv=2)
        except Exception as e:
            logging.error(f"Engine analysis failed: {e}. Falling back to simpler search.")
            info = []

        if not info or len(info) < 1:
            # Fallback to a simpler search if the complex one fails
            info = self.engine.analyse(board, limit=chess.engine.Limit(depth=10), multipv=1)
            if not info:
                logging.error("Engine analysis failed completely.")
                return None, []


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
        best_score = moves_with_scores[0][1]

        # 4. Blunder Logic
        if len(moves_with_scores) > 1:
            second_best_move = moves_with_scores[1][0]
            second_best_score = moves_with_scores[1][1]

            # Score difference in centipawns
            score_diff = abs(best_score - second_best_score)

            # Blunder probability
            blunder_chance = random.uniform(0, 1)

            if score_diff <= 20 and blunder_chance < random.uniform(0.05, 0.10):
                logging.info(f"Choosing second best move. Score diff: {score_diff/100.0} pawns.")
                best_move = second_best_move

        return best_move, moves_with_scores

    def close(self):
        """
        Closes the engine.
        """
        self.engine.quit()
