import inspect
import textwrap
import pygame
import Levels
from Levels import Level
from Board import Board
from GameObjects import *
from Sprites import SPRITES


# Constants
LINE = "\n_________________________\n"
CON = "press enter to continiue"

FPS = 30
DELAY = 0.05

PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]

# Power ups that change mechanics
GAME_FLAGS = {
    "gates_go_up": False,
    "wall_kick": False,
}

# Pygame Constants
TILE_WIDTH = 32
TILE_HEIGHT = 16
GRID_WIDTH = 20
GRID_HEIGHT = 20

BASE_WIDTH, BASE_HEIGHT = 1600, 900


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


def grid_to_iso(x, y, z):
    iso_x = -(x - y) * (TILE_WIDTH // 2)
    iso_y = (x + y) * (TILE_HEIGHT // 2) - z * TILE_HEIGHT
    return iso_x, iso_y


class Game:
    def __init__(self, screen_width=1600, screen_height=900):

        pygame.init()
        # Ignore all mouse events
        pygame.event.set_blocked(
            [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
        )

        self.renderer = Renderer(screen_width, screen_height)

        # Cycling visible layers
        self.transparent_layers = 0
        self.visible_radius = 0

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

        # LV DEPENDENT PARAMS for renderer
        pygame.display.set_caption(lv.__repr__())
        # Display parameters
        corners = [
            grid_to_iso(0, 0, 0),
            grid_to_iso(board.hight - 1, 0, 0),
            grid_to_iso(0, board.width - 1, 0),
            grid_to_iso(board.hight - 1, board.width - 1, 0),
        ]
        self.renderer.min_x = min(c[0] for c in corners)
        max_x = max(c[0] for c in corners)
        self.renderer.min_y = min(c[1] for c in corners)
        max_y = max(c[1] for c in corners)
        self.renderer.grid_width_px = max_x - self.renderer.min_x
        self.renderer.grid_height_px = max_y - self.renderer.min_y
        # Zoom level
        zoom_x = BASE_WIDTH / (self.renderer.grid_width_px) * 0.6
        zoom_y = BASE_HEIGHT / (self.renderer.grid_height_px) * 0.6
        self.renderer.zoom = min(zoom_x, zoom_y)

        # Play
        self.renderer.displaying_message = False
        self.transparent_layers = 0
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
                        board.msg = None
                        # Take image of end state
                        board.take_snapshot()
                        if exit_flag:
                            return exit_flag

                    # Lock out of all options except enter and quit when:
                    if board.msg:
                        time.sleep(DELAY)
                        continue

                    if event.key == 1073741906:
                        self.visible_radius += 1
                    if event.key == 1073741905 and self.visible_radius > -1 / 2 * max(
                        board.width, board.hight
                    ):
                        self.visible_radius -= 1

                    # INPUT OPTIONS
                    try:
                        key = chr(event.key)
                    except:
                        continue

                    # Change transparency
                    if key == "t":
                        self.transparent_layers += 1
                        self.transparent_layers = self.transparent_layers % 3
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
                            self.renderer.draw_board(self, lv, board, snapshot)

                            pygame.display.flip()
                            self.renderer.clock.tick(FPS)

                        board.snapshots = []

            # Here for 60fps
            # Here for every input
            # Here for every keypress
            if not board.msg:
                self.renderer.draw_board(self, lv, board)
                pygame.display.flip()
                self.renderer.clock.tick(FPS)

            # Render text message (only once, then stuck until enter or esc)
            if board.msg and not self.renderer.displaying_message:

                self.renderer.draw_board(self, lv, board)

                # Dim the background
                overlay = pygame.Surface(self.renderer.screen.get_size())
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                self.renderer.screen.blit(overlay, (0, 0))

                self.renderer.draw_text(board.msg)

                pygame.display.flip()
                continue


class Renderer:
    def __init__(self, screen_width, screen_height):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.render_surface = pygame.Surface((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.font = pygame.font.SysFont(None, 32)

        self.displaying_message = True

        self.grid_width_px = 0
        self.grid_height_px = 0
        self.min_x = 0
        self.min_y = 0
        self.zoom = 1

    def zoom_surface(self):

        # Rescale
        zoomed_surface = pygame.transform.scale(
            self.render_surface,
            (int(BASE_WIDTH * self.zoom), int(BASE_HEIGHT * self.zoom)),
        )

        zoomed_width = zoomed_surface.get_width()
        zoomed_height = zoomed_surface.get_height()

        center_x = (BASE_WIDTH - zoomed_width) // 2
        center_y = (BASE_HEIGHT - zoomed_height) // 2

        return zoomed_surface, center_x, center_y

    def draw_board(self, game: Game, lv: Level, board: Board, snapshot=None):

        if not snapshot:
            snapshot = board.take_snapshot(True)

        # Draw
        self.render_surface.fill((30, 30, 30))  # Dark background
        for i in range(-game.visible_radius, board.hight + game.visible_radius):
            for j in range(-game.visible_radius, board.width + game.visible_radius):
                for z in range(3):
                    offset_y = 0
                    element = board.get_element(snapshot[z], (i, j))
                    if element:
                        screen_x, screen_y = grid_to_iso(i, j, z)
                        sprite = SPRITES[type(element)]

                        # Ensure players get dedicated sprite
                        if type(element) == Player:
                            if element.name == "Aelira":
                                sprite = sprite[0]
                            else:
                                sprite = sprite[1]

                        # Move lower half Block to upper
                        if type(element) == Teleporter:
                            offset_y = -0.5 * TILE_HEIGHT

                        # Who needs an actual empty tile
                        if type(element) == Pit:
                            sprite.set_alpha(0)

                        # Make disabled layers transparent
                        elif (
                            2 - z - game.transparent_layers
                            < 0
                            # and type(element) != Player - for leaving players visible
                        ):
                            sprite.set_alpha(100)

                        else:
                            sprite.set_alpha(255)

                        self.render_surface.blit(
                            sprite,
                            (
                                screen_x
                                + 0.5 * (BASE_WIDTH - self.grid_width_px)
                                - self.min_x,
                                screen_y
                                + 0.5 * (BASE_HEIGHT - self.grid_height_px)
                                - self.min_y
                                + offset_y,
                            ),
                        )
        # Zoom
        zoomed_surface, center_x, center_y = self.zoom_surface()
        # Main draw
        self.screen.blit(zoomed_surface, (center_x, center_y))

    def draw_text(self, text, color=(255, 255, 255), line_spacing=5):
        """Render text with word wrap inside a given rect."""

        screen_width, screen_height = self.render_surface.get_size()

        j = 0
        parts = text.split("\n")
        for text in parts:
            old_j = copy.deepcopy(j)
            if not text.strip():
                continue
            lines = []

            # Use textwrap to break text into wrapped lines
            wrapper = textwrap.TextWrapper(width=70)  # Adjust width for line length
            wrapped_lines = wrapper.wrap(text)

            # Render each line and add to list
            for line in wrapped_lines:
                j += 1
                rendered_line = self.font.render(line, True, color)
                lines.append(rendered_line)

            total_height = sum(line.get_height() for line in lines)
            max_line_width = max(line.get_width() for line in lines)

            # Create a bounding rect centered on screen
            rect = pygame.Rect(
                (screen_width - max_line_width) // 2,
                (screen_height) // 2 + old_j * 45 - 300,
                max_line_width,
                total_height,
            )

            # Blit each line with spacing
            y = rect.top
            for line_surface in lines:
                line_rect = line_surface.get_rect()
                line_rect.topleft = ((screen_width - line_surface.get_width()) // 2, y)
                self.screen.blit(line_surface, line_rect)
                y += line_surface.get_height() + line_spacing

            self.displaying_message = True

            # self.zoom = 1
            # zoomed_surface, offset_x, offset_y = self.zoom_surface()
            # self.screen.blit(zoomed_surface, (offset_x  , offset_y))


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
                msg = text + "Invalid Level Nr"
                game.renderer.draw_text(msg)
            else:
                msg = text + LINE + "".join(nrs)
                game.renderer.draw_text(msg)

            pygame.display.flip()
            game.renderer.clock.tick(60)


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
            lv.end()
            if lv_idx == unlocked_levels:
                unlocked_levels += 1
                lv_idx += 1
                menu_skip = True

        if exit_status == "Esc":
            menu_skip = False

        if exit_status == "died":
            menu_skip = True
    pygame.quit()


if __name__ == "__main__":
    main()


### TODO wall kick off switch over pit onto gate

### TODO freeze player to use as wall

### TODO text interactions in pygame
