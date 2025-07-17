import random

from classes.UI import Hpbar, CombatMenu
from classes.states import AnimationState, BattleState
from classes.floatingdamage import FloatingDamage
from other.settings import *

# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy, window: pygame.Surface):
        # __general___
        self.player = player
        self.enemy = enemy
        self.window: pygame.Surface = window

        # ___idle positions___
        self.player_position: pygame.Vector2 = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy_position: pygame.Vector2 = pygame.Vector2(enemy.x, enemy.y)

        # ___end battle toggle___
        self.return_to_overworld: bool = False

        # ___UI setup___
        self.combat_menu = CombatMenu(self.player.attacks, [self.player_attack, self.player_run, self.player_run])
        self.combat_menu.state = "main_menu"
        self.player_hp_bar = Hpbar((self.window.get_size()), "left", self.player.hp, self.player.max_hp, "PLAYER") #enemy.name in the future
        self.player_hp_bar.set_hp(self.player.hp) # Update player's hp
        self.enemy_hp_bar = Hpbar((self.window.get_size()), "right", self.enemy.hp, self.enemy.hp, "SKELETON") #enemy.name in the future

        # ___used as an argument to perform the chosen attack option___
        self.player_attack_option = None
        self.enemy_attack_option = None

        # ___states___ (to change based on speed stat)
        self.state = BattleState.PLAYER_TURN

        # ___delays and the clock___
        self.delay = pygame.time.get_ticks() + 0 # set if enemy starts first
        self.clock_time = pygame.time.get_ticks() + 10000

        # ___screen messages___
        self.screen_messages_group = pygame.sprite.Group()
        self.damage_counter = 0
        self.critical_floated = False
        self.perfect_block_floated = False
        self.perfect_block_counter = 0

        # ___block and crit hotkey___
        self.block_duration = 250 # blocking last time
        self.block_cooldown_end = 0 # when blocking ends
        self.block = False # whether blocking is True
        self.block_delay = 250

    def timer_(self):
        if self.state == BattleState.PLAYER_TURN and self.clock_time and not pygame.time.get_ticks() >= self.clock_time:

            current_time = ((self.clock_time - pygame.time.get_ticks()) // 1000)

            font = pygame.font.Font(TEXT_TWO, 33)
            time_text = font.render(str(current_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            # box = pygame.image.load(TIME_BACKGROUND)
            # # box_size = box.get_width()

            # self.window.blit(box, (WINDOW_WIDTH // 2 - box_size // 2, self.player_hp_bar.box_position[1] ))
            self.window.blit(time_text, (WINDOW_WIDTH // 2 - time_size // 2 + 1, self.player_hp_bar.box_position[1] - 2))

    def update(self):
        self.player.projectiles.draw(self.window)
        self.player.projectiles.update(self.enemy.screen_position)

        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar.set_hp(self.enemy.hp)

        self.handle_input()
        self.animation()
        self.draw_ui(self.window)

        if not self.delay or pygame.time.get_ticks() >= self.delay:
            if self.state == BattleState.PLAYER_TURN:
                if self.clock_time and pygame.time.get_ticks() >= self.clock_time:
                    self.state = BattleState.ENEMY_TURN
                    self.clock_time = pygame.time.get_ticks() + 20000

            elif self.state == BattleState.ENEMY_TURN:
                    self.enemy_turn()
                    self.delay = None

            elif self.state == BattleState.END_BATTLE:
                    self.return_to_overworld = True
                    self.untoggle()

            elif self.state == self.state.END_SCREEN:
                self.combat_menu.state = "end_screen"
                self.combat_menu.draw(self.window)


    def action_lock(self) -> bool:
        return (
                self.player.animation_state == AnimationState.APPROACH or
                self.enemy.animation_state == AnimationState.APPROACH or
                self.player.animation_state == AnimationState.WAIT or
                self.enemy.animation_state == AnimationState.WAIT
        )

    def screen_messages(self):
        offset = 32
        player_dmg_position = pygame.Vector2(self.player.screen_position.x + offset, self.player.screen_position.y)
        enemy_dmg_position = pygame.Vector2(self.enemy.screen_position.x + offset, self.enemy.screen_position.y)

        if self.state == BattleState.PLAYER_ANIMATION:
            self.screen_messages_group.update(enemy_dmg_position)
        elif self.state == BattleState.ENEMY_ANIMATION:
            self.screen_messages_group.update(player_dmg_position)

        self.screen_messages_group.draw(self.window)

        if self.player.hit_landed and not self.enemy.death:
            for index, dmg in enumerate(self.enemy.dmg_taken):
                FloatingDamage(self.screen_messages_group, dmg, enemy_dmg_position, self.damage_counter)
                self.damage_counter += 1
            self.enemy.dmg_taken.clear()

        elif self.enemy.hit_landed and not self.player.death:
            for index, dmg in enumerate(self.player.dmg_taken):
                FloatingDamage(self.screen_messages_group, dmg, enemy_dmg_position, self.damage_counter)
                self.damage_counter += 1
            self.player.dmg_taken.clear()

        if self.player.critical_hit and self.player.critical_hit_messages:
            FloatingDamage(self.screen_messages_group, "CRITICAL HIT", player_dmg_position, 1)
            self.player.critical_hit_messages.clear()

        if self.enemy.critical_hit and self.enemy.critical_hit_messages:
            FloatingDamage(self.screen_messages_group, "CRITICAL HIT", player_dmg_position, -3)
            self.enemy.critical_hit_messages.clear()

        if self.player.perfect_block and self.player.perfect_block_messages:
            FloatingDamage(self.screen_messages_group, "PERFECT BLOCK", player_dmg_position, -4)
            self.player.perfect_block_messages.clear()

    def draw_ui(self, window):
        self.timer_()


        if self.state == BattleState.PLAYER_TURN or self.state == BattleState.END_SCREEN:
            self.combat_menu.draw(self.window)

        if (self.player.hit_landed or self.enemy.hit_landed
                or self.player.animation_state == AnimationState.RETURN or self.enemy.animation_state == AnimationState.RETURN):
            self.enemy_hp_bar.update()
            self.player_hp_bar.update()

        if not self.action_lock() or self.player.hit_landed or self.enemy.hit_landed:
            self.player_hp_bar.draw(window)
            self.enemy_hp_bar.draw(window)
            self.screen_messages()


    def handle_input(self):
        if self.block and pygame.time.get_ticks() >= self.block_cooldown_end:
            self.block = False
            self.player.blocking = False

    def hotkeys(self, event):
            current_time = pygame.time.get_ticks()

            # if event.type == pygame.KEYDOWN:

                # # Navigate up
                # if event.key == pygame.K_UP and self.number == 0:
                #     self.buttons[self.number].hovering = True
                #
                # elif event.key == pygame.K_DOWN and self.number == len(self.buttons) - 1:
                #     self.buttons[self.number].hovering = True
                #
                #
                # elif event.key == pygame.K_UP and self.number > 0:
                #     self.buttons[self.number].hovering = False
                #     self.number -= 1
                #     self.buttons[self.number].hovering = True
                #
                # # Navigate down
                # elif event.key == pygame.K_DOWN and self.number < len(self.buttons) - 1:
                #     self.buttons[self.number].hovering = False
                #     self.number += 1
                #     self.buttons[self.number].hovering = True
                #
                # # Confirm selection
                # elif event.key == pygame.K_RETURN:
                #     self.buttons[self.number].clicked = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                if not self.block and current_time >= self.block_cooldown_end + self.block_delay:
                    self.block = True
                    self.player.blocking = True
                    self.block_cooldown_end = current_time + self.block_duration  # Next time we can block again

    def player_run(self):
        self.state = BattleState.END_BATTLE

    def player_attack(self, attack):
        attack_ = attack.replace(" ", "_")

        self.player_attack_option = attack_.lower()
        self.perfect_block_counter = 0
        self.damage_counter = 0

        if self.player_attack_option == "fire_ball":
            self.delay = pygame.time.get_ticks() + 1000
            self.player.spawn_projectile = True

            self.player.animation_state = AnimationState.WAIT

        else:
            if self.player_attack_option == "combustion":
                print("check")
                self.player.spawn_projectile = True
            self.player.animation_state = AnimationState.APPROACH

            # self.player.approach_trigger = True # depending on animation else we can do wait and then attack trigger
        self.state = BattleState.PLAYER_ANIMATION

    def animation(self):
        if self.state == BattleState.PLAYER_ANIMATION:
            if self.player.animation_state == AnimationState.APPROACH:
                self.player.approach_animation(self.enemy)
                self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking

            elif self.player.animation_state == AnimationState.WAIT:
                self.player.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.player.animation_state = AnimationState.ATTACK
                    self.delay = None

            elif self.player.animation_state == AnimationState.ATTACK:
                self.player.attack_animation(self.enemy, self.player_attack_option) # self.player_attack

                if self.enemy.hp <= 0 and not self.enemy.death:
                    self.enemy.death_animation()
                self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking

            elif self.player.animation_state == AnimationState.RETURN:
                if not self.enemy.hp <= 0: self.enemy.action = "idle"
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.player.return_animation(self.player_position)

            elif self.enemy.hp <= 0:
                self.state = BattleState.END_SCREEN

            elif self.player.animation_state == AnimationState.IDLE:
                if not self.delay: self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.delay = None

                    self.state = BattleState.ENEMY_TURN
                    self.critical_floated = False

        elif self.state == BattleState.ENEMY_ANIMATION:
            if self.enemy.animation_state == AnimationState.APPROACH:
                self.enemy.approach_animation(self.player)
                self.delay = pygame.time.get_ticks() + random.randint(500, 3000) # random wait time before attacking

            elif self.enemy.animation_state == AnimationState.WAIT:
                self.enemy.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.enemy.animation_state = AnimationState.ATTACK
                    self.delay = None  # Reset! = True

            elif self.enemy.animation_state == AnimationState.ATTACK:
                self.enemy.attack_animation(self.player, self.enemy_attack_option)
                if self.player.hp <= 0:
                    self.player.death_animation()
                self.delay = pygame.time.get_ticks() + 1000

            elif self.enemy.animation_state == AnimationState.RETURN:
                if not self.player.hp <= 0: self.player.action = "idle"
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.enemy.return_animation(self.enemy_position)

            elif self.player.hp <= 0:
                self.state = BattleState.END_SCREEN

            elif self.enemy.animation_state == AnimationState.IDLE:
                # End of enemy's animation
                if not self.delay:
                    self.delay = pygame.time.get_ticks() + 1000 # delay before player turn

                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.combat_menu.state = "main_menu"
                    self.combat_menu.buttons_group = pygame.sprite.Group()
                    self.state = BattleState.PLAYER_TURN
                    self.critical_floated = False
                    self.delay = None
                    self.clock_time = pygame.time.get_ticks() + 20000



    def enemy_attack(self):
        self.damage_counter = 0
        self.perfect_block_counter = 0
        self.state = BattleState.ENEMY_ANIMATION
        self.enemy_attack_option = random.choice(self.enemy.moves)
        self.enemy.animation_state = AnimationState.APPROACH

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
