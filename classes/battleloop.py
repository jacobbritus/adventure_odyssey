import random

import pygame
from classes.UI import Hpbar, Button, CombatMenu
from classes.floatingdamage import FloatingDamage
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

        self.combat_menu = CombatMenu(self.player.attacks, self.player_attack)

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

        self.player_attack = None


        self.state = "player_turn" # to be changed based on speed stat.
        self.delay = pygame.time.get_ticks() + 0 # set if enemy starts first


        self.timer = 0
        self.timer_started = False
        self.death_delay = 1000
        self.clock_time = pygame.time.get_ticks() + 10000

        self.damage_group = pygame.sprite.Group()
        self.damage_counter = 0
        self.critical_floated = False
        self.perfect_block_floated = False
        self.perfect_block_counter = 0

        # Hotkey stuff
        self.block_duration = 250 # blocking last time
        self.block_cooldown_end = 0 # when blocking ends
        self.block = False # whether blocking is True
        self.block_delay = 250



    def timer_(self):
        if self.state == "player_turn" and self.clock_time and not pygame.time.get_ticks() >= self.clock_time:

            current_time = ((self.clock_time - pygame.time.get_ticks()) // 1000)



            font = pygame.font.Font(TEXT_TWO, 33)
            time_text = font.render(str(current_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            box = pygame.image.load(TIME_BACKGROUND)
            box_size = box.get_width()

            # self.window.blit(box, (WINDOW_WIDTH // 2 - box_size // 2, self.player_hp_bar.box_position[1] ))
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
                    self.combat_menu.option_selected = False
                    if not self.combat_menu.buttons_group: self.combat_menu.main_menu()
                    self.combat_menu.draw(self.window)
                    self.display_menu_options = True
                    if self.clock_time and pygame.time.get_ticks() >= self.clock_time:
                        self.state = "enemy_turn"

                        self.clock_time = pygame.time.get_ticks() + 20000


            elif self.state == "enemy_turn":
                    self.display_menu_options = False
                    self.enemy_turn()
                    self.delay = None

            elif self.state == "end_battle":
                    self.return_to_overworld = True
                    self.untoggle()

            elif self.state == "end_screen":
                self.display_menu_options = True

    def action_lock(self) -> bool:
        return (
                self.player.approach_trigger or
                self.enemy.approach_trigger or
                self.player.wait_trigger or
                self.enemy.wait_trigger

        )

    def display_dmg(self):
        offset = 32
        player_dmg_position = pygame.Vector2(self.player.screen_position.x + offset, self.player.screen_position.y)
        enemy_dmg_position = pygame.Vector2(self.enemy.screen_position.x + offset, self.enemy.screen_position.y)


        if self.state == "player_animation":
            self.damage_group.update(enemy_dmg_position)
        elif self.state == "enemy_animation":
            self.damage_group.update(player_dmg_position)

        self.damage_group.draw(self.window)

        if self.player.hit_landed and not self.enemy.death:
            for index, dmg in enumerate(self.enemy.dmg_taken):
                FloatingDamage(self.damage_group, dmg, enemy_dmg_position, self.damage_counter)
                self.damage_counter += 1
            self.enemy.dmg_taken.clear()

        elif self.enemy.hit_landed and not self.player.death:
            for index, dmg in enumerate(self.player.dmg_taken):
                FloatingDamage(self.damage_group, dmg, enemy_dmg_position, self.damage_counter)
                self.damage_counter += 1
            self.player.dmg_taken.clear()


        if self.player.critical_hit and self.player.critical_hit_messages:
            FloatingDamage(self.damage_group, "CRITICAL HIT", player_dmg_position, 1)
            self.player.critical_hit_messages.clear()

        if self.enemy.critical_hit and self.enemy.critical_hit_messages:
            FloatingDamage(self.damage_group, "CRITICAL HIT", player_dmg_position, -3)
            self.enemy.critical_hit_messages.clear()

        # if self.player.perfect_block and not self.perfect_block_floated:
        #     FloatingDamage(self.damage_group, "PERFECT BLOCK", player_dmg_position, 1)
        #     self.perfect_block_floated = True

        if self.player.perfect_block and self.player.perfect_block_messages:
            FloatingDamage(self.damage_group, "PERFECT BLOCK", player_dmg_position, -4)
            self.player.perfect_block_messages.clear()





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



        # if not self.buttons_group:
        #     if self.state == "player_turn":
        #         self.buttons = [Button(self.buttons_group, "no parameter", self.player_attack, "Attack", "small", ((WINDOW_WIDTH // 2) - pygame.image.load(BUTTON_TWO_NORMAL).get_width() , WINDOW_HEIGHT // 1.25)),
        #             Button(self.buttons_group,"no parameter", self.player_run, "Run", "small", ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 6 , WINDOW_HEIGHT // 1.25))]
        #
        #
        #
        if not self.buttons_group:
            if self.state == "end_screen":
                self.buttons = [Button(self.buttons_group, "no parameter", self.player_run, "DONE", "medium", ((WINDOW_WIDTH // 2) + pygame.image.load(BUTTON_TWO_NORMAL).get_width() // 5 , WINDOW_HEIGHT // 1.25))]

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

    def player_attack(self, attack):
        attack_ = attack.replace(" ", "_")

        self.player_attack = attack_.lower()
        self.perfect_block_counter = 0
        self.damage_counter = 0

        self.player.approach_trigger = True # depending on animation else we can do wait and then attack trigger
        self.state = "player_animation"

    def animation(self):
        if self.state == "player_animation":
            if self.player.approach_trigger:
                self.player.approach_animation(self.enemy)
                self.delay = pygame.time.get_ticks() + 1000 # wait time before attacking

            elif self.player.wait_trigger:
                self.player.wait()
                if pygame.time.get_ticks() >= self.delay:
                    self.player.attack_trigger = True
                    self.player.wait_trigger = False
                    self.delay = None

            elif self.player.attack_trigger:
                self.player.attack_animation(self.enemy, self.player_attack)
                self.delay = pygame.time.get_ticks() + 500  # delay before returning

            elif self.player.return_trigger:
                self.enemy.action = "idle"
                if self.enemy.hp <= 0:
                    self.enemy.death_animation()

                if pygame.time.get_ticks() >= self.delay:
                    self.player.return_animation(self.player_position)

            elif self.enemy.hp <= 0:
                self.state = "end_screen"

            elif not self.player.attack_trigger and not self.player.return_trigger:
                # End of player's animation
                self.delay = pygame.time.get_ticks() + 500
                self.state = "enemy_turn"
                self.critical_floated = False


        elif self.state == "enemy_animation":
            if self.enemy.approach_trigger:
                self.enemy.approach_animation(self.player)
                self.delay = pygame.time.get_ticks() + random.randint(500, 3000) # random wait time before attacking

            elif self.enemy.wait_trigger:
                self.enemy.wait()
                if pygame.time.get_ticks() >= self.delay:
                    self.enemy.wait_trigger = False
                    self.enemy.attack_trigger = True
                    self.delay = None  # Reset! = True

            elif self.enemy.attack_trigger:
                self.player_hp_bar.update()
                self.enemy.attack_animation(self.player, "sword_slash")

                self.delay = pygame.time.get_ticks() + 500  # delay before returning


            elif self.enemy.return_trigger:
                self.player.action = "idle"
                if self.player.hp <= 0:
                    self.state = "end_screen"

                if pygame.time.get_ticks() >= self.delay:
                    self.enemy.return_animation(self.enemy_position)
                    self.clock_time = pygame.time.get_ticks() + 20000

            elif self.player.hp <= 0:
                self.state = "end_screen"

            elif not self.enemy.attack_trigger and not self.enemy.return_trigger :
                # End of enemy's animation
                self.delay = pygame.time.get_ticks() + 500 # delay before player turn
                self.state = "player_turn"
                self.critical_floated = False



    def enemy_attack(self):
        self.damage_counter = 0
        self.perfect_block_counter = 0
        self.enemy.approach_trigger = True
        self.state = "enemy_animation"

    def untoggle(self):
        for participant in [self.player, self.enemy]:
            participant.approach_trigger = False
            participant.return_trigger = False
            participant.attack_trigger = False
            if not participant.hp <= 0: participant.death = False
            participant.hit_landed = False
            participant.blocking = False
            participant.wait_trigger = False
            participant.death_trigger = False
            participant.current_action = None
            participant.critical_hit = False
            participant.critical_hit_is_done = False

    def enemy_turn(self):
        # add random actions in the future
        self.enemy_attack()




# state	Meaning
# "idle"	Waiting for player input
# "animation"	Currently animating a move (moving, attacking, returning)
# "battle_start"	Intro sequence or setup
# "result"	Show victory/loss screen
