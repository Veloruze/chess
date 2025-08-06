
import argparse
import configparser
import logging
import os
import sys
import time
import random

from src.browser import ChessBrowser
from src.game import Game

CREDENTIALS_FILE = "credentials.txt"
from src.utils import _parse_config_value

def get_credentials():
    username = ""
    password = ""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                username = lines[0].strip()
                password = lines[1].strip()
    
    if not username or not password:
        print("Credentials not found or incomplete. Please enter them.")
        username = input("Enter Chess.com username: ")
        password = input("Enter Chess.com password: ")
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(f"{username}\n{password}\n")
        print(f"Credentials saved to {CREDENTIALS_FILE}")
    
    return username, password

def main():
    """
    Main function to run the chess assistant.
    """
    parser = argparse.ArgumentParser(description="Chess.com assistant.")
    parser.add_argument("--mode", choices=["Bullet", "Blitz", "Rapid"], help="Game mode.")
    parser.add_argument("--headless", type=bool, help="Run in headless mode.")
    parser.add_argument("--engine-depth", type=int, help="Engine search depth.")
    parser.add_argument("--auto-move", type=bool, help="Enable auto-move.")
    
    
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        config["play"] = {
            "mode": "Blitz",
            "headless": "false",
            "engine_depth": "15",
            "auto_move": "false",
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        print("config.ini not found. A new one has been created. Please fill it out and run the script again.")
        sys.exit(0)

    config.read("config.ini")

    # Manually parse config values to handle inline comments
    config_mode = _parse_config_value(config.get("play", "mode"))
    config_headless = _parse_config_value(config.get("play", "headless")).lower() == 'true'
    config_engine_depth = int(_parse_config_value(config.get("play", "engine_depth")))
    config_auto_move = _parse_config_value(config.get("play", "auto_move")).lower() == 'true'
    config_auto_play = _parse_config_value(config.get("play", "auto_play")).lower() == 'true'
    config_num_games = int(_parse_config_value(config.get("play", "num_games")))

    # Override config with CLI args
    if args.mode:
        config.set("play", "mode", args.mode)
    else:
        config.set("play", "mode", config_mode) # Set parsed value if not overridden by CLI

    if args.headless is not None:
        config.set("play", "headless", str(args.headless))
    else:
        config.set("play", "headless", str(config_headless))

    if args.engine_depth is not None:
        config.set("play", "engine_depth", str(args.engine_depth))
    else:
        config.set("play", "engine_depth", str(config_engine_depth))

    if args.auto_move is not None:
        config.set("play", "auto_move", str(args.auto_move))
    else:
        config.set("play", "auto_move", str(config_auto_move))
    
    config.set("play", "auto_play", str(config_auto_play))
    config.set("play", "num_games", str(config_num_games))

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    username, password = get_credentials()

    browser = ChessBrowser(config)
    game = Game(config, browser)

    games_played = 0
    try:
        browser.start()
        browser.login(username, password)

        while True:
            if config_num_games != 0 and games_played >= config_num_games:
                logging.info(f"Finished playing {games_played} games as per num_games setting.")
                break

            logging.info(f"Starting game {games_played + 1}...")
            browser.select_mode() # This needs to be called for each new game
            game.start() # This needs to be modified to return when game is over

            games_played += 1
            logging.info(f"Game {games_played} finished.")

            if config_auto_play:
                # Handle game over modal and click new game button
                if not handle_game_over_modal(browser, config_mode): # New function
                    logging.info("Could not find game over modal or new game button. Stopping auto-play.")
                    break
                logging.info("Starting next game...")
            else:
                logging.info("Auto-play is disabled. Stopping after one game.")
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        browser.close()

def handle_game_over_modal(browser_instance, game_mode):
    try:
        # Wait for the game over modal to appear
        game_over_modal = browser_instance.page.wait_for_selector(".game-over-modal-content", timeout=10000)
        logging.info("Game over modal detected.")

        # Determine the text for the new game button based on the mode
        button_text = ""
        if game_mode.lower() == "bullet":
            button_text = "New 1 min"
        elif game_mode.lower() == "blitz":
            button_text = "New 3 min"
        elif game_mode.lower() == "rapid":
            button_text = "New 10 min"
        else:
            logging.warning(f"Unknown game mode: {game_mode}. Cannot determine new game button text.")
            return False

        # Click the new game button within the modal
        new_game_button_selector = f"button:has-text('{button_text}')"
        
        # Add random delay before starting a new game
        delay = random.randint(10, 30)
        logging.info(f"Waiting for {delay} seconds before starting a new game...")
        time.sleep(delay)

        logging.info(f"Attempting to click new game button: {new_game_button_selector}")
        browser_instance.page.click(new_game_button_selector, timeout=5000)
        logging.debug(f"Successfully clicked {button_text} button.")
        return True
    except Exception as e:
        logging.error(f"Error handling game over modal: {e}")
        return False


if __name__ == "__main__":
    main()
