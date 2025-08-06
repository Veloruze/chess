
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

class StockfishEngine:
    """
    A wrapper for the Stockfish chess engine.
    """
    def __init__(self, config):
        self.config = config
        self.engine = chess.engine.SimpleEngine.popen_uci("engine/stockfish.exe")

    def get_best_move(self, board, depth=None):
        """
        Gets the best move from the engine.
        """
        if depth is None:
            depth_str = self.config.get("play", "engine_depth")
            depth = int(_parse_config_value(depth_str))
        limit = chess.engine.Limit(depth=depth)

        info = self.engine.analyse(board, limit=limit, multipv=3)
        # Sort moves by their score, best first
        moves_with_scores = []
        for pv in info:
            if "pv" in pv and pv["pv"]:
                move = pv["pv"][0]
                score = pv["score"].white().score(mate_score=10000) # Score from White's perspective, mate as large number
                moves_with_scores.append((move, score))
        
        # If it's Black's turn, we want the move with the lowest score (most negative).
        # Otherwise, for White, we want the highest score.
        is_black_turn = not board.turn
        moves_with_scores.sort(key=lambda x: x[1], reverse=not is_black_turn)
        
        best_move = None
        if moves_with_scores:
            best_move = moves_with_scores[0][0]

        return best_move, moves_with_scores

    def close(self):
        """
        Closes the engine.
        """
        self.engine.quit()
