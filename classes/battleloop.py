import random

import pygame
from classes.UI import Hpbar, Button
from other.settings import *


# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy, window: pygame.Surface, offset):
        self.player = player
        self.enemy = enemy
        self.window: pygame.Surface = window

        self.player_position: pygame.Vector2 = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy_position: pygame.Vector2 = pygame.Vector2(enemy.x, enemy.y)

        self.offset = offset


        self.return_to_overworld: bool = False

        self.player_hp_bar = Hpbar((self.window.get_size()), "left", self.player.hp, self.player.max_hp, "PLAYER") #enemy.name in the future
        self.player_hp_bar.set_hp(self.player.hp) # Update player's hp
        self.enemy_hp_bar = Hpbar((self.window.get_size()), "right", self.enemy.hp, self.enemy.hp, "SKELETON") #enemy.name in the future

        self.buttons_group: pygame.sprite.Group = pygame.sprite.Group()
        self.buttons = []
        self.display_menu_options = False
        self.number = 0

        self.enemy_damage_position = pygame.Vector2(self.enemy.x - self.offset.x + 32, self.enemy.y - self.offset.y - 16)
        self.player_damage_position = pygame.Vector2(self.player.x - self.offset.x + 32,
                                                     self.player.y - self.offset.y - 16)





        self.state = "player_turn" # to be changed based on speed stat.
        self.delay = pygame.time.get_ticks() + 0 # set if enemy starts first


        self.timer = 0
        self.timer_started = False
        self.death_delay = 1000
        self.time = pygame.time.get_ticks() + 10000



        # Hotkey stuff
        self.block_duration = 250 # blocking last time
        self.block_cooldown_end = 0 # when blocking ends
        self.block = False # whether blocking is True
        self.block_delay = 2000

    def timer_(self):
        if self.state == "player_turn" and self.time and not pygame.time.get_ticks() >= self.time:

            current_time = ((self.time - pygame.time.get_ticks()) // 1000)



            font = pygame.font.Font(TEXT_TWO, 44)
            time_text = font.render(str(current_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            box = pygame.image.load(TIME_BACKGROUND)
            box_size = box.get_width()

            self.window.blit(box, (WINDOW_WIDTH // 2 - box_size // 2, self.player_hp_bar.box_position[1] ))
            self.window.blit(time_text, (WINDOW_WIDTH // 2 - time_size // 2 + 1, self.player_hp_bar.box_position[1] - 2))

    def update(self):
        self.timer_()
        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar.set_hp(self.enemy.hp)

        self.handle_input()
        self.animation()
        self.draw_ui(self.window)

        if not self.delay or pygame.time.get_ticks() >= self.delay:
            if self.state == "player_turn":
                    self.display_menu_options = True
                    if self.time and pygame.time.get_ticks() >= self.time:
                        self.state = "enemy_turn"

                        self.time = pygame.time.get_ticks() + 20000


            elif self.state == "enemy_turn":
                    self.display_menu_options = False
                    self.enemy_turn()
                    self.delay = None

            elif self.state == "end_battle":
                    self.return_to_overworld = True
            elif self.state == "end_screen":
                self.display_menu_options = True

    def action_lock(self) -> bool:
        return (
                self.player.approach_trigger or
                self.enemy.approach_trigger or
                self.player.wait_trigger or
                self.enemy.wait_trigger or
                self.player.attack_trigger or
                self.enemy.attack_trigger
        )

    def display_dmg(self):
        font = pygame.font.Font(TEXT_TWO, 22)

        if self.player.hit_landed:

            damage_text = font.render(str(self.player.dmg), True, (255, 255, 255))

            self.window.blit(damage_text, self.enemy_damage_position)
            self.enemy_damage_position.y -= 1


        elif self.enemy.hit_landed:
            dmg = self.enemy.dmg
            if self.player.blocking:
                dmg = dmg // 2

            damage_text = font.render(str(dmg), True, (255, 255, 255))
            self.window.blit(damage_text, self.player_damage_position)
            self.player_damage_position.y -= 1

        else:
            self.enemy_damage_position = pygame.Vector2(self.enemy.x - self.offset.x - 16,
                                                        self.enemy.y - self.offset.y - 16)
            self.player_damage_position = pygame.Vector2(self.player.x - self.offset.x + 64,
                                                         self.player.y - self.offset.y - 16)

    def draw_ui(self, window):


        if self.player.hit_landed or self.enemy.hit_landed or self.player.return_trigger or self.enemy.return_trigger:
            self.enemy_hp_bar.update()
            self.player_hp_bar.update()


        if not self.action_lock() or self.player.hit_landed or self.enemy.hit_landed:
            self.player_hp_bar.draw(window)
            self.enemy_hp_bar.draw(window)
            self.display_dmg()



        if self.buttons and self.display_menu_options:
            for button in self.buttons:
                button.update()
                button.draw(window)

                if button.delete:
                    for buttons in self.buttons_group:
                        self.display_menu_options = False
                        buttons.kill()

    def handle_input(self):
        if self.block and pygame.time.get_ticks() >= self.block_cooldown_end:
            self.block = False
            self.player.blocking = False


        if not self.buttons_group:
            if self.state == "player_turn":
                self.buttons = [Button(self.buttons_group,  self.player_attack, "Attack", "one"),
                    Button(self.buttons_group, self.player_run, "Run", "two")]




            if self.state == "end_screen":
                self.buttons = [Button(self.buttons_group, self.player_run, "Done", "middle")]


    def hotkeys(self, event):
            current_time = pygame.time.get_ticks()

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
                    self.buttons[self.number].clicked = True

                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    if not self.block and current_time >= self.block_cooldown_end + self.block_delay:
                        self.block = True
                        self.player.blocking = True
                        self.block_cooldown_end = current_time + self.block_duration  # Next time we can block again


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
                self.delay = pygame.time.get_ticks() + 1000  # or whatever delay you prefer


            elif self.player.wait_trigger:
                self.player.wait()
                if self.delay is None:
                    self.delay = pygame.time.get_ticks() + 1000  # or whatever delay you prefer
                if pygame.time.get_ticks() >= self.delay:
                    self.player.attack_trigger = True
                    self.player.wait_trigger = False
                    self.delay = None

            elif self.player.attack_trigger:
                self.player.attack_animation(self.enemy, "sword_slash")

                self.delay = pygame.time.get_ticks() + 1000  # or whatever delay you prefer


            elif self.player.return_trigger and pygame.time.get_ticks() >= self.delay:
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


            elif self.enemy.wait_trigger:
                self.enemy.wait()
                if self.delay is None:
                    self.delay = pygame.time.get_ticks() + random.randint(500, 2000)

                if pygame.time.get_ticks() >= self.delay:
                    self.enemy.wait_trigger = False
                    self.enemy.attack_trigger = True
                    self.delay = None  # Reset! = True


            elif self.enemy.attack_trigger:
                self.player_hp_bar.update()
                self.enemy.attack_animation(self.player, "sword_slash")

                self.delay = pygame.time.get_ticks() + 1000  # or whatever delay you prefer


            elif self.enemy.return_trigger and pygame.time.get_ticks() >= self.delay:
                self.enemy.return_animation(self.enemy_position)
                self.player_hp_bar.update()
                self.time = pygame.time.get_ticks() + 20000




            elif self.player.hp <= 0:
                self.state = "end_screen"

            elif not self.enemy.attack_trigger and not self.enemy.return_trigger :
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
