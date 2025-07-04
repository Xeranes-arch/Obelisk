import copy


GROUND = "."
PIT = "x"
WALL = "#"
ICE = "□"
TELEPORT = "T"
WIN = "W"
FIELD_TYPES = [PIT, WALL, ICE, TELEPORT, WIN]


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


def prompt_move(player: Player):
    """Gets next move."""
    # Prompt
    print(f"{player}, pick a move (wasd):")
    # Try to get a valid move and translate to coordinates
    while True:
        move = False
        read_move = input()
        if read_move == "":
            move = (0, 0)
        if read_move == "w":
            move = (-1, 0)
        elif read_move == "a":
            move = (0, -1)
        elif read_move == "s":
            move = (1, 0)
        elif read_move == "d":
            move = (0, 1)
        if move:
            break
    return move


def make_move(board: Board, current_player: Player, move):
    """Executes move on board."""
    # Calculate new position
    new_pos = tuple(a + b for a, b in zip(move, current_player.position))

    # Wrap new position back into board
    new_pos = board.wrap(new_pos)

    # Required lists for events
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
            make_move(board, collision_player, move_P2)
        except RecursionError:
            print("Infinite player collision chain. Hell yea!")

    # wall collision case
    elif new_pos in board.find_element(WALL):
        ### TODO maybe make this a kick back mechanic to allow two movement in oposite direction
        pass

    # pit case
    elif new_pos in board.find_element(PIT):
        # Set old player position back to neutral
        board.reset(current_player.position)
        # Delete Player
        current_player.destroy(board)

        print(f"\nOh no! {current_player} died!")

    # Ice case
    elif new_pos in board.find_element(ICE) and new_pos != current_player.position:
        # Set old player position back to neutral
        board.reset(current_player.position)

        move_again = tuple(-(a - b) for a, b in zip(current_player.position, new_pos))

        # Set new player position
        current_player.position = new_pos

        # Show new Player position on board
        board.set_element(current_player.position, current_player.repr)

        # Make the new move because of ice
        try:
            make_move(board, current_player, move_again)
        except RecursionError:
            print("Infinite ice slide. Hell yea!")
            exit()

    # Teleport case
    elif new_pos in list_of_tps:
        # Set old player position back to neutral
        board.reset(current_player.position)

        list_of_tps.pop(list_of_tps.index(new_pos))
        new_pos = list_of_tps[0]
        board.set_element(new_pos, current_player.repr)
        current_player.position = new_pos

    # Neutral case
    else:
        # Set old player position back to neutral
        board.reset(current_player.position)

        # Move player
        current_player.position = new_pos

        # Show new Player position on board
        board.set_element(current_player.position, current_player.repr)

    # Win case: all player positions match positions of win on initial board
    if [i.position for i in board.players] == board.find_element(
        WIN, board.initial_grid
    ):
        board.display()
        print("WIN!!!\n_________________________")
        main()


def level0():

    width = 8
    hight = 8

    pit_list = []

    wall_list = []

    ice_list = []

    teleport_list = []

    win_list = [(6, 1), (6, 6)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
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

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
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
    [pit_list.remove(i) for i in pit_to_ice]
    [pit_list.remove(i) for i in pit_to_wall]
    pit_list.remove((8, 10))

    wall_list = []
    [wall_list.append(i) for i in pit_to_wall]

    ice_list = [(i, 2 * n + 1) for i in range(10) for n in range(5)]
    [ice_list.append(i) for i in pit_to_ice]

    teleport_list = []

    win_list = [(8, 10), (10, 10)]

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
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

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
    ]

    start_pos = [(0, 3), (4, 5)]
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

    # lodtfp
    list_of_diff_type_field_positions = [
        pit_list,
        wall_list,
        ice_list,
        teleport_list,
        win_list,
    ]

    start_pos = [(0, 3), (4, 5)]
    names = ["Alice", "Bob"]
    return list_of_diff_type_field_positions, width, hight, start_pos, names


def main():
    lv_list = [level0(), level1(), level2(), level3(), level4()]
    print("Pick a level 0-4:")
    lv = int(input())
    lodtfp, width, hight, start_pos, names = lv_list[lv]

    Ps = []
    for i in range(len(names)):
        Ps.append(Player(names[i], start_pos[i]))
    B = Board(Ps, lodtfp, width, hight)
    B.display()

    while True:
        # Detect if everyone is dead
        if not len(B.players):
            print("EVERYONE IS DEAD AAAAAAAAAAAAAAAAAAA")
            exit()

        for current_player in B.players[:]:
            for _ in range(1):
                # Start of a turn
                if current_player not in B.players:
                    break
                move = prompt_move(current_player)
                make_move(B, current_player, move)
                B.display()


if __name__ == "__main__":
    main()
