class GameObject:
    def __init__(self, position):
        self.position = position

    def collide_with(self,other, board):
        pass

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

    def kill(self, board):
        board.players.remove(self)

    def collide_with(self, other, board):
        return other.collide_with_player(self, board)
    

class Rock(GameObject):
    
    def collide_with(self, other, board):
        return other.collide_with_rock(self, board)
    
    def collide_with_player(self, player, board):
        # Try to push the rock in the direction the player is moving
        push_direction = (self.position[0] - player.position[0], self.position[1] - player.position[1])
        new_rock_pos = (self.position[0] + push_direction[0], self.position[1] + push_direction[1])
        board.
        






















