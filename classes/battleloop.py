import pygame
from classes.hpbar import Hpbar

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

        self.player_hp_bar = Hpbar((125, 187), self.player.hp, self.player.max_hp)
        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar = Hpbar((450, 187), self.enemy.hp, self.enemy.hp)

    def update(self):
        self.player_hp_bar.update()
        self.enemy_hp_bar.update()


        if self.finished:
            return

        if self.turn == "player":
            pass

        elif self.turn == "enemy":
            self.enemy_turn()
            self.turn = "player"

    def ui(self, window):
        # font = pygame.font.Font("sprites/fonts/FantasyRPGtext.ttf", 32)
        # player_hp = font.render(f"hp {self.player.hp}",True, (255, 0, 0))
        # enemy_hp = font.render(f"hp {self.enemy.hp}",True, (255, 0, 0))
        # window.blit(player_hp, (100, 195))
        # window.blit(enemy_hp, (400, 195))

        self.player_hp_bar.draw(window)
        self.enemy_hp_bar.draw(window)




        # print(self.player.hp)




    def handle_input(self, event):
        if self.turn == "player":

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player_attack()
                    self.turn = "enemy"

                if event.key == pygame.K_r:
                    self.finished = True



    def player_attack(self):
        self.enemy.hp -= self.player.dmg


        if self.enemy.hp <= 0:
            self.finished = True

        self.enemy_hp_bar.set_hp(self.enemy.hp)


    def enemy_turn(self):
        self.player.hp -= self.enemy.dmg



        if self.player.hp <= 0:
            self.finished = True

        self.player_hp_bar.set_hp(self.player.hp)


