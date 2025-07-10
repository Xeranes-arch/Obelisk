import copy

from GameObjects import *

GROUND_OBJECTS = [Pit, Ice, Teleporter, Switch, Win]
MIDDLE_OBJECTS = [Player, Rock, Wall, Gate]
TOP_OBJECTS = [RockSpawner]


class Board:
    def __init__(self, width=10, hight=10, tiles=[], middles=[], tops=[]):

        self.players = []
        self.rocks = []
        self.gates = []

        # Dimensions
        self.width = width
        self.hight = hight

        # Board layers
        self.ground = [[None for _ in range(width)] for _ in range(hight)]
        self.middle = [[None for _ in range(width)] for _ in range(hight)]
        self.top = [[None for _ in range(width)] for _ in range(hight)]

        # TODO Set all ground tiles from list given by level
        for tile_type, obj in zip(tiles, GROUND_OBJECTS):
            for pos in tile_type:
                self.set_element(self.ground, pos, obj(pos))
        # Set all other ground to Ground
        for i in range(hight):
            for j in range(width):
                if self.ground[i][j] == None:
                    self.set_element(self.ground, (i, j), Ground((i, j)))
        # Set middle layer
        for middle_type, obj in zip(middles, MIDDLE_OBJECTS):
            for pos in middle_type:
                temp = obj(pos)
                self.set_element(self.middle, pos, temp)
                if obj == Player:
                    self.players.append(temp)
                elif obj == Gate:
                    self.gates.append(temp)
                elif obj == Rock:
                    self.rocks.append(temp)
        # Set top layer
        for top_type, obj in zip(tops, TOP_OBJECTS):
            for pos in top_type:
                self.set_element(self.top, pos, obj(pos))

        # Independent copy of initial ground state
        self.initial_ground = copy.deepcopy(self.ground)
        self.initial_middle = copy.deepcopy(self.middle)
        self.initial_top = copy.deepcopy(self.top)

    def set_element(self, layer, position, obj):
        """Modify grid"""
        row, col = self.wrap(position)
        layer[row][col] = obj

    def get_element(self, layer, position):
        """Read grid at position"""
        row, col = self.wrap(position)
        return layer[row][col]

    def display(self):
        """Prints board"""
        vis = [[obj.repr for obj in row] for row in self.ground]
        for layer in [self.middle, self.top]:
            for i in range(self.hight):
                for j in range(self.width):
                    if layer[i][j] != None:
                        vis[i][j] = layer[i][j].repr
        print("\n")
        for row in vis:
            print(" ".join(row))
        print("\n")

    # def spawn_rock(self, current_player, idx):
    #     print(f"{current_player}, kicks loose a rock!")
    #     rock_pos = self.rock_spawners[idx][1]
    #     self.rock_spawners.pop(idx)
    #     self.rocks.append(Rock(rock_pos))
    #     self.set_element(rock_pos, ROCK)

    def wrap(self, position):
        """Board specific folding of coordinates"""
        return (position[0] % self.hight, position[1] % self.width)

    # def find_element(self, repr, grid=None):
    #     """Find positions of elements on grid"""
    #     if not grid:
    #         grid = self.grid
    #     found_positions = []
    #     for i, row in enumerate(grid):
    #         for j, val in enumerate(row):
    #             if val == repr:
    #                 found_positions.append((i, j))
    #     return found_positions

    def reset(self, layer, position, initial):
        """Reset a specific square back to initial value"""
        row, col = position
        self.set_element(layer, position, initial[row][col])

    def update_gates(self):
        players_pos = [i.position for i in self.players]
        gates_pos = [i.position for i in self.gates]

        # Gates without players
        free_gates = []
        for i in gates_pos:
            if i not in players_pos:
                free_gates.append(i)

        for i in gates_pos:

            # Find player on gate if any
            player_on_gate = None
            if i in players_pos:
                player_on_gate = self.players[players_pos.index(i)]

            # Button pressed
            if self.switch:

                # Lower player to ground
                if player_on_gate:
                    player_on_gate.topside = False

                # Set free gates to ground
                if i in free_gates:
                    self.set_element(i, GROUND)

            # Button not pressed
            else:
                # Set free gates to Gate
                if i in free_gates:
                    self.set_element(i, GATE)

                # Raise player onto gate if gates go up
                if player_on_gate:
                    if GAME_FLAGS["gates_go_up"]:
                        player_on_gate.topside = True

                    # Kill player if gates go down
                    else:
                        self.display()
                        print(
                            f"{player_on_gate} got squashed by a GATE!",
                            LINE,
                        )
                        return "died"

    def update(self, current_player: Player = None, old_pos=None, new_pos=None):
        """Handle player-gate overlap??? Alter board state"""

        # Set old player position back to neutral
        if old_pos:
            self.reset(old_pos)
        # Set new player position
        if new_pos:
            self.set_element(new_pos, current_player.repr)
