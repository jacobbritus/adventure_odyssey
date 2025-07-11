import pygame.key

# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        self.turn = "player"
        self.finished = False

    def update(self):
        if self.finished:
            return

        if self.turn == "player":
            self.handle_input()

        elif self.turn == "enemy":
            self.turn = "player"

    def handle_input(self):
        if self.turn == "player":

            key_pressed = pygame.key.get_pressed()

            if key_pressed[pygame.K_a]:
                print("attack")

            if key_pressed[pygame.K_r]:
                self.finished = True