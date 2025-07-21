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

        self.rocks_to_be_spawned = []
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
            if obj != Rock or self.flags["rocks_spawn"]:
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
            else:
                self.rocks_to_be_spawned = middle_type

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
            self.set_element(self.initial_middle, i, None)
        self.initial_top = copy.deepcopy(self.top)

        # Switch state
        self.switch = False

    def set_element(self, layer, position, obj):
        """Modify layer at position"""
        row, col = self.wrap(position)
        layer[row][col] = obj

    def get_element(self, layer, position):
        """Read layer at position"""
        row, col = self.wrap(position)
        return layer[row][col]

    def get_stack(self, position):
        """Return stack of objects across layers at position"""
        stack = []
        for layer in [self.top, self.middle, self.ground]:
            stack.append(self.get_element(layer, position))
        return stack

    def get_collision_target(self, partyA, new_pos):
        """Scan stack for proper target to execute collision with"""
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
                    if layer[i][j] != None and (
                        not isinstance(layer[i][j], RockSpawner)
                        or self.flags["rocks_spawn"]
                    ):
                        vis[i][j] = layer[i][j].repr
        print("\n")
        for row in vis:
            print(" ".join(row))
        print("\n")

    def spawn_rocks(self):
        """Spawn rocks in middle of Level."""
        for pos in self.rocks_to_be_spawned:
            self.set_element(self.middle, pos, Rock(pos))
            self.rocks.append(self.get_element(self.middle, pos))

    def wrap(self, position):
        """Folding of coordinates"""
        return (position[0] % self.hight, position[1] % self.width)

    def reset(self, layer, position, initial):
        """Reset a a layer at position back to initial value"""
        # WTF is this... Any time you exit a space it will be empty after that. This is just a decrepid bit from when everything in the game was still in one layer...

        # row, col = position
        # # if leaving a Gate (only in middle layer), it must be off, so set None
        # if isinstance(initial[row][col], Gate):
        #     self.set_element(layer, position, None)
        # else:
        #     self.set_element(layer, position, initial[row][col])

        self.set_element(layer, position, None)

    def update_teleporters(self):
        """Updates free teleporters list, so collision with tps can function properly."""
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

    def pit_check(self):
        """
        Players over pits fall in.
        Specifically for the case of wall jumping over pit but being stopped from moving on.
        """
        for p in self.players:
            tile = self.get_element(self.ground, p.position)
            if isinstance(tile, Pit):
                print(LINE, f"\nOh no {p} has fallen into a pit and died!", LINE)
                p.kill(self)

    def fall(self):
        """
        Sets any floating thing to the ground.
        Ensures, that when rock is removed below player/rock, they fall.
        """
        for row in self.top:
            for i in row:
                if i != None and self.get_element(self.middle, i.position) == None:
                    i.topside = False
                    self.set_element(self.middle, i.position, i)
                    self.reset(self.top, i.position, self.initial_top)

    def update_gates(self, flags):
        """
        Handles all gate states as well as objects on them.
        Switch state change is not handled in collisions. Must be called.
        """
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

            # Switch pressed
            if any(ppos in switches_pos for ppos in moveables_pos):
                self.switch = True
            # Switch not pressed
            else:
                self.switch = False

        for gate in self.gates:

            # Find moveable on gate if any
            moveable_on_gate = None
            if gate.position in moveables_pos:
                moveable_on_gate = moveables[moveables_pos.index(gate.position)]
                # print(moveable_on_gate)

            if self.switch:
                gate.is_active = False

                # Remove gate from middle
                middle_element = self.get_element(self.middle, gate.position)
                top_element = self.get_element(self.top, gate.position)
                if isinstance(middle_element, Gate):
                    if isinstance(top_element, Player) or isinstance(top_element, Rock):
                        top_element.topside = False
                    self.set_element(self.middle, gate.position, top_element)
                    self.reset(self.top, gate.position, self.initial_top)

            if not self.switch:
                gate.is_active = True

                # Raise moveable onto gate if gates go up
                if moveable_on_gate:
                    if self.flags["gates_go_up"]:
                        # Do not raise the gate if there are two rocks on top
                        if isinstance(
                            self.get_element(self.top, moveable_on_gate.position), Rock
                        ):
                            pass
                        # Ascenion if Player on Rock on Gate goes up
                        elif isinstance(
                            self.get_element(self.top, moveable_on_gate.position),
                            Player,
                        ) and isinstance(
                            self.get_element(self.middle, moveable_on_gate.position),
                            Rock,
                        ):
                            print(
                                LINE,
                                f"{moveable_on_gate}, ascends into a higher strata and doesn't further asociate with this bs down here.",
                                LINE,
                            )
                            moveable_on_gate.kill(self)
                            # Put gates on middle again
                            self.set_element(self.middle, gate.position, gate)
                        # Just raise it up
                        else:
                            moveable_on_gate.topside = True
                            self.set_element(
                                self.top, moveable_on_gate.position, moveable_on_gate
                            )
                            print("on_gate, flag, no top")
                            self.reset(
                                self.middle,
                                moveable_on_gate.position,
                                self.initial_middle,
                                # Put gates on middle again
                                self.set_element(self.middle, gate.position, gate),
                            )
                            print(self.get_element(self.middle, (5, 1)))

                    # Kill player if gates go down
                    else:
                        if isinstance(moveable_on_gate, Player):
                            self.display()
                            print(self.flags)
                            print(
                                LINE,
                                f"\n{moveable_on_gate} got squashed by a GATE!",
                                LINE,
                            )
                            moveable_on_gate.kill(self)
                            # Put gates on middle again
                            self.set_element(self.middle, gate.position, gate)
                            self.update_gates(flags)
                        elif isinstance(moveable_on_gate, Rock):
                            pass
                        else:
                            # Put gates on middle again
                            self.set_element(self.middle, gate.position, gate)
