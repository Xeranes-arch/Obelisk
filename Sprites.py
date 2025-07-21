import pygame
from GameObjects import *
# Initialize Pygame (required for image functions)
pygame.init()
pygame.display.set_mode()
# Load the sprite sheet
sprite_sheet = pygame.image.load("./assets/TileSetIsometricoFiumeIsole.png").convert_alpha()

# Sprite sheet info
sheet_width, sheet_height = sprite_sheet.get_size()
columns, rows = 5, 5
sprite_width = sheet_width // columns
sprite_height = sheet_height // rows

# Extract individual sprites into a list
sprites = []

for row in range(rows):
    for col in range(columns):
        rect = pygame.Rect(
            col * sprite_width,
            row * sprite_height,
            sprite_width,
            sprite_height
        )
        sprite = sprite_sheet.subsurface(rect).copy()  # copy() is optional but safer
        sprites.append(sprite)

TELEPORTER = sprites[24]


PLAYER = pygame.image.load("./assets/Isometric Pack/NormalMap.png").convert_alpha()
ROCK = pygame.image.load("./assets/Isometric Pack/crackedStone.png").convert_alpha()
GATE = pygame.image.load("./assets/Isometric Pack/Stone.png").convert_alpha()
WALL = pygame.image.load("./assets/Isometric Pack/SmoothStone.png").convert_alpha()
GROUND = pygame.image.load("./assets/Isometric Pack/HalfBrick.png").convert_alpha()
PIT = pygame.image.load("./assets/Isometric Pack/Dirt.png").convert_alpha()
ICE = pygame.image.load("./assets/Isometric Pack/Water.png").convert_alpha()
WIN = pygame.image.load("./assets/Isometric Pack/HalfGrass.png").convert_alpha()
SWITCH = pygame.image.load("./assets/Isometric Pack/HalfStone.png").convert_alpha()

SPRITES = {
    Player: PLAYER,
    Rock: ROCK,
    Gate: GATE,
    Wall: WALL,
    Ground: GROUND,
    Pit: PIT,
    Ice: ICE,
    Teleporter: TELEPORTER,
    Win: WIN,
    Switch: SWITCH,
    }