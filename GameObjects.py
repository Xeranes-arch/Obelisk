import copy
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Board import Board  # only used for type hints

# indent_output.py
# import sys

# class Indent:
#     def __init__(self, indent="    "):
#         self.indent = indent
#     def write(self, text):
#         for line in text.splitlines(True):
#             sys.__stdout__.write(self.indent + line)
#     def flush(self):
#         pass

# sys.stdout = Indent()

DELAY = 0
LINE = "\n_________________________\n"


class GameObject:
    def __init__(self, position):
        self.position = position

    def collide_with(self, other, board: "Board"):
        pass

    def collide_with_player(self, other, board: "Board"):
        pass

    def collide_with_rock(self, other, board: "Board"):
        pass

    def find_layer(self, board):
        if self.topside:
            layer = board.top
            initial_layer = board.initial_top
        else:
            layer = board.middle
            initial_layer = board.initial_top
        return layer, initial_layer

    def push(self, other):
        push_direction = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )
        new_self_pos = (
            self.position[0] + push_direction[0],
            self.position[1] + push_direction[1],
        )
        return new_self_pos, push_direction

    def move(self, other, board, target_layer=False):
        # default target layer
        if not target_layer:
            target_layer = board.middle

        layer, ini = other.find_layer(board)
        # Reset old
        board.reset(layer, other.position, ini)
        # Set pos
        other.position = copy.deepcopy(self.position)
        # Set on board
        board.set_element(target_layer, other.position, other)
        # board.display()

### Ground level


class Ground(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "."

    def collide_with_player(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False

    def collide_with_rock(self, other, board):
        self.move(other, board)
        other.topside = False


class Pit(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "x"

    def collide_with_player(self, other, board: "Board"):
        if other.flying:
            self.move(other, board)
        else:
            other.kill(board)

    def collide_with_rock(self, other, board: "Board"):
        other.remove(board)


class Ice(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "□"

    def collide_with_player(self, other, board: "Board"):

        # Move after
        move_again = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )

        # Main move
        self.move(other, board)

        # Take Image for pygame
        board.snapshots.append([copy.deepcopy(board.ground), copy.deepcopy(board.middle), copy.deepcopy(board.top)])
        
        # board.display()
        time.sleep(DELAY)

        flying_flag = False
        if isinstance(other, Player):
            if other.flying:
                flying_flag = True
        if other.topside:
            other.topside = False
        elif flying_flag:
            pass
        else:
            # Next move
            new_pos = tuple(a + b for a, b in zip(move_again, other.position))
            new_pos = board.wrap(new_pos)
            obj = board.get_collision_target(other, new_pos)
            other.collide_with(obj, board)

    def collide_with_rock(self, other, board: "Board"):
        # Move after
        move_again = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )

        # Main move
        self.move(other, board)
        board.display()
        time.sleep(DELAY)
        if other.topside:
            other.topside = False
        else:
            # Next move
            new_pos = tuple(a + b for a, b in zip(move_again, other.position))
            new_pos = board.wrap(new_pos)
            obj = board.get_collision_target(other, new_pos)
            other.collide_with(obj, board)


class Teleporter(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "T"

    def collide_with_player(self, other, board: "Board"):
        if len(board.free_teleporters) == 2:
            board.free_teleporters.remove(self)
            new_pos = board.free_teleporters[0].position
            board.reset(board.middle, other.position, board.initial_middle)
            other.position = new_pos
            board.set_element(board.middle, new_pos, other)
        else:
            self.move(other, board)
        other.topside = False

    def collide_with_rock(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False


class Switch(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "S"

    def collide_with_player(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False

    def collide_with_rock(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False


class Win(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "W"

    def collide_with_player(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False

    def collide_with_rock(self, other, board: "Board"):
        self.move(other, board)
        other.topside = False


### Middle level


class Player(GameObject):

    def __init__(self, position, name=None, repr=None):

        self.position = position
        self.repr = repr
        self.name = name

        # Property for being on top of walls
        self.topside = False
        # Property after kicking off walls, avoids ice and pits
        self.flying = False

    def __str__(self):
        return f"{self.name}"

    def kill(self, board: "Board"):
        # Criterion for game end
        board.players.remove(self)

        # Reset space
        layer, ini = self.find_layer(board)
        board.reset(layer, self.position, ini)

    def collide_with(self, other, board: "Board"):
        board.update_teleporters()
        return other.collide_with_player(self, board)

    def collide_with_player(self, other, board: "Board"):
        if other.topside and not self.topside:
            print(f"{self} got squashed by {other} and died!", LINE)
            self.kill(board)
            self.move(other, board)
            return

        # Next push
        new_self_pos, _ = self.push(other)
        partyB = board.get_collision_target(self, new_self_pos)
        self.collide_with(partyB, board)

    def collide_with_rock(self, other, board: "Board"):
        if other.topside and not self.topside:
            print(f"{self} got squashed by {other} and died!", LINE)
            self.kill(board)
            self.move(other, board)
            return

        # Next push
        new_self_pos, _ = self.push(other)
        partyB = board.get_collision_target(self, new_self_pos)
        self.collide_with(partyB, board)


class Rock(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "R"
        self.topside = False

    def __str__(self):
        return "a rock"

    def collide_with(self, other, board: "Board"):
        board.update_teleporters()
        return other.collide_with_rock(self, board)

    def remove(self, board: "Board"):
        board.rocks.remove(self)

        layer, ini = self.find_layer(board)
        board.reset(layer, self.position, ini)

    def collide_with_player(self, other, board: "Board"):
        # Rocks are walkable
        if other.topside and not self.topside:
            self.move(other, board, board.top)
        else:
            old_pos = copy.deepcopy(self.position)
            # Next push
            new_self_pos, _ = self.push(other)
            partyB = board.get_collision_target(self, new_self_pos)
            self.collide_with(partyB, board)

            if self.position != old_pos and isinstance(
                board.get_element(board.top, old_pos), Rock
            ):
                rock = board.get_element(board.top, old_pos)
                rock.topside = False
                board.set_element(board.top, old_pos, None)
                board.set_element(board.middle, old_pos, rock)

    def collide_with_rock(self, other, board: "Board"):
        if other.topside and not self.topside:
            self.move(other, board, board.top)
        else:
            # Next push
            new_self_pos, _ = self.push(other)
            partyB = board.get_collision_target(self, new_self_pos)
            self.collide_with(partyB, board)


class Wall(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "#"

    def collide_with_player(self, other, board: "Board"):
        # Walk on wall
        if other.topside:
            self.move(other, board, board.top)
        # Wall jump
        elif board.flags["wall_kick"]:
            _, push_dir = self.push(other)
            push_dir = [-1 * i for i in push_dir]
            other.flying = True

            # Make two tumovesns
            for i in range(2):
                time.sleep(DELAY)
                new_pos = (
                    other.position[0] + push_dir[0],
                    other.position[1] + push_dir[1],
                )
                partyB = board.get_collision_target(other, new_pos)
                if not isinstance(partyB, Wall):
                    other.collide_with(partyB, board)
                    # board.display()
                    # time.sleep(DELAY)
                other.flying = False
                if not i:
                    board.snapshots.append([copy.deepcopy(board.ground), copy.deepcopy(board.middle), copy.deepcopy(board.top)])
                        

    def collide_with_rock(self, other, board: "Board"):
        if other.topside:
            self.move(other, board, board.top)


class Gate(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "G"
        self.is_active = True

    def collide_with_player(self, other, board: "Board"):
        if self.is_active:
            if other.topside:
                self.move(other, board, board.top)
        else:
            new_other = board.get_element(board.middle, self.position)
            print("HEERE", new_other)
            exit()
            other.collide_with(new_other, board)

    def collide_with_rock(self, other, board):
        if self.is_active:
            if other.topside:
                self.move(other, board, board.top)
        else:
            self.move(other, board)


### Top level


class RockSpawner(GameObject):
    def __init__(self, position, target):
        super().__init__(position)
        self.repr = "+"
        self.target = target

    def collide_with_player(self, other, board):
        board.spawn_rock()
        board.initial_top.remove(self)
