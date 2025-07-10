import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Board import Board  # only used for type hints


LINE = "\n_________________________"


class GameObject:
    def __init__(self, position):
        self.position = position

    def collide_with(self, other, board: "Board"):
        pass

    def collide_with_player(self, other, board: "Board"):
        pass

    def collide_with_rock(self, other, board: "Board"):
        pass


### Ground level


class Ground(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "."

    def collide_with_player(self, other, board: "Board"):
        other.position = copy.deepcopy(self.position)
        board.set_element(board.middle, other.position, other)


class Pit(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "x"

    def collide_with_player(self, other, board: "Board"):
        print(f"Oh no {other} has fallen into a pit and died!", LINE)
        other.kill(board)


class Ice(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "□"

    def collide_with_player(self, other, board: "Board"):
        pass

    def collide_with_rock(self, other, board: "Board"):
        return super().collide_with_rock(other, board)


class Teleporter(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "T"

    def collide_with_player(self, other, board: "Board"):
        return super().collide_with_player(other, board)

    def collide_with_rock(self, other, board: "Board"):
        return super().collide_with_rock(other, board)


class Switch(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "S"

    def collide_with_player(self, other, board: "Board"):
        return super().collide_with_player(other, board)

    def collide_with_rock(self, other, board: "Board"):
        return super().collide_with_rock(other, board)


class Win(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "W"

    def collide_with_player(self, other, board: "Board"):
        return super().collide_with_player(other, board)

    def collide_with_rock(self, other, board: "Board"):
        return super().collide_with_rock(other, board)


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
        # Specifically to handle landing in walls after a kick and sliding down onto a field
        self.landing = False

    def __str__(self):
        return f"{self.name}"

    def kill(self, board: "Board"):
        board.players.remove(self)

    def collide_with(self, other, board: "Board"):
        return other.collide_with_player(self, board)

    def collide_with_player(self, other, board: "Board"):
        # Try to push the player in the direction the other player is moving
        push_direction = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )
        new_rock_pos = (
            self.position[0] + push_direction[0],
            self.position[1] + push_direction[1],
        )
        obj = board.get_element(board.middle, new_rock_pos)
        obj.collide_with(self, board)

    def collide_with_rock(self, other, board: "Board"):

        push_direction = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )
        new_rock_pos = (
            self.position[0] + push_direction[0],
            self.position[1] + push_direction[1],
        )
        obj = board.get_element(board.middle, new_rock_pos)
        obj.collide_with(self, board)


class Rock(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "R"

    def collide_with(self, other, board: "Board"):
        return other.collide_with_rock(self, board)

    def collide_with_player(self, other, board: "Board"):
        # Try to push the rock in the direction the player is moving
        push_direction = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )
        new_rock_pos = (
            self.position[0] + push_direction[0],
            self.position[1] + push_direction[1],
        )
        obj = board.get_element(board.middle, new_rock_pos)
        obj.collide_with(self, board)

    def collide_with_rock(self, other, board: "Board"):

        push_direction = (
            self.position[0] - other.position[0],
            self.position[1] - other.position[1],
        )
        new_rock_pos = (
            self.position[0] + push_direction[0],
            self.position[1] + push_direction[1],
        )
        obj = board.get_element(board.middle, new_rock_pos)
        obj.collide_with(self, board)


class Wall(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "#"

    def collide_with_player(self, other, board: "Board"):
        pass

    def collide_with_rock(self, other, board: "Board"):
        pass


class Gate(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.repr = "G"
        self.is_active = True

    def collide_with_player(self, other, board: "Board"):
        if self.is_active:
            pass
        else:
            other.position = copy.deepcopy(self.position)
            board.set_element(board.middle, other.position, other)


### Top level


class RockSpawner(GameObject):
    def __init__(self, position, target):
        super().__init__(position)
        self.repr = "+"
        self.target = target

    def collide_with_player(self, other, board):
        board.spawn_rock()
        board.initial_top.remove(self)
