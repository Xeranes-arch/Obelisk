from Board import Board
from GameObjects import *
import pygame
if TYPE_CHECKING:
    from Obelisk import Game, Renderer  # only used for type hints

LINE = "\n_________________________\n"
CON = "press enter to continiue"

# Player properties
PLAYER_NAMES = ["Aelira", "Baelric"]
PLAYER_REPRESENTATIONS = ["A", "B"]


GROUND_OBJECTS = [Pit, Ice, Teleporter, Switch, Win]
MIDDLE_OBJECTS = [Player, Rock, Wall, Gate]
TOP_OBJECTS = []


class Level:
    def __init__(self):
        # Nr of transformations to be done - count down by one each time transform is done until 0
        self.transformations = 0
        # Power ups that change mechanics
        self.flags = {
            "gates_go_up": False,
            "wall_kick": False,
        }
        self.transform_dict = {}
        self.win_msg = "\nDONE!!!\n"

    def __repr__(self):
        return self.__class__.__name__

    def empty_elements(self):
        list = []
        for type in [GROUND_OBJECTS, MIDDLE_OBJECTS, TOP_OBJECTS]:
            lst = []
            for _ in GROUND_OBJECTS:
                lst.append([])
            list.append(lst)
        return list

        return []

    def on_enter(self,game):
        """Show dialogue or perform actions when the level starts."""
        pass

    def transform(self, new_flags):
        """Transform level to different powerups/objects."""
        pass

    def end(self):
        pass

    def laser(self):
        print(LINE, "\nA laser completely incinerates Aelira and Baelric!" + LINE)
        self.enter()

    def enter(self):
        print(LINE)
        input("press enter to continue")


class Level0(Level):

    # Flexibile start position for return levels
    def __init__(self):
        super().__init__()

    def on_enter(self,game):
        """Run start up sequence/dialgue."""
        print(LINE, "\nCongratz. You've found the bug checking site!" + LINE)

    def setup_board(self):
        # Geometry inflexible
        width = 15
        hight = 15

        start_pos = [(5, 5), (5, 6)]

        # Grounds
        pit_list = [(4, 5), (6, 2)]
        ice_list = [(i, 6) for i in range(1, 5)]
        teleporter_list = [(5, 4), (1, 4)]
        win_list = [(7, 5), (6, 6)]
        switch_list = [(0, 6), (7, 2), (11, 11)]
        tiles = [
            pit_list,
            ice_list,
            teleporter_list,
            switch_list,
            win_list,
        ]

        # Middles
        player_list = []
        rock_list = [(1, 3), (2, 3), (3, 2), (10, 10), (10, 9)]
        wall_list = [(5, 7), (0, 2), (1, 5), (12, 12)]
        gate_list = [(6, 5), (1, 2), (0, 4), (0, 5), (2, 2), (5, 2), (11, 12), (12, 11)]
        middles = [player_list, rock_list, wall_list, gate_list]

        # Tops
        tops = []
        # TODO put in boaord init
        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)

        # Set players
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level1(Level):
    def __init__(self):
        super().__init__()

    def on_enter(self,game: "Game"):
        # Game intro
        text = (
            LINE
            + "\nAelira and Baelric on the run from the Obelisk, step through the stone archway covered by darkness and find themselves in an empty square stone room. The archway slams shut behind them!\nTheir companions are still fighting the Obelisk so the Heroes better hurry to figure out how to disable it!"
            + LINE
            + CON
        )
        game.renderer.draw_text(text)



        # fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        # pygame.event.post(fake_event)

    def setup_board(self):
        width, hight = 8, 8

        start_pos = [(1, 2), (2, 4)]

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

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

    def end(self):
        # Riddle 1
        i = 0
        lst = ["", "*correctly*"]
        while True:
            print(
                LINE,
                f"\nBefore they proceed, Aelira and Baelric must {lst[i]} answer a riddle.\nWhat should every Hitchhiker be sure to bring?\na - A towel\nb - A beloved friend",
                LINE,
            )
            if input() == "a":
                print("Correct!" + LINE)
                break
            else:
                print("No! WRONG! INCORRECT!!!")
                self.laser()
                i = 1


class Level2(Level):
    def __init__(self):
        super().__init__()

    def on_enter(self,game):
        print(
            "\nSuddenly the room comes alive and completely restructures itself. Some of the ground and all the walls fall away.\nIn place of the Walls appear identical rooms with identical Aeliras and Baelrics.\nWtf"
        )
        self.enter()

    def setup_board(self):
        width, hight = 8, 8

        start_pos = [(6, 1), (6, 6)]
        pit_list = [(4, i) for i in range(8)]
        ice_list = []
        teleporter_list = []
        switch_list = []
        win_list = [(2, 2), (2, 5)]

        wall_list = []
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

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

    def end(self):
        # Riddle 2
        while True:
            print(
                LINE,
                "\nBefore they proceed, Aelira and Baelric must\nagain answer a riddle.\nWhat is the objectively superior condiment?\na - Ketchup\nb - Mayonaise",
                LINE,
            )
            if input() == "b":
                print("Correct!" + LINE)
                break
            else:
                print("No! WRONG! INCORRECT!!!")
                self.laser()


class Level3(Level):
    """Pits and Ice"""

    def __init__(self):
        super().__init__()

    def on_enter(self,game, board=None):
        print("\nParts of the ground freeze over and next to Aelira a Switch appears.")
        self.enter()

    def setup_board(self):
        width, hight = 8, 8

        start_pos = [(2, 2), (2, 5)]

        pit_list = [(2, 0), (3, 0), (6, 0), (5, 0), (5, 7)] + [
            (j, i) for i in range(2, 6) for j in [0, 1, 3, 5, 7]
        ]
        wall_list = [(0, 1), (0, 0), (1, 0), (4, 0), (5, 1), (7, 7), (0, 6)] + [
            (i, 7) for i in range(4)
        ]
        ice_list = (
            [(i, 1) for i in range(2, 5)]
            + [(4, i) for i in range(2, 7)]
            + [(7, 6)]
            + [(6, i) for i in range(2, 7)]
        )
        teleporter_list = []
        switch_list = [(1, 1), (7, 0)]
        gate_list = [(5, 6), (4, 7)]
        win_list = [(6, 1), (7, 1)]

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
        tops = []

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

    def end(self):
        # Riddle 3
        while True:
            print(
                LINE,
                "\nBefore they proceed, Aelira and Baelric must\nagain answer a riddle.\nDoes pineapple belong on Pizza?\na - Yes\nb - No",
                LINE,
            )
            if input() == "a":
                print("Correct!" + LINE)
                break
            else:
                print(
                    "Only those weak of mind close themselves off from greatness.\nHarharhar!"
                )
                self.laser()


class Level4(Level):
    def __init__(self):
        super().__init__()

    def setup_board(self):
        width, hight = 11, 11

        start_pos = [(9, 1), (10, 1)]

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

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

    def end(self):
        # Riddle 4
        for i in ["cereal", "a smoothy", "a salad", "everything"]:
            if i == "everything":
                j = "bucket"
            else:
                j = "soup"
            while True:
                print(
                    LINE,
                    f"\nBefore they proceed, Aelira and Baelric must\nagain answer a riddle.\nIs {i} a {j}?\na - Yes\nb - No",
                    LINE,
                )
                if input() == "a":
                    print("Correct!" + LINE)
                    break
                else:
                    print("Soup is a scam...")
                    self.laser()


class Level5(Level):
    def __init__(self):
        super().__init__()

    def setup_board(self):
        width, hight = 7, 5

        start_pos = [(3, 6), (4, 6)]

        pit_list = [(1, 3), (1, 4), (1, 5), (2, 5)]
        wall_list = [(2, 0), (1, 0), (2, 2), (3, 3), (0, 1), (1, 2), (3, 1), (0, 2)]
        ice_list = [(4, i) for i in range(6)]
        teleporter_list = [(3, 2), (2, 1)]
        switch_list = [(0, 3)]
        gate_list = [(3, 5)]
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

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

    def end(self):
        # Riddle 5
        i = 0
        print(LINE, "\nBefre the prosed, Aevnoa and Baelric must\nagin b rid.")
        while True:
            print(
                "Why oövicah sa jk HREeAAN?\n----.---\nbael##+Ǵ",
                LINE,
            )
            input()
            if i == 1:
                break
            else:
                print("The Obe#### i# ### ##er")
                i += 1


class Level6(Level):
    def __init__(self):
        super().__init__()
        self.transformations = 1

        # Power ups that change mechanics
        self.flags = {
            "gates_go_up": False,
            "wall_kick": False,
        }

    def setup_board(self):
        width, hight = 16, 15

        start_pos = [(0, 3), (4, 4)]
        pit_list = (
            [
                (0, 10),
                (14, 10),
                (0, 5),
                (10, 4),
                (14, 5),
                (7, 6),
                (7, 9),
                (8, 15),
                (13, 5),
                (7, 0),
                (13, 12),
                (12, 14),
                (9, 7),
                (6, 12),
                (10, 7),
                (10, 3),
            ]
            + [(i, 15) for i in range(9, 15)]
            + [(i, 15) for i in range(7)]
            + [(i, j) for i in [6, 8] for j in [6, 7, 8, 9]]
            + [(8, i) for i in range(11, 14)]
        )

        wall_list = (
            [(7, i) for i in range(1, 3)]
            + [
                (7, 11),
                (7, 4),
                (6, 14),
                (14, 9),
                (10, 12),
                (14, 7),
                (14, 8),
                (11, 3),
                (8, 4),
                (11, 8),
                (0, 14),
                (0, 4),
                (9, 8),
                (0, 1),
                (14, 1),
            ]
            + [(i, 7) for i in range(11, 13)]
            + [(14, i) for i in range(11, 15)]
            + [(i, 12) for i in range(1, 5)]
            + [(13, i) for i in range(4)]
        )
        ice_list = [(i, j) for i in range(1, 13) for j in [5, 10]] + [
            (7, 14),
            (13, 10),
            (0, 13),
            (13, 13),
        ]
        teleporter_list = [(3, 3), (4, 3), (3, 13), (1, 1)]
        switch_list = [(4, 6), (13, 8), (13, 4), (2, 13)]
        gate_list = [(5, 1), (13, 7), (11, 4), (5, 12), (0, 0)]
        win_list = [(14, 0), (13, 14)]

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
        tops = []

        win_msg = str(
            LINE
            + "\nThe entire Dungeon starts shaking. Is it done?\nCracks form all over the room and chunks fall from it. The Gates start malfunctioning and start raising from the ground to shut passages instead of coming down from the ceiling.\n A siren blares: NO PASSAGE PRotednfvk the hiden swi ELIMINATE THe the island in the center KILL THE INTRUDERS. \nAmidst this chaos a faint glow envelops the heroes to protect them from the rubble. The blessing coalesces into their boot enabeling them to wall jump.\nThe shaking dies down but nothing else happens..."
            + LINE
            + CON,
        )

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)

        self.board.flags = self.flags
        self.board.win_msg = win_msg

        return self.board

    def transform(self):

        # New win message
        self.board.win_msg = (
            LINE
            + LINE
            + "\nYOU'VE DONE IT!!!\nThe entire system shuts down and the archway of darkness opens up again.\nOutside, the Obelisk falls silent at last."
        )

        # Change Powerups
        self.flags["gates_go_up"] = True
        self.flags["wall_kick"] = True

        # Remove Elements
        for i in self.board.wins:
            self.board.set_element(self.board.ground, i.position, Ground(i.position))
        self.board.wins = []

        # Spawn Elements
        rock_list = [(11, 12), (5, 8), (6, 2), (12, 4), (12, 5)]
        elements = self.empty_elements()
        elements[1][1] = rock_list
        self.board.set_many(elements)

        # Only create the win con without setting visible tiles
        self.board.wins = [Win((7, 7)), Win((7, 8))]


class Level7(Level):
    # Flexibile start position for return levels
    def __init__(self):
        super().__init__()
        self.flags = {
            "gates_go_up": True,
            "wall_kick": True,
        }

    def setup_board(self):
        width, hight = 10, 4

        start_pos = [(0, 0), (2, 0)]

        pit_list = [(2, 7), (2, 8), (2, 9), (0, 8)]
        wall_list = [(0, 7), (0, 9), (1, 7), (1, 9)]
        ice_list = []
        teleporter_list = []
        switch_list = [(1, 0)]
        gate_list = [(1, 1)]
        win_list = [(1, 8), (3, 8)]

        player_list = []
        rock_list = [(1, 3), (1, 2)]

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
        tops = []

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board


class Level8(Level):
    # Flexibile start position for return levels
    def __init__(self):
        super().__init__()
        self.flags = {
            "gates_go_up": True,
            "rocks_spawn": True,
            "wall_kick": True,
        }

    def setup_board(self):
        width, hight = 10, 7

        start_pos = [(0, 0), (2, 0)]

        pit_list = [(2, 7), (2, 8), (2, 9), (3, 9), (3, 5), (2, 5), (2, 6), (0, 8)] + [
            (4, i) for i in range(5, 10)
        ]
        wall_list = [(0, 7), (0, 9), (1, 7), (1, 9)]
        ice_list = []
        teleporter_list = [(1, 8), (3, 6), (6, 0)]
        switch_list = [(1, 0)]
        gate_list = [(1, 2)]
        win_list = [(3, 7), (3, 8)]

        player_list = []
        rock_list = [(1, 3), (1, 4), (0, 2), (1, 1)]

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
        tops = []

        elements = [tiles, middles, tops]
        self.board = Board(self.flags, width, hight, elements)
        for i, pos in enumerate(start_pos):
            P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
            self.board.set_element(self.board.middle, pos, P)
            self.board.players.append(P)
        return self.board

        # class Levelo6_the_way_we_played_at_party(Level):
        #     def __init__(self, flags):
        #         super().__init__([(0, 3), (4, 4)], flags)

        #     def end(self):
        #         print(
        #             LINE,
        #             "\nThe entire Dungeon starts shaking. Is it done?\nCracks form all over the room and chunks fall from it. The Gates start malfunctioning and start raising from the ground to shut passages instead of coming down from the ceiling.\n A siren blares: NO PASSAGE PRotednfvk the hiden swi ELIMINATE THe the island in the center KILL THE INTRUDERS. \nAmidst this chaos a faint glow envelops the heroes to protect them from the rubble. The blessing coalesces into their boot enabeling them to wall jump.\nThe shaking dies down but nothing else happens...",
        #             LINE,
        #         )
        #         self.enter()

        #     def setup_board(self):
        #         width, hight = 16, 15

        #         pit_list = (
        #             [
        #                 (0, 10),
        #                 (14, 10),
        #                 (0, 5),
        #                 (10, 4),
        #                 (14, 5),
        #                 (7, 6),
        #                 (7, 9),
        #                 (8, 15),
        #                 (13, 5),
        #                 (7, 0),
        #                 (13, 12),
        #                 (12, 14),
        #             ]
        #             + [(i, 15) for i in range(7)]
        #             + [(i, j) for i in [6, 8] for j in [6, 7, 8, 9]]
        #             + [(8, i) for i in range(11, 14)]
        #         )

        #         wall_list = (
        #             [(7, i) for i in range(1, 3)]
        #             + [
        #                 (7, 11),
        #                 (7, 4),
        #                 (6, 14),
        #                 (14, 9),
        #                 (10, 12),
        #                 (14, 7),
        #                 (14, 8),
        #                 (11, 3),
        #                 (8, 4),
        #                 (11, 8),
        #                 (0, 14),
        #                 (6, 12),
        #                 (0, 4),
        #                 (9, 8),
        #                 (0, 1),
        #                 (14, 1),
        #             ]
        #             + [(i, 7) for i in range(9, 13)]
        #             + [(i, 15) for i in range(9, 15)]
        #             + [(14, i) for i in range(11, 15)]
        #             + [(i, 12) for i in range(1, 5)]
        #             + [(13, i) for i in range(4)]
        #         )
        #         ice_list = [(i, j) for i in range(1, 13) for j in [5, 10]] + [
        #             (7, 14),
        #             (13, 10),
        #             (0, 13),
        #             (13, 13),
        #         ]
        #         teleporter_list = [(3, 3), (4, 3), (3, 13), (1, 1)]
        #         switch_list = [(4, 6), (13, 8), (13, 4), (2, 13)]
        #         gate_list = [(5, 1), (13, 7), (11, 4), (5, 12), (0, 0)]
        #         win_list = [(14, 0), (13, 14)]

        #         player_list = []
        #         rock_list = [(11, 12), (5, 8), (6, 2), (12, 4), (12, 5)]

        #         tiles = [
        #             pit_list,
        #             ice_list,
        #             teleporter_list,
        #             switch_list,
        #             win_list,
        #         ]
        #         middles = [
        #             player_list,
        #             rock_list,
        #             wall_list,
        #             gate_list,
        #         ]
        #         tops = []

        elements = [tiles, middles, tops]
        #         self.board = Board(self.flags, width, hight, elements)
        #         for i, pos in enumerate(self.start_pos):
        #             P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
        #             self.board.set_element(self.board.middle, pos, P)
        #             self.board.players.append(P)
        #         return self.board

        # class Level_preset(Level):
        #     # Flexibile start position for return levels
        #     def __init__(self):
        #         super().__init__(start_pos)

        #     def on_enter(self,game):
        #         """Run start up sequence/dialgue."""
        #         print(LINE, "\nPRESET"+ LINE)

        #     def setup_board(self):
        #         width, hight = 10, 10

        #         start_pos=[(0, 0), (0, 1)]
        #         pit_list = []
        #         wall_list = []
        #         ice_list = []
        #         teleporter_list = []
        #         switch_list = []
        #         gate_list = []
        #         win_list = []

        #         player_list = []
        #         rock_list = []

        #

        #         tiles = [
        #             pit_list,
        #             ice_list,
        #             teleporter_list,
        #             switch_list,
        #             win_list,
        #         ]
        #         middles = [
        #             player_list,
        #             rock_list,
        #             wall_list,
        #             gate_list,
        #         ]
        #         tops = []

        elements = [tiles, middles, tops]


#         self.board = Board(self.flags, width, hight, elements)
#         for i, pos in enumerate(start_pos):
#             P = Player(pos, PLAYER_NAMES[i], PLAYER_REPRESENTATIONS[i])
#             self.board.set_element(self.board.middle, pos, P)
#             self.board.players.append(P)
#         return self.board
