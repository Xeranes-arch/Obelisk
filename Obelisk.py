import sys
import tty
import inspect
import termios

import pygame

import Levels
from Levels import Level
from Board import Board
from GameObjects import *
from Sprites import SPRITES

# Constants
LINE = "\n_________________________\n"
DELAY = 0.05

PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]

# Power ups that change mechanics
GAME_FLAGS = {
    "gates_go_up": False,
    "rocks_spawn": False,
    "wall_kick": False,
}

# Pygame Constants
TILE_WIDTH = 32
TILE_HEIGHT = 16
GRID_WIDTH = 20
GRID_HEIGHT = 20

BASE_WIDTH, BASE_HEIGHT = 1600, 900


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


def pygame_move(key):
    try:
        for j, i in enumerate(PLAYER_INPUTS):
            if key == i[0]:
                move = (-1, 0)
            elif key == i[1]:
                move = (0, -1)
            elif key == i[2]:
                move = (1, 0)
            elif key == i[3]:
                move = (0, 1)
            if key in i:
                current_player_idx = j
        return current_player_idx, move
    except:
        pass


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


def grid_to_iso(x, y, z):
    iso_x = -(x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2) - z * TILE_HEIGHT
    return iso_x, iso_y


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
    # show - non pygame
    # board.display()

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))

    # Create render surface
    render_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    pygame.display.set_caption(lv.__repr__())
    clock = pygame.time.Clock()
    clock.tick(60)

    # Display parameters
    corners = [
        grid_to_iso(0, 0, 0),
        grid_to_iso(board.hight - 1, 0, 0),
        grid_to_iso(0, board.width - 1, 0),
        grid_to_iso(board.hight - 1, board.width - 1, 0),
    ]
    min_x = min(c[0] for c in corners)
    max_x = max(c[0] for c in corners)
    min_y = min(c[1] for c in corners)
    max_y = max(c[1] for c in corners)
    grid_width_px = max_x - min_x
    grid_height_px = max_y - min_y
    # Zoom level
    zoom_x = BASE_WIDTH / (grid_width_px) * 0.6
    zoom_y = BASE_HEIGHT / (grid_height_px) * 0.6
    zoom = min(zoom_x, zoom_y)

    # For toggeling visible layers
    transparent_layers = 0

    # To show initial board state
    board.snapshots.append(
        [
            copy.deepcopy(board.ground),
            copy.deepcopy(board.middle),
            copy.deepcopy(board.top),
        ]
    )

    # Play
    exit_flag = False
    while True:
        # move prompt - non pygame
        # current_player_idx, move = prompt_move()

        for event in pygame.event.get():
            # Window closed
            if event.type == pygame.QUIT:
                exit_flag = "Q"

            # Button press
            if event.type == pygame.KEYDOWN:
                try:
                    key = chr(event.key)
                except:
                    continue

                # Change transparency
                if key == "t":
                    transparent_layers += 1
                    transparent_layers = transparent_layers % 3
                    board.snapshots.append(
                        [
                            copy.deepcopy(board.ground),
                            copy.deepcopy(board.middle),
                            copy.deepcopy(board.top),
                        ]
                    )
                    continue

                # Escape to main menu
                elif key == "\x1b":
                    board.flags["gates_go_up"] = False
                    board.flags["wall_kick"] = False
                    exit_flag = "Q"

                # Actual move
                elif key in PLAYER1_INPUTS or key in PLAYER2_INPUTS:
                    # Translate to move
                    current_player_idx, move = pygame_move(key)

                    # Execute turn
                    current_player = board.players[current_player_idx]
                    make_move(board, current_player, move)

                    # End of turn effects

                    board.update_gates(GAME_FLAGS)
                    board.pit_check()
                    board.fall()

                    # Win case
                    if sorted([i.position for i in board.players]) == sorted(
                        [i.position for i in board.wins]
                    ):
                        # board.display() - non pygame

                        print("DONE!!!", LINE)
                        if lv_idx == 6:
                            for i in board.wins:
                                board.flags["gates_go_up"] = True
                                board.flags["wall_kick"] = True
                                board.set_element(
                                    board.ground, i.position, Ground(i.position)
                                )
                                board.spawn_rocks()
                            board.wins = []
                        else:

                            exit_flag = "W"

                    # Secret Win case
                    if sorted([i.position for i in board.players]) == sorted(
                        [(7, 7), (7, 8)]
                    ):
                        print(
                            LINE,
                            LINE,
                            "\nYOU'VE DONE IT!!!\nThe entire system shuts down and the archway of darkness opens up again.\nOutside, the Obelisk falls silent at last.",
                        )

                    # Death case
                    if len(board.players) < 2:
                        board.flags["gates_go_up"] = False
                        board.flags["wall_kick"] = False
                        # board.display()

                        exit_flag = "died"

                    # Display in Terminal
                    # board.display()

                    # Take image of end state
                    board.snapshots.append(
                        [
                            copy.deepcopy(board.ground),
                            copy.deepcopy(board.middle),
                            copy.deepcopy(board.top),
                        ]
                    )

            # Draw
            for layers in board.snapshots:
                render_surface.fill((30, 30, 30))  # Dark background
                for i in range(-1, board.hight + 1):
                    for j in range(board.width):
                        for z in range(3):
                            offset_y = 0
                            element = board.get_element(layers[z], (i, j))
                            if element:
                                screen_x, screen_y = grid_to_iso(i, j, z)
                                sprite = SPRITES[type(element)]
                                if type(element) == Teleporter:
                                    offset_y = -0.5 * TILE_HEIGHT
                                if type(element) == Pit:
                                    sprite.set_alpha(0)
                                elif (
                                    2 - z - transparent_layers < 0
                                    and type(element) != Player
                                ):
                                    sprite.set_alpha(0)
                                else:
                                    sprite.set_alpha(255)

                                render_surface.blit(
                                    sprite,
                                    (
                                        screen_x
                                        + 0.5 * (BASE_WIDTH - grid_width_px)
                                        - min_x,
                                        screen_y
                                        + 0.5 * (BASE_HEIGHT - grid_height_px)
                                        - min_y
                                        + offset_y,
                                    ),
                                )
                # Rescale
                zoomed_surface = pygame.transform.scale(
                    render_surface, (int(BASE_WIDTH * zoom), int(BASE_HEIGHT * zoom))
                )

                zoomed_width = zoomed_surface.get_width()
                zoomed_height = zoomed_surface.get_height()

                center_x = (BASE_WIDTH - zoomed_width) // 2
                center_y = (BASE_HEIGHT - zoomed_height) // 2

                # Main draw
                screen.blit(zoomed_surface, (center_x, center_y))

                pygame.display.flip()
                time.sleep(DELAY)
            board.snapshots = []
        if exit_flag:
            return exit_flag


def main_menu(unlocked_levels):
    while True:
        try:
            print(LINE, "\nPick a level:")
            for i in range(unlocked_levels):
                print(f"Level{i+1}")
            print(LINE)
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

    lv_idx = 8
    unlocked_levels = 8

    menu_skip = True

    while True:
        # Call main menu
        if not menu_skip:
            lv_idx = main_menu(unlocked_levels)

        # Start level
        lv: Level = Level_classes[lv_idx](GAME_FLAGS)
        lv.on_enter()
        board = lv.setup_board()
        exit_status = play(lv, board, lv_idx)
        pygame.quit()

        if exit_status == "W":
            lv.end()
            if lv_idx == unlocked_levels:
                unlocked_levels += 1
                lv_idx += 1
                menu_skip = True

        if exit_status == "Q":
            menu_skip = False

        if exit_status == "died":
            input("press enter to restart")
            menu_skip = True


if __name__ == "__main__":
    main()


### TODO wall kick off switch over pit onto gate

### TODO freeze player to use as wall

### TODO Secret win con is hardcoded!!!
