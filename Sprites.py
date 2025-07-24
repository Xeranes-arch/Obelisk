import pygame
from GameObjects import *

# Initialize Pygame (required for image functions)
pygame.init()
pygame.display.set_mode()
# Load the sprite sheet
# Credit https://starlinetor.itch.io/isometrical-tile-set-river-and-island starlinetor
sprite_sheet = pygame.image.load(
    "./assets/TileSetIsometricoFiumeIsole.png"
).convert_alpha()

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
            col * sprite_width, row * sprite_height, sprite_width, sprite_height
        )
        sprite = sprite_sheet.subsurface(rect).copy()  # copy() is optional but safer
        sprites.append(sprite)

TELEPORTER = sprites[24]

# Credit https://jaofazjogos.itch.io/iconisometricpack Jao
Aelira = pygame.image.load("./assets/Heroes/FOES/OriginalRes/IMPERIALS/spy assassin.png").convert_alpha()
Baelric = pygame.image.load("./assets/Heroes/PCs/OriginalRes/Baelric.png").convert_alpha()
PLAYERS = [Aelira, Baelric]

# Credit https://leon-twemlow.itch.io/free-isometric-tile-pack Leon Twemlow
ROCK = pygame.image.load("./assets/Floors/crackedStone.png").convert_alpha()
GATE = pygame.image.load("./assets/Floors/Stone.png").convert_alpha()
WALL = pygame.image.load("./assets/Floors/SmoothStone.png").convert_alpha()
GROUND = pygame.image.load("./assets/Floors/HalfBrick.png").convert_alpha()
PIT = pygame.image.load("./assets/Floors/Dirt.png").convert_alpha()
ICE = pygame.image.load("./assets/Floors/Water.png").convert_alpha()
WIN = pygame.image.load("./assets/Floors/HalfGrass.png").convert_alpha()
SWITCH = pygame.image.load("./assets/Floors/HalfSand.png").convert_alpha()

SPRITES = {
    Player: PLAYERS,
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
