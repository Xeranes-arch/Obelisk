from Board import Board
from GameObjects import *


LINE = "\n_________________________"

# Player properties
PLAYER_NAMES = ["Aelira", "Baelric"]
PLAYER_REPRESENTATIONS = ["A", "B"]


class Level:
    def __init__(self, start_pos):
        self.start_pos = start_pos

    def setup(self, board):
        """Place objects, set up the board. Override in subclasses."""
        pass

    def on_enter(self, board):
        """Show dialogue or perform actions when the level starts."""
        pass

    def on_event(self, board, event):
        """React to custom events during gameplay (optional)."""
        pass


class Level0(Level):

    # Flexibile start position for return levels
    def __init__(self, start_pos=[(5, 5), (5, 6)]):
        super().__init__(start_pos)

    def on_enter(self):
        """Run start up sequence/dialgue."""
        print(LINE, "\nCongratz. You've found the bug checking site!", LINE)

    def check_for_events(self, board):
        """Check for level specific events like powerups or first time learn effect dialouge"""
        pass

    def setup_board(self):
        # Geometry inflexible
        width = 8
        hight = 8

        pit_list = [(4, 5)]
        ice_list = [(i, 6) for i in range(1, 5)]
        teleporter_list = [(5, 4), (1, 4)]
        win_list = [(7, 5), (6, 6)]
        switch_list = [(0, 6)]
        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]

        wall_list = [(5, 7)]
        gate_list = [(6, 5)]

        # TODO put in boaord init
        self.board = Board(width, hight, tiles)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


def level1():
    i = 0
    lst = ["", "*correctly*"]
    while True:
        print(
            LINE,
            f"\nBefore they proceed, Aelira and Baelric must {lst[i]} answer a riddle.\nWhat should every Hitchhiker be sure to bring?\na - A towel\nb - A beloved friend",
            LINE,
        )
        if input() == "a":
            print("Correct!", LINE)
            break
        else:
            print("No! WRONG! INCORRECT!!!")
            i = 1

    print(
        "\nAelira and Baelric figure out they can move around with wasd and ijkl respectively (ESC for back to main menu).\nWhat might be the thing they have to do?"
    )

    width = 8
    hight = 8

    pit_list = []

    wall_list = []
    for i in range(8):
        wall_list.append((0, i))
        wall_list.append((7, i))
        wall_list.append((i, 0))
        wall_list.append((i, 7))

    ice_list = []

    teleporter_list = []

    win_list = [(6, 1), (6, 6)]

    switch_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleporter_list,
        win_list,
        switch_list,
        gate_list,
    ]

    start_pos = [(1, 2), (4, 3)]
    return list_of_diff_type_field_positions, width, hight, start_pos


def level2():
    while True:
        print(
            LINE,
            "\nBefore they proceed, Aelira and Baelric must again answer a riddle.\nWhat is the objectively superior condiment?\na - Ketchup\nb - Mayonaise",
            LINE,
        )
        if input() == "b":
            print("Correct!", LINE)
            break
        else:
            print("No! WRONG! INCORRECT!!!")

    print(
        "\nSuddenly the walls fall away.\nIn their place appear identical rooms with identical Aeliras and Baelrics.\nWtf"
    )

    width = 8
    hight = 8

    pit_list = []

    wall_list = [(4, i) for i in range(8)]

    ice_list = []

    teleporter_list = []

    win_list = [(2, 2), (2, 5)]

    switch_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleporter_list,
        win_list,
        switch_list,
        gate_list,
    ]

    start_pos = [(6, 1), (6, 6)]
    return list_of_diff_type_field_positions, width, hight, start_pos


def level3():

    width = 11
    hight = 11

    pit_to_ice = [(1, 2), (8, 4), (7, 6), (3, 8)]
    pit_to_wall = [(1, 4), (8, 6), (7, 8), (3, 10)]

    pit_list = [(i, 2 * n) for i in range(10) for n in range(6)]
    for i in pit_to_ice:
        pit_list.remove(i)
    for i in pit_to_wall:
        pit_list.remove(i)
    pit_list.remove((8, 10))

    wall_list = [i for i in pit_to_wall]

    ice_list = [(i, 2 * n + 1) for i in range(10) for n in range(5)]
    for i in pit_to_ice:
        ice_list.append(i)

    teleporter_list = []

    win_list = [(8, 10), (10, 10)]

    switch_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleporter_list,
        win_list,
        switch_list,
        gate_list,
    ]
    start_pos = [(9, 1), (10, 1)]
    return list_of_diff_type_field_positions, width, hight, start_pos


def level4():

    width = 7
    hight = 5

    pit_list = [(1, 3), (1, 4), (1, 5), (2, 5)]

    wall_list = [(2, 0), (1, 0), (2, 2), (3, 3), (0, 1), (1, 2), (3, 1), (0, 2)]

    ice_list = [(4, i) for i in range(6)]

    teleporter_list = [(3, 2), (2, 1)]

    win_list = [(1, 1), (2, 3)]

    switch_list = [(3, 5)]

    gate_list = [(0, 4)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleporter_list,
        win_list,
        switch_list,
        gate_list,
    ]

    start_pos = [(0, 3), (4, 5)]
    return list_of_diff_type_field_positions, width, hight, start_pos


def level5():

    # print("It looks only have complete with random elements strewn about.")

    width = 16
    hight = 15

    pit_list = [(0, 10), (14, 10)]
    for i in range(6, 9):
        pit_list.append((6, i))
        pit_list.append((8, i))
        pit_list.append((i, 6))
        pit_list.append((i, 9))

    wall_list = []
    for i in range(6):
        wall_list.append((7, i))
        wall_list.append((7, i + 11))

    wall_list.append((2, 11))
    wall_list.append((2, 14))

    ice_list = [(i, 10) for i in range(1, 14)]
    ice_list.append((5, 14))

    ice_list.append((2, 9))
    ice_list.append((2, 8))
    ice_list.append((2, 7))

    teleporter_list = [(7, 7)]

    teleporter_list.append((2, 13))

    win_list = []

    switch_list = [(4, 6)]

    gate_list = [(8, 14), (6, 1)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleporter_list,
        win_list,
        switch_list,
        gate_list,
    ]

    swin_list = [(7, 7), (7, 8)]
    loose_rock_list = [[(7, 12), (5, 12)], [(0, 0), (1, 1)]]
    # secret list
    secret_list = [swin_list, loose_rock_list]

    start_pos = [(0, 3), (4, 5)]
    return list_of_diff_type_field_positions, secret_list, width, hight, start_pos


### Build last level without achievable WIN or even fake one, or one that grants the powerup but no win
