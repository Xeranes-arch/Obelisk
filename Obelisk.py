import copy
import time
import sys
import tty
import termios

LINE = "\n_________________________"

GROUND = "."
PIT = "x"
WALL = "#"
ICE = "□"
TELEPORT = "T"
WIN = "W"
BUTTON = "B"
GATE = "G"
FIELD_TYPES = [PIT, WALL, ICE, TELEPORT, WIN, BUTTON, GATE]

PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]


class Player:
    def __init__(self, name, position=(0, 0)):
        self.name = name
        self.position = position
        self.repr = None

    def __str__(self):
        return f"{self.name}"

    def destroy(self, board):
        board.players.remove(self)


class Board:
    def __init__(self, players, lodtfp, width=10, hight=10):
        # List of players
        self.players = players

        # Dimensions
        self.width = width
        self.hight = hight

        # Grid setup
        self.grid = [[GROUND for _ in range(width)] for _ in range(hight)]

        # Set fields
        for i, j in enumerate(FIELD_TYPES):
            for k in lodtfp[i]:
                self.set_element(k, j)

        # Independent copy of initial state
        self.initial_grid = copy.deepcopy(self.grid)

        # Assigning representations to players
        for idx, i in enumerate(self.players):
            i.repr = str(idx)

        # Drawing them onto board in initial state
        for i in players:
            self.set_element(i.position, i.repr)

        self.button = False  # True for button is pressed

    def display(self):
        """Prints board"""
        print("\n")
        for row in self.grid:
            print(" ".join(row))
        print("\n")

    def wrap(self, position):
        """Board specific folding of coordinates"""
        return (position[0] % self.hight, position[1] % self.width)

    def set_element(self, position, value):
        """Modify grid"""
        row, col = self.wrap(position)
        self.grid[row][col] = value

    def get_element(self, position):
        """Read grid position"""
        row, col = self.wrap(position)
        return self.grid[row][col]

    def find_element(self, repr, grid=None):
        if not grid:
            grid = self.grid
        result = []
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                if val == repr:
                    result.append((i, j))
        return result

    def reset(self, position):
        # Set old player position back to neutral
        row, col = self.wrap(position)
        self.set_element(position, self.initial_grid[row][col])

    def update(self, current_player: Player = None, old_pos=None, new_pos=None):
        # Set old player position back to neutral
        if old_pos:
            self.reset(old_pos)
        # Set new player position
        if new_pos:
            self.set_element(new_pos, current_player.repr)

        # Check for players on gates
        player_pos_list = [i.position for i in self.players]
        gate_list = self.find_element(GATE, self.initial_grid)
        free_gates = []
        for i in gate_list:
            if i not in player_pos_list:
                free_gates.append(i)

        # Set gates
        if self.button:
            for i in free_gates:
                self.set_element(i, GROUND)
        else:
            for i in gate_list:
                self.set_element(i, GATE)
                if i in player_pos_list:
                    self.display()
                    print(
                        f"{self.players[player_pos_list.index(i)]} got squashed by a GATE!",
                        LINE,
                    )
                    return "died"

        self.display()


def get_key():
    """Read a single keypress from stdin and return it."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def prompt_move():
    while True:
        key = get_key()
        for j, i in enumerate(PLAYER_INPUTS):
            if key == i[0]:
                move = (-1, 0)
            elif key == i[1]:
                move = (0, -1)
            elif key == i[2]:
                move = (1, 0)
            elif key == i[3]:
                move = (0, 1)
            elif key == "\x1b":
                print("Exiting.", LINE)
                return None, "Q"
            if key in i:
                current_player_idx = j
        return current_player_idx, move


# def prompt_move(player: Player):
#     """Gets next move."""
#     # Prompt
#     print(f"{player}, pick a move (wasd):")
#     # Try to get a valid move and translate to coordinates
#     while True:
#         move = False
#         read_move = input()
#         if read_move == "":
#             move = (0, 0)
#         if read_move == "w":
#             move = (-1, 0)
#         elif read_move == "a":
#             move = (0, -1)
#         elif read_move == "s":
#             move = (1, 0)
#         elif read_move == "d":
#             move = (0, 1)
#         if move:
#             break
#     return move


def make_move(board: Board, current_player: Player, move, recursion_depth=0):
    """Executes move on board."""

    # Recursion counter to regulate end of turn effects
    recursion_depth += 1

    # Store old position
    old_pos = current_player.position

    # Calculate new position
    new_pos = tuple(a + b for a, b in zip(move, current_player.position))

    # Wrap new position back into board
    new_pos = board.wrap(new_pos)

    # Reused lists for events
    lst_of_player_pos = [i.position for i in board.players]
    list_of_tps = board.find_element(TELEPORT)

    # player collision case
    if new_pos in lst_of_player_pos and new_pos != current_player.position:
        # Find idx of 2nd party
        collision_player_idx = lst_of_player_pos.index(new_pos)
        collision_player = board.players[collision_player_idx]

        move_P2 = tuple(
            -(a - b) for a, b in zip(current_player.position, collision_player.position)
        )
        try:
            make_move(board, collision_player, move_P2, recursion_depth)
        except RecursionError:
            print("Infinite player collision chain. Hell yea!")
            return "collision_chain"

    # wall collision case
    elif new_pos in board.find_element(WALL) or new_pos in board.find_element(GATE):
        ### TODO maybe make this a kick back mechanic to allow two movement in oposite direction

        new_pos = old_pos
        board.update(current_player, old_pos, new_pos)

    # pit case
    elif new_pos in board.find_element(PIT):

        # Delete Player
        current_player.destroy(board)

        # Death message
        print(f"\nOh no! {current_player} died!", LINE)

        # Show one more time
        board.update(current_player, old_pos)
        return "died"

    # Ice case
    elif new_pos in board.find_element(ICE) and new_pos != current_player.position:

        move_again = tuple(-(a - b) for a, b in zip(current_player.position, new_pos))

        # Set new player position
        current_player.position = new_pos

        # Update board
        board.update(current_player, old_pos, new_pos)
        time.sleep(0.3)

        # Make the new move because of ice
        try:
            make_move(board, current_player, move_again, recursion_depth)
        except RecursionError:
            print("Infinite ice slide. Hell yea!")
            return "ice slide"

    # Teleport case
    elif new_pos in list_of_tps:
        try:
            list_of_tps.pop(list_of_tps.index(new_pos))
            new_pos = list_of_tps[0]

        except:
            print("Teleporter doesn't know what to do...\nTeleporter sad :(")

        #####
        current_player.position = new_pos
        board.update(current_player, old_pos, new_pos)

    # Button case
    elif new_pos in board.find_element(BUTTON):
        current_player.position = new_pos
        board.button = True
        print("GATE opened!", LINE)
        board.update(current_player, old_pos, new_pos)

    # Neutral case
    else:
        # Move player
        current_player.position = new_pos

        # Update
        board.update(current_player, old_pos, new_pos)

    recursion_depth -= 1
    # End of turn effects
    if not recursion_depth:

        # Check whether anyone still on button
        if board.button:
            flag = False
            for i in board.players:
                if i.position in board.find_element(BUTTON, board.initial_grid):
                    flag = True
            if not flag:
                board.button = False
                print("GATE closed!", LINE)
                board.update()

    # Win case
    if sorted([i.position for i in board.players]) == sorted(
        board.find_element(WIN, board.initial_grid)
    ):
        board.display()
        print("WIN!!!", LINE)
        return "W"


def level0():

    width = 8
    hight = 8

    pit_list = [(4, 5)]

    wall_list = [(5, 7)]

    ice_list = [(i, 6) for i in range(1, 5)]

    teleport_list = [(5, 4), (1, 4)]

    win_list = [(7, 5), (6, 6)]

    button_list = [(0, 6)]

    gate_list = [(6, 5)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
        button_list,
        gate_list,
    ]

    start_pos = [(5, 5), (5, 6)]
    names = ["Alice", "Bob"]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


def level1():
    width = 8
    hight = 8

    pit_list = []

    wall_list = []

    ice_list = []

    teleport_list = []

    win_list = [(6, 1), (6, 6)]

    button_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
        button_list,
        gate_list,
    ]

    start_pos = [(0, 3), (4, 5)]
    names = ["Alice", "Bob"]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


def level2():

    width = 8
    hight = 8

    pit_list = []

    wall_list = []

    ice_list = []

    teleport_list = []

    win_list = [(6, 1), (6, 6)]

    button_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
        button_list,
        gate_list,
    ]

    start_pos = [(0, 3), (4, 5)]
    names = ["Alice", "Bob"]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


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

    teleport_list = []

    win_list = [(8, 10), (10, 10)]

    button_list = []

    gate_list = []

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
        button_list,
        gate_list,
    ]
    names = ["Alice", "Bob"]
    start_pos = [(9, 1), (10, 1)]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


def level4():

    width = 7
    hight = 5

    pit_list = [(1, 3), (1, 4), (1, 5), (2, 5)]

    wall_list = [(2, 0), (1, 0), (2, 2), (3, 3), (0, 1), (1, 2), (3, 1), (0, 2)]

    ice_list = [(4, i) for i in range(6)]

    teleport_list = [(3, 2), (2, 1)]

    win_list = [(1, 1), (2, 3)]

    button_list = [(3, 5)]

    gate_list = [(0, 4)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
        button_list,
        gate_list,
    ]

    start_pos = [(0, 3), (4, 5)]
    names = ["Alice", "Bob"]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


def main_menu(unlocked_levels):
    lv_list = [level0(), level1(), level2(), level3(), level4()]
    while True:
        try:
            print("Pick a level:")
            for i in range(unlocked_levels):
                print(f"level{i+1}")
            lv = input()
            if lv == "":
                lv = 0
                break
            elif int(lv) - 1 in range(unlocked_levels):
                lv = int(lv)
                break
        except:
            pass

    lodtfp, width, hight, start_pos, names = lv_list[lv]

    Ps = []
    for i in range(len(names)):
        Ps.append(Player(names[i], start_pos[i]))
    B = Board(Ps, lodtfp, width, hight)
    B.display()

    # Play
    while True:
        current_player_idx, move = prompt_move()
        if move == "Q":
            return False
        current_player = B.players[current_player_idx]
        exit_status = make_move(B, current_player, move)
        if exit_status == "W" and lv == unlocked_levels:
            return True
        elif exit_status != None:
            return False


def main():
    unlocked_levels = 1
    while True:
        unlock_next = main_menu(unlocked_levels)
        if unlock_next:
            unlocked_levels += 1


if __name__ == "__main__":
    main()


### TODO werid tp level where blocking one of three allows the remaining one to function
