import sys
import tty
import inspect
import termios

import Levels
from Levels import Level
from Board import Board
from GameObjects import *

# Constants
LINE = "\n_________________________\n"

# Field type representations
GROUND = "."
PIT = "x"
WALL = "#"
ICE = "□"
TELEPORT = "T"
WIN = "W"
SWITCH = "S"
GATE = "G"
FIELD_TYPES = [PIT, WALL, ICE, TELEPORT, WIN, SWITCH, GATE]

# Secrets
LOOSE_ROCK = "+"
ROCK = "R"


PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]

# Power ups that change mechanics
GAME_FLAGS = {
    "gates_go_up": False,
    "rocks_spawn": False,
    "wall_kick": False,
}


def get_key():
    """Read a single keypress from stdin and return it."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def prompt_move():
    while True:
        try:
            key = get_key()
            for j, i in enumerate(PLAYER_INPUTS):
                if key == i[0]:
                    move = (-1, 0)
                elif key == i[1]:
                    move = (0, -1)
                elif key == i[2]:
                    move = (1, 0)
                elif key == i[3]:
                    move = (0, 1)
                elif key == "\x1b":
                    print("Exiting.", LINE)
                    return None, "Q"
                if key in i:
                    current_player_idx = j
            return current_player_idx, move
        except:
            pass


def make_move(board: Board, current_player: Player, move, recursion_depth=0):
    """Executes move on board."""

    # Store old position
    old_pos = current_player.position

    # Calculate new position
    new_pos = tuple(a + b for a, b in zip(move, current_player.position))

    # Wrap new position back into board
    new_pos = board.wrap(new_pos)

    # Actual move handled by game objects
    other = board.get_collision_target(current_player, new_pos)
    current_player.collide_with(other, board)


def play(lv: Level, board: Board, lv_idx):

    board.display()
    # Play
    while True:

        current_player_idx, move = prompt_move()

        # Quit to main
        if move == "Q":
            board.flags["gates_go_up"] = False 
            board.flags["wall_kick"] = False 
            return move

        current_player = board.players[current_player_idx]
        make_move(board, current_player, move)

        # End of turn effects
        board.update_gates(GAME_FLAGS)
        board.pit_check()

        # Win case
        if sorted([i.position for i in board.players]) == sorted(
            [i.position for i in board.wins]
        ):
            board.display()
            print("DONE!!!", LINE)
            lv.end()
            if lv_idx == 6:
                for i in board.wins:
                    board.flags["gates_go_up"] = True 
                    board.flags["wall_kick"] = True 
                    board.set_element(board.ground, i.position, Ground(i.position))
                    board.spawn_rocks()
                board.wins=[]
            else:
                return "W"
            
        # Secret Win case
        if sorted([i.position for i in board.players]) == sorted([(7,7),(7,8)]):
            print(LINE,LINE,"\nYOU'VE DONE IT!!!\nThe entire system shuts down and the archway of darkness opens up again.\nOutside, the Obelisk falls silent at last.")

        # Death case
        if len(board.players) < 2:
            board.flags["gates_go_up"] = False 
            board.flags["wall_kick"] = False 
            board.display()
            input("press enter to restart")
            return "died"
        board.display()


def main_menu(unlocked_levels):

    while True:
        try:
            print("Pick a level:")
            for i in range(unlocked_levels):
                print(f"level{i+1}")
            lv = input()
            if lv == "":
                lv = 0
            elif int(lv) - 1 in range(unlocked_levels):
                lv = int(lv)
            return lv
        except:
            pass


def main():

    Level_classes = [
        cls
        for name, cls in inspect.getmembers(Levels, inspect.isclass)
        if cls.__module__ == "Levels" and name.startswith("Level")
    ]
    Level_classes.pop(0)

    lv_idx = 1
    unlocked_levels = 1

    menu_skip = True

    while True:
        # Call main menu
        if not menu_skip:
            lv_idx = main_menu(unlocked_levels)

        # Start level
        lv: Level = Level_classes[lv_idx](GAME_FLAGS)
        lv.on_enter()
        board = lv.setup_board()
        exit_status = play(lv, board,lv_idx)

        if exit_status == "W" and lv_idx == unlocked_levels:
            unlocked_levels += 1
            lv_idx += 1
            menu_skip = True

        if exit_status == "Q":
            menu_skip = False

        if exit_status == "died":
            menu_skip = True

if __name__ == "__main__":
    main()


### use to press button and let both into a section
### block tp to allow function


### Kick rebound enables pulling another onto ice maybe

### TODO wall kick off switch over pit onto gate
