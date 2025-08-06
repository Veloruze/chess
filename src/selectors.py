# src/selectors.py

LOGIN_USERNAME_INPUT = "#login-username"
LOGIN_PASSWORD_INPUT = "#login-password"
LOGIN_BUTTON_SELECTORS = [
    "#login",
    "button:has-text('Log In')",
    "button[type='submit']",
]

TIME_CONTROL_DROPDOWN_BUTTON = ".time-selector-next-component .selector-button-button"
TIME_CONTROL_SELECTORS = {
    "bullet": ":text('1 min')",
    "blitz": ":text('3 min')",
    "rapid": ":text('10 min')",
}

PLAY_BUTTON_SELECTORS = [
    "button:has-text('Start Game')",
]

BOARD_SELECTOR = ".board"

# Game over/re-arm selectors
NEW_GAME_BUTTON_SELECTORS = [
    "button:has-text('New Game')",
    "button:has-text('New 3 min')", # Specific to the screenshot
    "button:has-text('Rematch')",
]

def algebraic_to_xy_selector(square, is_flipped=False):
    """
    Converts an algebraic square string (e.g., 'e2') to a selector-friendly XY format (e.g., '52').
    If is_flipped is True, it adjusts the coordinates for a flipped board.
    """
    col = ord(square[0]) - ord('a') + 1
    row = int(square[1])

    if is_flipped:
        col = 9 - col
        row = 9 - row

    return f"{col}{row}"
