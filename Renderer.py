import pygame
import textwrap
from Sprites import SPRITES
from GameObjects import *

if TYPE_CHECKING:
    from Board import Board


# Pygame Constants
TILE_WIDTH = 32
TILE_HEIGHT = 16

FPS = 30


class Renderer:
    def __init__(self, screen_width, screen_height):

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.render_surface = pygame.Surface((screen_width, screen_height))

        self.clock = pygame.time.Clock()
        self.fps = FPS

        self.font = pygame.font.SysFont(None, 32)
        self.displaying_message = False

        # Board display and zoom params
        self.grid_width_px = 0
        self.grid_height_px = 0
        self.min_x = 0
        self.min_y = 0
        self.zoom = 1

        # Object visibility
        self.transparent_layers = 0
        self.visible_radius = 0

    def grid_to_iso(self, x, y, z):
        iso_x = -(x - y) * (TILE_WIDTH // 2)
        iso_y = (x + y) * (TILE_HEIGHT // 2) - z * TILE_HEIGHT
        return iso_x, iso_y

    def zoom_surface(self):

        # Rescale
        if self.zoom > 2.5:
            self.zoom = 2.5
        zoomed_surface = pygame.transform.scale(
            self.render_surface,
            (int(self.screen_width * self.zoom), int(self.screen_height * self.zoom)),
        )

        zoomed_width = zoomed_surface.get_width()
        zoomed_height = zoomed_surface.get_height()

        center_x = (self.screen_width - zoomed_width) // 2
        center_y = (self.screen_height - zoomed_height) // 2

        return zoomed_surface, center_x, center_y

    def draw_board(self, board: "Board", snapshot=None):

        if not snapshot:
            snapshot = board.take_snapshot(True)

        # Draw
        self.render_surface.fill((30, 30, 30))  # Dark background
        for i in range(-self.visible_radius, board.height + self.visible_radius):
            for j in range(-self.visible_radius, board.width + self.visible_radius):
                for z in range(3):
                    offset_y = 0
                    element = board.get_element(snapshot[z], (i, j))
                    if element:
                        screen_x, screen_y = self.grid_to_iso(i, j, z)
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
                            2 - z - self.transparent_layers
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
                                + 0.5 * (self.screen_width - self.grid_width_px)
                                - self.min_x,
                                screen_y
                                + 0.5 * (self.screen_height - self.grid_height_px)
                                - self.min_y
                                + offset_y,
                            ),
                        )
        # Zoom
        zoomed_surface, center_x, center_y = self.zoom_surface()
        # Main draw
        self.screen.blit(zoomed_surface, (center_x, center_y))

    def dim(self):
        # Dim the background
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

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
