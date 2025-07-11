from Board import Board
from GameObjects import *


LINE = "\n_________________________"

# Player properties
PLAYER_NAMES = ["Aelira", "Baelric"]
PLAYER_REPRESENTATIONS = ["A", "B"]


class Level:
    def __init__(self, start_pos, flags):
        self.start_pos = start_pos
        self.flags = flags

    def on_enter(self):
        """Show dialogue or perform actions when the level starts."""
        pass

    def on_event(self):
        """React to custom events during gameplay (optional)."""
        pass


class Level0(Level):

    # Flexibile start position for return levels
    def __init__(self, flags, start_pos=[(5, 5), (5, 6)]):
        super().__init__(start_pos, flags)

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

        # Grounds
        pit_list = [(4, 5),(6,2)]
        ice_list = [(i, 6) for i in range(1, 5)]
        teleporter_list = [(5, 4), (1, 4)]
        win_list = [(7, 5), (6, 6)]
        switch_list = [(0, 6),(7,2)]
        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]

        # Middles
        player_list = []
        rock_list = [(1,3),(2,3),(3,2)]
        wall_list = [(5, 7),(0,2),(1,5)]
        gate_list = [(6, 5),(1,2),(0,4),(0,5),(2,2),(5,2)]
        middles = [player_list, rock_list, wall_list, gate_list]

        # Tops
        rock_spawner_list = [[(5, 7), (1, 1)]]
        tops = [rock_spawner_list]
        # TODO put in boaord init
        self.board = Board(self.flags, width, hight, tiles, middles, tops)

        # Set players
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level1(Level):
    def __init__(self, flags):
        super().__init__([(1, 2), (4, 3)], flags)

    def on_enter(self, board=None):
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

    def setup_board(self):
        width, hight = 8, 8

        pit_list = []
        ice_list = []
        teleporter_list = []
        switch_list = []
        win_list = [(6, 1), (6, 6)]

        wall_list = [
            (i, j) for i in range(8) for j in range(8) if i in [0, 7] or j in [0, 7]
        ]
        gate_list = []

        player_list = []
        rock_list = []

        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]
        middles = [
            player_list,
            rock_list,
            wall_list,
            gate_list,
        ]
        tops = [[]]

        self.board = Board(self.flags, width, hight, tiles, middles, tops)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level2(Level):
    def __init__(self, flags):
        super().__init__([(6, 1), (6, 6)], flags)

    def on_enter(self, board=None):
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

    def setup_board(self):
        width, hight = 8, 8

        pit_list = []
        ice_list = []
        teleporter_list = []
        switch_list = []
        win_list = [(2, 2), (2, 5)]

        wall_list = [(4, i) for i in range(8)]
        gate_list = []

        player_list = []
        rock_list = []

        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]
        middles = [
            player_list,
            rock_list,
            wall_list,
            gate_list,
        ]
        tops = [[]]

        self.board = Board(self.flags, width, hight, tiles, middles, tops)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level3(Level):
    def __init__(self, flags):
        super().__init__([(9, 1), (10, 1)], flags)

    def setup_board(self):
        width, hight = 11, 11

        pit_to_ice = [(1, 2), (8, 4), (7, 6), (3, 8)]
        pit_to_wall = [(1, 4), (8, 6), (7, 8), (3, 10)]

        pit_list = [(i, 2 * n) for i in range(10) for n in range(6)]
        for p in pit_to_ice + pit_to_wall + [(8, 10)]:
            if p in pit_list:
                pit_list.remove(p)

        wall_list = pit_to_wall[:]
        ice_list = [(i, 2 * n + 1) for i in range(10) for n in range(5)] + pit_to_ice

        teleporter_list = []
        switch_list = []
        gate_list = []
        win_list = [(8, 10), (10, 10)]

        player_list = []
        rock_list = []

        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]
        middles = [
            player_list,
            rock_list,
            wall_list,
            gate_list,
        ]
        tops = [[]]

        self.board = Board(self.flags, width, hight, tiles, middles, tops)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level4(Level):
    def __init__(self, flags):
        super().__init__([(0, 3), (4, 5)], flags)

    def setup_board(self):
        width, hight = 7, 5

        pit_list = [(1, 3), (1, 4), (1, 5), (2, 5)]
        wall_list = [(2, 0), (1, 0), (2, 2), (3, 3), (0, 1), (1, 2), (3, 1), (0, 2)]
        ice_list = [(4, i) for i in range(6)]
        teleporter_list = [(3, 2), (2, 1)]
        switch_list = [(3, 5)]
        gate_list = [(0, 4)]
        win_list = [(1, 1), (2, 3)]

        player_list = []
        rock_list = []

        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]
        middles = [
            player_list,
            rock_list,
            wall_list,
            gate_list,
        ]
        tops = [[]]

        self.board = Board(self.flags, width, hight, tiles, middles, tops)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level5(Level):
    def __init__(self, flags):
        super().__init__([(0, 3), (4, 5)], flags)

    def setup_board(self):
        width, hight = 16, 15

        pit_list = [(0, 10), (14, 10)] + [
            (i, j) for i in range(6, 9) for j in [6, 7, 8, 9]
        ]
        wall_list = (
            [(7, i) for i in range(6)]
            + [(7, i + 11) for i in range(6)]
            + [(2, 11), (2, 14)]
        )
        ice_list = [(i, 10) for i in range(1, 14)] + [(5, 14), (2, 9), (2, 8), (2, 7)]
        teleporter_list = [(7, 7), (2, 13)]
        switch_list = [(4, 6)]
        gate_list = [(8, 14), (6, 1)]
        win_list = []

        player_list = []
        rock_list = [
            [(7, 12), (5, 12)],
            [(0, 0), (1, 1)],
        ]

        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]
        middles = [
            player_list,
            rock_list,
            wall_list,
            gate_list,
        ]
        tops = [[[(7, 7), (7, 8)]]]

        self.board = Board(self.flags, width, hight, tiles, middles, tops)
        for i, pos in enumerate(self.start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board
