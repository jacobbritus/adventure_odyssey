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

        self.player_position: pygame.Vector2 = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy_position: pygame.Vector2 = pygame.Vector2(enemy.x, enemy.y)

        self.return_to_overworld: bool = False

        self.player_hp_bar = Hpbar((self.window.get_size()), "left", self.player.hp, self.player.max_hp)
        self.player_hp_bar.set_hp(self.player.hp) # Update player's hp
        self.enemy_hp_bar = Hpbar((self.window.get_size()), "right", self.enemy.hp, self.enemy.hp)

        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.display_menu_options = False


        self.state: str = "player" # to be changed based on speed stat.

        self.state = "player_turn"

        self.timer = 0
        self.timer_started = False
        self.death_delay = 2000


    def update(self):
        self.animation()
        self.draw_ui(self.window)

        print(self.timer)

        if self.state == "player_turn":
            self.display_menu_options = True

        elif self.state == "enemy_turn":
            self.display_menu_options = False
            self.enemy_turn()

        elif self.state == "end_battle":
            if not self.timer_started:
                self.timer = pygame.time.get_ticks()
                self.timer_started = True

            if pygame.time.get_ticks() - self.timer > self.death_delay:
                self.return_to_overworld = True

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
        self.state = "end_battle"

    def player_attack(self):
        self.player.close_distance = True
        self.state = "player_animation"
        # attack_type = ... gets inputted in button as action

        self.enemy.hp -= self.player.dmg

        self.enemy_hp_bar.set_hp(self.enemy.hp)

    def animation(self):
        if self.state == "player_animation":
            if self.player.close_distance:
                self.player.move_to(self.enemy)

            elif self.player.attacking:
                self.enemy_hp_bar.update()
                self.player.attack(self.enemy)

            elif self.player.move_back:
                self.player.go_back(self.player_position)

            elif self.enemy.hp <= 0:
                self.state = "end_battle"

            elif not self.player.attacking and not self.player.move_back:
                # End of player's animation
                self.state = "enemy_turn"

        elif self.state == "enemy_animation":
            if self.enemy.close_distance:
                self.enemy.move_to(self.player)

            elif self.enemy.attacking:
                self.enemy.attack(self.player)
                self.player_hp_bar.update()

            elif self.enemy.move_back:
                self.enemy.go_back(self.enemy_position)

            elif self.player.hp <= 0 and not self.enemy.move_back:
                self.state = "end_battle"

            elif not self.enemy.attacking and not self.enemy.move_back:
                # End of enemy's animation
                self.state = "player_turn"



    def enemy_attack(self):
        self.enemy.close_distance = True
        self.state = "enemy_animation"

        self.player.hp -= self.enemy.dmg

        self.player_hp_bar.set_hp(self.player.hp)

    def enemy_turn(self):
        # add random actions in the future
        self.enemy_attack()




# state	Meaning
# "idle"	Waiting for player input
# "animation"	Currently animating a move (moving, attacking, returning)
# "battle_start"	Intro sequence or setup
# "result"	Show victory/loss screen
