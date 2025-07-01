# Base class (Parent)
class Player:
    player_count = 0

    def __init__(self, name, posititon=(0, 0)):
        self.name = name
        self.position = posititon
        self.nr = Player.player_count + 1
        self.repr = str(self.nr)
        Player.player_count += 1

    def __str__(self):
        return f"{self.name}"

    def __del__(self):
        Player.player_count -= 1


class Board:
    def __init__(self, players, width=7, hight=5):
        self.players = players
        self.width = width
        self.hight = hight
        self.grid = [["." for _ in range(width)] for _ in range(hight)]
        for i in players:
            self.set_element(i.position, i.repr)

    def display(self):
        for row in self.grid:
            print(" ".join(row))
        print("\n")

    def set_element(self, position, value):
        row, col = position
        self.grid[row][col] = value


def prompt_move(player):
    "Gets next move."

    # Prompt
    print(f"{player}, pick a move (wasd):")
    # Try to get a valid move and translate to coordinates
    while True:
        move = False
        read_move = input()
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


def make_move(board, player, move):
    """Executes move on board."""

    # Set old player position back to neutral
    board.set_element(player.position, ".")

    # Calculate new position
    new_pos = tuple(a + b for a, b in zip(move, player.position))

    # Wrap new position back into board
    new_pos = (new_pos[0] % board.hight, new_pos[1] % board.width)
    # Move player
    player.position = new_pos

    # Set new Player position on board
    board.set_element(player.position, player.repr)


def main():
    Player1 = Player("Alice")
    B = Board([Player1])
    B.display()

    while True:
        move = prompt_move(Player1)
        make_move(B, Player1, move)
        B.display()


main()
