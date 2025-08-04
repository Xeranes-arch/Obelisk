import inspect
import pygame
import Levels

# from Renderer import *
from Renderer import Renderer
from Levels import Level
from Board import Board
from GameObjects import *

# Constants
LINE = "\n_________________________\n"
CON = "press enter to continiue"

DELAY = 0.05

PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]

# Power ups that change mechanics
GAME_FLAGS = {
    "gates_go_up": False,
    "wall_kick": False,
}


def key_to_move(key):
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


class Game:
    def __init__(self, screen_width=1600, screen_height=900):

        pygame.init()
        # Ignore all mouse events
        pygame.event.set_blocked(
            [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
        )

        self.renderer = Renderer(screen_width, screen_height)
        self.board = None

    def make_move(self, board: Board, current_player: Player, move, recursion_depth=0):
        """Executes move on board."""

        # Calculate new position
        new_pos = tuple(a + b for a, b in zip(move, current_player.position))

        # Wrap new position back into board
        new_pos = board.wrap(new_pos)

        # Actual move handled by game objects
        other = board.get_collision_target(current_player, new_pos)
        current_player.collide_with(other, board)

    def help(self, board):
        """Show controlls"""
        board.msg = (
            "CONTROLLS:\n\nQuit to main menu: Esc\nMovement: Aelira - wasd, Baelric - ijkl\nCycle transparent layers: t\n Increase/Decrease visible radius: up/down\nShow help menu: h"
            + LINE
            + CON
        )

    def play(self, lv: Level, board: Board):
        self.board = board
        # LV DEPENDENT PARAMS for renderer
        pygame.display.set_caption(lv.__repr__())
        # Display parameters
        corners = [
            self.renderer.grid_to_iso(0, 0, 0),
            self.renderer.grid_to_iso(board.height - 1, 0, 0),
            self.renderer.grid_to_iso(0, board.width - 1, 0),
            self.renderer.grid_to_iso(board.height - 1, board.width - 1, 0),
        ]
        self.renderer.min_x = min(c[0] for c in corners)
        max_x = max(c[0] for c in corners)
        self.renderer.min_y = min(c[1] for c in corners)
        max_y = max(c[1] for c in corners)
        self.renderer.grid_width_px = max_x - self.renderer.min_x
        self.renderer.grid_height_px = max_y - self.renderer.min_y
        # Zoom level
        zoom_x = self.renderer.screen_width / (self.renderer.grid_width_px) * 0.6
        zoom_y = self.renderer.screen_height / (self.renderer.grid_height_px) * 0.6
        self.renderer.zoom = min(zoom_x, zoom_y)

        # Play
        self.renderer.displaying_message = False
        self.renderer.transparent_layers = 0
        exit_flag = False
        lv.on_enter(self)
        while True:

            for event in pygame.event.get():
                # Window closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Button press
                if event.type == pygame.KEYDOWN:

                    # Esc - to quit to main menu
                    if event.key == 27:
                        return "Esc"

                    # Enter - to hide message (and quit if exit_flag)
                    if event.key == 13:
                        self.renderer.displaying_message = False
                        board.msg = None
                        # Take image of end state
                        board.take_snapshot()
                        if exit_flag:
                            return exit_flag

                    # Lock out of all options except enter and quit when:
                    if self.renderer.displaying_message:
                        # time.sleep(DELAY)
                        continue

                    if event.key == 1073741906:
                        self.renderer.visible_radius += 1
                    if (
                        event.key == 1073741905
                        and self.renderer.visible_radius
                        > -1 / 2 * max(board.width, board.height)
                    ):
                        self.renderer.visible_radius -= 1

                    # INPUT OPTIONS
                    try:
                        key = chr(event.key)
                    except:
                        continue

                    # Change transparency
                    if key == "t":
                        self.renderer.transparent_layers += 1
                        self.renderer.transparent_layers = (
                            self.renderer.transparent_layers % 3
                        )
                        board.take_snapshot()
                        continue
                    # Help menu
                    elif key == "h":
                        self.help(board)
                    # Actual move
                    elif key in PLAYER1_INPUTS or key in PLAYER2_INPUTS:
                        # Translate to move
                        current_player_idx, move = key_to_move(key)

                        # Execute turn
                        current_player = board.players[current_player_idx]
                        self.make_move(board, current_player, move)

                        # END OF TURN EFFECTS
                        board.update_gates(board.flags)
                        board.fall()
                        board.pit_check()
                        board.win_check()

                        # Death case
                        if len(board.players) < 2:
                            exit_flag = "died"
                        # Win case
                        if board.win:
                            if lv.transformations:
                                lv.transform()
                                board.win = False
                            else:
                                exit_flag = "W"

                        # Take image of end state
                        board.take_snapshot()
                        for snapshot in board.snapshots:
                            self.renderer.draw_board(board, snapshot)

                            pygame.display.flip()
                            self.renderer.clock.tick(self.renderer.fps)

                        board.snapshots = []

            if not self.renderer.displaying_message:
                self.renderer.draw_board(board)
                pygame.display.flip()
                self.renderer.clock.tick(self.renderer.fps)

            # Render text message (only once, then stuck until enter or esc)
            if board.msg and not self.renderer.displaying_message:

                self.renderer.draw_board(board)

                self.renderer.dim()

                self.renderer.draw_text(board.msg)

                pygame.display.flip()
                continue


def main_menu(game: Game, unlocked_levels):
    nrs = []
    invalid = False
    while True:
        for event in pygame.event.get():
            # Window closed or Esc
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == 27
            ):
                pygame.quit()
                exit()

            # Enter to confirm
            if event.type == pygame.KEYDOWN and event.key == 13:
                if nrs == []:
                    continue

                number = int("".join(nrs))
                if number in range(unlocked_levels + 1):
                    return number
                else:
                    invalid = True
                    nrs = []

            if event.type == pygame.KEYDOWN and event.key == 8 and len(nrs) > 0:
                nrs.pop(-1)

            # Type number choices
            if event.type == pygame.KEYDOWN and event.key in range(48, 58):
                nrs.append(chr(event.key))
                invalid = False

            # Render text
            game.renderer.screen.fill((30, 30, 30))
            text = "Pick a Level:" + LINE
            for i in range(unlocked_levels):
                text += f"Level{i+1}\n"
            if invalid:
                msg = text + LINE + "Invalid Level Nr" + LINE + "Try again"
                game.renderer.draw_text(msg)
            else:
                msg = text + LINE + "".join(nrs)
                game.renderer.draw_text(msg)

            pygame.display.flip()
            game.renderer.clock.tick(game.renderer.fps)


def main():
    Level_instances = [
        cls
        for name, cls in inspect.getmembers(Levels, inspect.isclass)
        if cls.__module__ == "Levels" and name.startswith("Level")
    ]
    Level_instances.pop(0)

    game = Game()

    lv_idx = 1
    unlocked_levels = 1
    menu_skip = True
    while True:
        # Call main menu
        if not menu_skip:
            lv_idx = main_menu(game, unlocked_levels)

        # Start level
        lv: Level = Level_instances[lv_idx]()
        board = lv.setup_board()
        exit_status = game.play(lv, board)

        if exit_status == "W":
            riddle_res = lv.end(game)
            print(riddle_res)
            if riddle_res and lv_idx == unlocked_levels:
                unlocked_levels += 1
                lv_idx += 1
                menu_skip = True
            else:
                menu_skip = False

        if exit_status == "Esc":
            menu_skip = False

        if exit_status == "died":
            menu_skip = True


if __name__ == "__main__":
    main()


### TODO wall kick off switch over pit onto gate

### TODO freeze player to use as wall

### TODO text interactions in pygame
