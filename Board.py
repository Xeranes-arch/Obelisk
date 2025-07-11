import copy

from GameObjects import *

GROUND_OBJECTS = [Pit, Ice, Teleporter, Switch, Win]
MIDDLE_OBJECTS = [Player, Rock, Wall, Gate]
TOP_OBJECTS = [RockSpawner]


class Board:
    def __init__(self, flags, width=10, hight=10, tiles=[], middles=[], tops=[]):

        self.flags = flags

        self.players = []
        self.rocks = []
        self.gates = []
        self.switches = []
        self.teleporters = []
        self.free_teleporters = []
        self.wins = []

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
                temp = obj(pos)
                self.set_element(self.ground, pos, temp)

                # Track switches
                if obj == Switch:
                    self.switches.append(temp)
                if obj == Teleporter:
                    self.teleporters.append(temp)
                if obj == Win:
                    self.wins.append(temp)

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

                # Track players, gates, rocks
                if obj == Player:
                    self.players.append(temp)
                elif obj == Gate:
                    self.gates.append(temp)
                elif obj == Rock:
                    self.rocks.append(temp)

        # Set top layer
        for top_type, obj in zip(tops, TOP_OBJECTS):
            for pos in top_type:
                if obj == RockSpawner:
                    real_pos = pos[0]
                    target = pos[1]
                    self.set_element(self.top, real_pos, obj(real_pos, target))
                else:
                    self.set_element(self.top, pos, obj(pos))

        # Independent copy of initial ground state
        self.initial_ground = copy.deepcopy(self.ground)
        self.initial_middle = copy.deepcopy(self.middle)
        # Account for rocks. Should not respawn.
        for i in middles[1]:
            self.set_element(self.initial_middle,i,None)
        self.initial_top = copy.deepcopy(self.top)

        # Switch state
        self.switch = False

    def set_element(self, layer, position, obj):
        """Modify grid"""
        row, col = self.wrap(position)
        layer[row][col] = obj

    def get_element(self, layer, position):
        """Read grid at position"""
        row, col = self.wrap(position)
        return layer[row][col]

    def get_stack(self, position):
        """Return stack of objects across layers"""
        stack = []
        for layer in [self.top, self.middle, self.ground]:
            stack.append(self.get_element(layer, position))
        return stack

    def get_collision_target(self, partyA, new_pos):
        stack = self.get_stack(new_pos)
        print(stack)
        if not partyA.topside:
            stack.pop(0)
        for obj in stack:
            if obj == None:
                continue
            print(obj)
            return obj

    def display(self):
        """Prints board"""
        vis = [[obj.repr for obj in row] for row in self.ground]
        for layer in [self.middle, self.top]:
            for i in range(self.hight):
                for j in range(self.width):
                    if layer[i][j] != None and (not isinstance(layer[i][j],RockSpawner) or self.flags["rocks_spawn"]):
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
        if isinstance(initial[row][col], Gate):
            self.set_element(layer, position, None)
        else:
            self.set_element(layer, position, initial[row][col])


    def update_teleporters(self):

        t_pos = [i.position for i in self.teleporters]
        pr_pos = [i.position for i in self.players]
        for i in self.rocks:
            pr_pos.append(i.position)

        free_t_pos = []
        for t in t_pos:
            if not t in pr_pos:
                free_t_pos.append(t)
        self.free_teleporters = [
            tp for tp in self.teleporters if tp.position in free_t_pos
        ]

    def update_gates(self, flags):
        players_pos = [i.position for i in self.players]
        gates_pos = [i.position for i in self.gates]
        switches_pos = [i.position for i in self.switches]

        moveables = []
        for i in self.players:
            moveables.append(i)
        for i in self.rocks:
            moveables.append(i)
        moveables_pos = [i.position for i in moveables]

        # Gates without movables
        free_gates_pos = []
        for i in gates_pos:
            if i not in moveables_pos:
                free_gates_pos.append(i)

        for gate in self.gates:
            
            # Find moveable on gate if any
            moveable_on_gate = None
            if gate.position in moveables_pos:
                moveable_on_gate = moveables[moveables_pos.index(gate.position)]


            # Switch pressed
            if any(ppos in switches_pos for ppos in players_pos):
                print("Switch pressed")
                self.switch = True
                gate.is_active = False

                # Lower player to middle
                if moveable_on_gate:
                    moveable_on_gate.topside = False
                    self.set_element(self.middle, moveable_on_gate.position, moveable_on_gate)
                    self.reset(self.top, moveable_on_gate.position, self.initial_top)

                # Remove gates from middle
                if gate.position in free_gates_pos:
                    self.set_element(self.middle,gate.position,None)

            # Switch not pressed
            else:
                self.switch = False
                gate.is_active = True

                # Raise moveable onto gate if gates go up
                if moveable_on_gate:
                    if self.flags["gates_go_up"]:
                        moveable_on_gate.topside = True
                        self.set_element(self.top, moveable_on_gate.position, moveable_on_gate)
                        self.reset(self.middle, moveable_on_gate.position, self.initial_middle)
                        


                    # Kill player if gates go down
                    else:
                        if isinstance(moveable_on_gate,Player): 
                            self.display()
                            print(
                                f"{moveable_on_gate} got squashed by a GATE!",
                                LINE,
                            )
                            moveable_on_gate.kill(self)
                            self.update_gates(flags)
                        else:
                            pass
                # Put gates on middle again
                self.set_element(self.middle,gate.position,gate)