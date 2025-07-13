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
        self.buttons = []
        self.display_menu_options = False
        self.number = 0



        self.state: str = "player" # to be changed based on speed stat.

        self.state = "player_turn"

        self.timer = 0
        self.timer_started = False
        self.death_delay = 1000

        self.delay = pygame.time.get_ticks() + 0



    def update(self):

        self.handle_input()
        self.animation()
        self.draw_ui(self.window)

        if self.delay and pygame.time.get_ticks() >= self.delay:
            if self.state == "player_turn":
                    self.display_menu_options = True

            elif self.state == "enemy_turn":
                    self.display_menu_options = False
                    self.enemy_turn()
                    self.delay = None

            elif self.state == "end_battle":
                    self.return_to_overworld = True
            elif self.state == "end_screen":
                self.display_menu_options = True

    def draw_ui(self, window):
        self.player_hp_bar.draw(window)
        self.enemy_hp_bar.draw(window)

        if self.buttons and self.display_menu_options:
            for button in self.buttons:
                button.update()
                button.draw(window)

                if button.delete:
                    for buttons in self.buttons_group:
                        self.display_menu_options = False
                        buttons.kill()

    def handle_input(self):
        if not self.buttons_group:
            if self.state == "player_turn":
                self.buttons = [Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5)), self.player_attack, "Attack"),
                    Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5) + 32), self.player_run, "Run")]


                Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5)), self.player_attack, "Attack")
                Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5) + 32), self.player_run, "Run")

            if self.state == "end_screen":
                self.buttons = [Button(self.buttons_group, (self.window.get_width() // 2, int(self.window.get_height() // 1.5)), self.player_run, "Done")]


    def hotkeys(self, event):
            if event.type == pygame.KEYDOWN:

                # Navigate up
                if event.key == pygame.K_UP and self.number == 0:
                    self.buttons[self.number].hovering = True


                elif event.key == pygame.K_DOWN and self.number == len(self.buttons) - 1:
                    self.buttons[self.number].hovering = True


                elif event.key == pygame.K_UP and self.number > 0:
                    self.buttons[self.number].hovering = False
                    self.number -= 1
                    self.buttons[self.number].hovering = True

                # Navigate down
                elif event.key == pygame.K_DOWN and self.number < len(self.buttons) - 1:
                    self.buttons[self.number].hovering = False
                    self.number += 1
                    self.buttons[self.number].hovering = True

                # Confirm selection
                elif event.key == pygame.K_RETURN:
                    self.buttons[self.number].clicked = True  # <-- Call your button action here

    def player_run(self):
        self.state = "end_battle"

    def player_attack(self):
        self.player.approach_trigger = True
        self.state = "player_animation"
        # attack_type = ... gets inputted in button as action



    def animation(self):
        if self.state == "player_animation":
            if self.player.approach_trigger:
                self.player.approach_animation(self.enemy)
                self.delay = pygame.time.get_ticks() + 1000


            elif self.player.wait_trigger:
                self.player.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.player.attack_trigger = True
                    self.player.wait_trigger = False

            elif self.player.attack_trigger:
                self.enemy_hp_bar.update()
                self.player.attack_animation(self.enemy, "sword_slash")
                self.enemy_hp_bar.set_hp(self.enemy.hp)


            elif self.player.return_trigger:
                self.player.return_animation(self.player_position)

            elif self.enemy.hp <= 0:
                self.state = "end_screen"

            elif not self.player.attack_trigger and not self.player.return_trigger:
                # End of player's animation
                self.delay = pygame.time.get_ticks() + 500
                self.state = "enemy_turn"

        elif self.state == "enemy_animation":
            if self.enemy.approach_trigger:
                self.enemy.approach_animation(self.player)
                self.delay = pygame.time.get_ticks() + 1000 # random number for timed blocks


            elif self.enemy.wait_trigger:
                self.enemy.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.enemy.attack_trigger = True
                    self.enemy.wait_trigger = False


            elif self.enemy.attack_trigger:
                self.player_hp_bar.update()
                self.enemy.attack_animation(self.player, "sword_slash")
                self.player_hp_bar.set_hp(self.player.hp)

            elif self.enemy.return_trigger:
                self.enemy.return_animation(self.enemy_position)

            elif self.player.hp <= 0 and not self.enemy.return_trigger:
                self.state = "end_screen"

            elif not self.enemy.attack_trigger and not self.enemy.return_trigger:
                # End of enemy's animation
                self.delay = pygame.time.get_ticks() + 500
                self.state = "player_turn"




    def enemy_attack(self):
        self.enemy.approach_trigger = True
        self.state = "enemy_animation"



    def enemy_turn(self):
        # add random actions in the future
        self.enemy_attack()




# state	Meaning
# "idle"	Waiting for player input
# "animation"	Currently animating a move (moving, attacking, returning)
# "battle_start"	Intro sequence or setup
# "result"	Show victory/loss screen
