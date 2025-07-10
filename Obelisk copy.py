import copy
import time
import sys
import tty
import termios

from levels import *

# Constants
DELAY = 0.3
LINE = "\n_________________________"

# Field type representations
GROUND = "."
PIT = "x"
WALL = "#"
ICE = "□"
TELEPORT = "T"
WIN = "W"
SWITCH = "S"
GATE = "G"
FIELD_TYPES = [PIT, WALL, ICE, TELEPORT, WIN, SWITCH, GATE]

# Secrets
LOOSE_ROCK = "+"
ROCK = "R"


# Player properties
PLAYER_NAMES = ["Aelira", "Baelric"]
PLAYER_REPRESENTATIONS = ["A", "B"]

PLAYER1_INPUTS = ["w", "a", "s", "d"]
PLAYER2_INPUTS = ["i", "j", "k", "l"]

PLAYER_INPUTS = [PLAYER1_INPUTS, PLAYER2_INPUTS]

# Power ups that change mechanics
GAME_FLAGS = {
    "gates_go_up": True,
    "rocks_spawn": False,
    "wall_kick": True,
}


class Player:
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

    def kill(self, board):
        board.players.remove(self)


class Rock:
    def __init__(self, position):
        self.repr = ROCK
        self.position = position

    def kill(self, board):
        board.rocks.remove(self)


class Board:
    def __init__(self, players, lodtfp, secret_list, width=10, hight=10):
        # List of players
        self.players = players
        # List of rocks
        self.rocks = []

        # Dimensions
        self.width = width
        self.hight = hight

        # Grid setup
        self.grid = [[GROUND for _ in range(width)] for _ in range(hight)]

        # Set fields
        for i, j in enumerate(FIELD_TYPES):
            for k in lodtfp[i]:
                self.set_element(k, j)

        # Secret win
        self.secret_win = secret_list[0]

        # Set rock_spawners
        self.rocks = []
        self.rock_spawners = secret_list[1]

        # Independent copy of initial state
        self.initial_grid = copy.deepcopy(self.grid)

        # Assigning representations to players
        for idx, i in enumerate(self.players):
            i.repr = PLAYER_REPRESENTATIONS[idx]

        # Drawing them onto board in initial state
        for i in players:
            self.set_element(i.position, i.repr)

        self.switch = False  # True for switch is pressed

    def spawn_rock(self, current_player, idx):
        print(f"{current_player}, kicks loose a rock!")
        rock_pos = self.rock_spawners[idx][1]
        self.rock_spawners.pop(idx)
        self.rocks.append(Rock(rock_pos))
        self.set_element(rock_pos, ROCK)

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
        """Read grid at position"""
        row, col = self.wrap(position)
        return self.grid[row][col]

    def find_element(self, repr, grid=None):
        """Find positions of elements on grid"""
        if not grid:
            grid = self.grid
        found_positions = []
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                if val == repr:
                    found_positions.append((i, j))
        return found_positions

    def reset(self, position):
        """Reset a specific square back to initial value"""
        row, col = position
        self.set_element(position, self.initial_grid[row][col])

    def update_gates(self):

        player_pos_list = [i.position for i in self.players]
        gate_list = self.find_element(GATE, self.initial_grid)

        # Gates without players
        free_gates = []
        for i in gate_list:
            if i not in player_pos_list:
                free_gates.append(i)

        for i in gate_list:

            # Find player on gate if any
            player_on_gate = None
            if i in player_pos_list:
                player_on_gate = self.players[player_pos_list.index(i)]

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

        # Check for players on gates
        player_pos_list = [i.position for i in self.players]
        gate_list = self.find_element(GATE, self.initial_grid)
        free_gates = []
        for i in gate_list:
            if i not in player_pos_list:
                free_gates.append(i)

        # Set gates
        for i in gate_list:

            player_on_gate = None
            # Find player on gate if any
            if i in player_pos_list:
                player_on_gate = self.players[player_pos_list.index(i)]

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
    list_of_player_pos = [i.position for i in board.players]
    list_of_tps = board.find_element(TELEPORT)
    list_of_rock_spawners = [i[0] for i in board.rock_spawners]

    # Check rock spawn
    if new_pos in list_of_rock_spawners:
        idx = list_of_rock_spawners.index(new_pos)
        board.spawn_rock(current_player, idx)

    # player collision case
    if new_pos in list_of_player_pos and new_pos != current_player.position:

        # Find 2nd party
        collision_player_idx = list_of_player_pos.index(new_pos)
        collision_player = board.players[collision_player_idx]

        # Squash case
        if current_player.topside and not collision_player.topside:
            # Delete Player
            current_player.kill(board)

            # Death message
            print(
                f"\nOh no! {current_player} jumped on {collision_player}'s head and {collision_player} died!",
                LINE,
            )

            # Show one more time
            board.update(current_player, old_pos)
            return "died"

        # Current player below collision player
        elif not current_player.topside and collision_player.topside:
            # Ignore
            pass

        # Normal collision bottom or top
        else:
            move_P2 = tuple(
                -(a - b)
                for a, b in zip(current_player.position, collision_player.position)
            )
            try:
                make_move(board, collision_player, move_P2, recursion_depth)
            except RecursionError:
                print("Infinite player collision chain. Hell yea!")
                return "collision_chain"

    # wall (gate) collision case
    elif new_pos in board.find_element(WALL) or new_pos in board.find_element(GATE):

        # Topside case
        if current_player.topside:
            # Move as regular
            current_player.position = new_pos
            board.update(current_player, old_pos, new_pos)

        # Bottom
        else:
            # With wall kick
            if (
                GAME_FLAGS["wall_kick"]
                and not current_player.flying
                and not current_player.landing
            ):
                move_again = tuple(
                    (a - b) for a, b in zip(current_player.position, new_pos)
                )
                current_player.flying = True
                make_move(board, current_player, move_again)
                time.sleep(DELAY)
                # Landing
                current_player.flying = False
                current_player.landing = True
                make_move(board, current_player, move_again)
                current_player.landing = False
            elif current_player.landing:
                print("LANDED IN A WALL")
                move_again = (0, 0)
                make_move(board, current_player, move_again)
            # Or pass

    # pit case
    elif new_pos in board.find_element(PIT, board.initial_grid):
        if not current_player.flying:
            # Delete Player
            current_player.kill(board)

            # Death message
            print(f"\nOh no! {current_player} died by falling in a pit!", LINE)

            # Show one more time
            board.update(current_player, old_pos)
            return "died"
        else:
            # Move as regular
            current_player.position = new_pos
            board.update(current_player, old_pos, new_pos)

    # Ice case
    elif new_pos in board.find_element(ICE) and new_pos != current_player.position:

        # not topside not flying but landing
        if not current_player.flying and not current_player.topside:
            move_again = tuple(
                -(a - b) for a, b in zip(current_player.position, new_pos)
            )

            # Set new player position
            current_player.position = new_pos

            # Update board
            board.update(current_player, old_pos, new_pos)
            time.sleep(DELAY)

            # Make the new move because of ice
            try:
                make_move(board, current_player, move_again, recursion_depth)
            except RecursionError:
                print("Infinite ice slide. Hell yea!")
                return "ice slide"

        # Topside
        else:
            # Fall onto it as if regular ground
            current_player.topside = False
            current_player.position = new_pos
            board.update(current_player, old_pos, new_pos)

    # Teleport case
    elif new_pos in list_of_tps:
        current_player.topside = False
        try:
            list_of_tps.pop(list_of_tps.index(new_pos))
            new_pos = list_of_tps[0]

        except:
            print("Teleporter doesn't know what to do...\nTeleporter sad :(")

        #####
        current_player.position = new_pos
        board.update(current_player, old_pos, new_pos)

    # Switch case
    elif new_pos in board.find_element(SWITCH):
        current_player.topside = False
        current_player.position = new_pos
        board.switch = True
        print("GATE opened!", LINE)
        board.update(current_player, old_pos, new_pos)

    # Neutral case
    else:
        current_player.topside = False

        # Move player
        current_player.position = new_pos

        # Update
        board.update(current_player, old_pos, new_pos)

    recursion_depth -= 1
    # End of turn effects
    if not recursion_depth:

        # Check whether anyone still on switch
        if board.switch:
            flag = False
            for i in board.players:
                if i.position in board.find_element(SWITCH, board.initial_grid):
                    flag = True
            if not flag:
                board.switch = False
                print("GATE closed!", LINE)
                board.update()

    # Win case
    if sorted([i.position for i in board.players]) == sorted(
        board.find_element(WIN, board.initial_grid)
    ):
        board.display()
        print("DONE!!!", LINE)
        return "W"

    # Secret Win case
    if sorted([i.position for i in board.players]) == sorted(board.secret_win):
        print(
            "The ground tiles Aelira and Baelric stand on click into place and a mechanism starts up."
        )
        return "SW"


def main_menu(unlocked_levels, menu_skip, current_level):
    lv_list = [level0, level1, level2, level3, level4, level5]

    skip = True
    if skip:
        lodtfp, secret_list, width, hight, start_pos = lv_list[5]()
    else:
        if menu_skip:
            lv = current_level
            lodtfp, secret_list, width, hight, start_pos = lv_list[lv]()
        else:
            while True:
                try:
                    print("Pick a level:")
                    for i in range(unlocked_levels):
                        print(f"level{i+1}")
                    lv = input()
                    if lv == "":
                        lv = 0
                        lodtfp, secret_list, width, hight, start_pos = lv_list[lv]()
                        break
                    elif int(lv) - 1 in range(unlocked_levels):
                        lv = int(lv)
                        lodtfp, width, hight, start_pos = lv_list[lv]()
                        break
                except:
                    pass

    Ps = []
    for i in range(len(PLAYER_NAMES)):
        Ps.append(Player(start_pos[i], PLAYER_NAMES[i]))
    B = Board(Ps, lodtfp, secret_list, width, hight)
    B.display()

    # Play
    while True:
        current_player_idx, move = prompt_move()

        # Quit to main
        if move == "Q":
            menu_skip = False
            return False, menu_skip

        current_player = B.players[current_player_idx]
        exit_status = make_move(B, current_player, move)

        # Win case
        if exit_status == "W" and lv == unlocked_levels:
            unlock = True
            menu_skip = True
            go_back = False
            return unlock, menu_skip, go_back
        # Secret win case
        elif exit_status == "SW":
            print(
                "It's as if time runs backwards as the room reverts to the previous one."
            )
            unlock = False
            menu_skip = True
            go_back = True
            return unlock, menu_skip, go_back
            pass
        # Other cases
        elif exit_status != None:
            input("press enter to restart")
            unlock = False
            menu_skip = True
            go_back = False
            return unlock, menu_skip, go_back


def main():
    # print(
    #     LINE,
    #     "\nAelira and Baelric on the run from the Obelisk, step through the stone archway covered by darkness and find themselves in an empty square stone room. The archway slams shut behind them!\nTheir companions are still fighting the Obelisk so the Heroes better hurry to figure out how to disable it!",
    #     LINE,
    # )
    # input("press enter to continue")

    current_level = 1
    unlocked_levels = 1
    menu_skip = True
    while True:
        unlock_next, menu_skip, go_back = main_menu(
            unlocked_levels, menu_skip, current_level
        )
        if unlock_next:
            unlocked_levels += 1
            current_level += 1
        if go_back:
            current_level -= 1


if __name__ == "__main__":
    main()

### TODO ice slide into death doesnt prompt game end???

### TODO what is up with Board.update containing the gate logic? well the point of it is to decide what to show and what not...

### TODO wouldn't it be better to split make move to a seperate document and into functions depending on the collision types?

### TODO werid tp level where blocking one of three allows the remaining one to function

### TODO make levels run different with gates being able to be ridden onto walls

### able to kick hidden rock loose when stepping onto wall segment falls to place x and is pushable like player

### use to press button and let both into a section
### block tp to allow function


### Kick rebound enables pulling another onto ice maybe
