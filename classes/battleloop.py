import pygame
from classes.UI import Hpbar, Button


# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy, window: pygame.Surface):
        self.player = player
        self.enemy = enemy
        self.window: pygame.Surface = window



        battle_center = self.window.get_width() // 2
        battle_y = self.window.get_height() // 2
        self.battle_offset = 100  # adjust for more spacing



        self.player_position: pygame.Vector2 = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy_position: pygame.Vector2 = pygame.Vector2(enemy.x, enemy.y)

        self.turn: str = "player" # to be changed based on speed stat.

        self.end_battle: bool = False
        self.return_to_overworld: bool = False

        self.player_hp_bar = Hpbar((self.window.get_size()), "left", self.player.hp, self.player.max_hp)
        self.player_hp_bar.set_hp(self.player.hp) # Update player's hp
        self.enemy_hp_bar = Hpbar((self.window.get_size()), "right", self.enemy.hp, self.enemy.hp)

        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.display_menu_options = False


        self.state = None


    def update(self):

        self.animation()
        self.draw_ui(self.window)

        if not self.player.close_distance and not self.enemy.close_distance:
            self.player_hp_bar.update()
            self.enemy_hp_bar.update()



        # Stop the rest from updating
        if self.state == "animation" or self.end_battle:
            return
        if self.end_battle:
            self.return_to_overworld = True

        if self.turn == "player":
            self.display_menu_options = True

        elif self.turn == "enemy":
            self.display_menu_options = False
            self.enemy_turn()


    def draw_ui(self, window):
        self.player_hp_bar.draw(window)
        self.enemy_hp_bar.draw(window)

        if self.buttons_group and self.display_menu_options:
            for button in self.buttons_group:
                button.draw(window)
                button.update()
                if button.delete:
                    for buttons in self.buttons_group:
                        self.display_menu_options = False
                        buttons.kill()

    def handle_input(self):
        if not self.buttons_group:
            Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5)), self.player_attack, "Attack")
            Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5) + 32), self.player_run, "Run")

    def player_run(self):
        self.end_battle = True

    def player_attack(self):
        self.player.close_distance = True
        self.state = "animation"
        # attack_type = ... gets inputted in button as action

        self.enemy.hp -= self.player.dmg
        if self.enemy.hp <= 0:
            self.end_battle = True

        self.enemy_hp_bar.set_hp(self.enemy.hp)



    def animation(self):
        if self.player.close_distance:
            self.player.move_to(self.enemy)
        elif self.player.attacking:
            self.player.attack()
        elif self.player.move_back:
            self.player.go_back(self.player_position)
            self.turn = "enemy"

        elif self.enemy.close_distance:
            self.enemy.move_to(self.player)

        elif self.enemy.move_back:
            self.enemy.go_back(self.enemy_position)
            self.turn = "player"

        elif self.enemy.attacking:
            self.enemy.attack()

        elif self.enemy.death:
            self.enemy.death_animation()

        else:
            self.state = "ok"


    def enemy_turn(self):
        self.state = "animation"
        self.enemy.close_distance = True

        self.player.hp -= self.enemy.dmg

        if self.player.hp <= 0:
            self.end_battle = True

        self.player_hp_bar.set_hp(self.player.hp)
        self.delay = True


# state	Meaning
# "idle"	Waiting for player input
# "animation"	Currently animating a move (moving, attacking, returning)
# "battle_start"	Intro sequence or setup
# "result"	Show victory/loss screen
