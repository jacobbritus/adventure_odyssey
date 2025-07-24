import random

from classes.UI import CombatMenu, Hpbar
from classes.states import AnimationState, BattleState
from classes.screenmessages import ScreenMessages
from other.settings import *

# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy, window: pygame.Surface, offset):
        # __general___
        self.player = player
        self.enemy = enemy
        self.window: pygame.Surface = window
        self.offset = offset

        # ___idle positions___
        self.player_position: pygame.Vector2 = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy_position: pygame.Vector2 = pygame.Vector2(enemy.x, enemy.y)

        # ___end battle toggle___
        self.return_to_overworld: bool = False

        # ___UI setup___
        self.combat_menu = CombatMenu(self.player.attacks, [self.player_attack, self.player_run, self.player_run])
        self.combat_menu.state = "main_menu"
        self.player_hp_bar = Hpbar("left", self.player.level, self.player.hp, self.player.max_hp, self.player.mana,"PLAYER") #enemy.name in the future
        self.player_hp_bar.set_hp(self.player.hp) # Update player's hp
        self.enemy_hp_bar = Hpbar("right", self.enemy.level, self.enemy.hp, self.enemy.hp, None, self.enemy.monster_name.upper()) #enemy.name in the future

        # ___used as an argument to perform the chosen attack option___
        self.player_attack_option = None
        self.enemy_attack_option = None

        # ___state___
        if self.player.speed >= self.enemy.speed:
            self.state = BattleState.PLAYER_TURN
        elif self.enemy.speed >= self.player.speed:
            self.state = BattleState.ENEMY_TURN
        else:
            self.state = random.choice([BattleState.PLAYER_TURN, BattleState.ENEMY_TURN])

        # ___delays and the clock___
        self.delay = pygame.time.get_ticks() + 1000 # set if enemy starts first
        self.clock_time = pygame.time.get_ticks() + 20000

        # ___screen messages___
        self.screen_messages_group = pygame.sprite.Group()

        # ___block and crit hotkey___
        self.block_duration = 250 # blocking last time
        self.block_cooldown_end = 0 # when blocking ends
        self.block = False # whether blocking is True
        self.block_delay = 250

        # ___reward___
        self.reward_given = False

    def timer_(self) -> None:
        if self.state == BattleState.PLAYER_TURN and self.clock_time and not pygame.time.get_ticks() >= self.clock_time:

            current_time = ((self.clock_time - pygame.time.get_ticks()) // 1000)

            font = pygame.font.Font(FONT_TWO, 33)
            time_text = font.render(str(current_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            self.window.blit(time_text, (WINDOW_WIDTH // 2 - time_size // 2 + 1, self.player_hp_bar.box_pos[1] - 2))

    def handle_projectiles(self) -> None:
        self.player.projectiles.draw(self.window)
        self.enemy.projectiles.draw(self.window)
        if self.player.animation_state == AnimationState.ATTACK:
            self.player.projectiles.update(self.player.hitbox.center - self.offset, self.offset)
        elif self.player.animation_state == AnimationState.BUFF:
            self.player.projectiles.update(self.player.hitbox.center - self.offset, self.offset)
        elif self.enemy.animation_state == AnimationState.ATTACK:
            self.enemy.projectiles.update(self.enemy.hitbox.center - self.offset, self.offset)
        elif self.enemy.animation_state == AnimationState.BUFF:
            self.enemy.projectiles.update(self.enemy.hitbox.center - self.offset, self.offset)

    def run(self) -> None:
        self.handle_projectiles()
        self.handle_input()
        self.animation()

        if not self.delay or pygame.time.get_ticks() >= self.delay:
            if self.state == BattleState.PLAYER_TURN:
                if self.clock_time and pygame.time.get_ticks() >= self.clock_time:
                    self.state = BattleState.ENEMY_TURN
                    self.clock_time = pygame.time.get_ticks() + 20000

            elif self.state == BattleState.ENEMY_TURN:
                    self.enemy_turn()
                    self.delay = None

            elif self.state == BattleState.END_BATTLE:
                    if self.enemy.death: self.enemy.respawn_time = pygame.time.get_ticks() + 120000
                    self.return_to_overworld = True
                    if self.enemy.hp <= 0 and not self.reward_given:
                        self.player.exp += self.enemy.exp
                        if self.player.exp >= self.player.exp_to_level:
                            self.player.level += 1
                            self.player.exp = 0
                            self.player.exp_to_level += 20
                        self.reward_given = True

            elif self.state == self.state.END_SCREEN:
                self.combat_menu.state = "end_screen"

    def action_lock(self) -> bool:
        return (
                self.player.animation_state == AnimationState.APPROACH or
                self.enemy.animation_state == AnimationState.APPROACH or
                self.player.animation_state == AnimationState.WAIT or
                self.enemy.animation_state == AnimationState.WAIT
        )

    def screen_messages(self):
        self.screen_messages_group.update()

        self.screen_messages_group.draw(self.window)


        for participant in [self.player, self.enemy]:
            damage_counter = 0
            for dmg in participant.dmg_taken:
                ScreenMessages(self.screen_messages_group, dmg, (255, 0, 0), damage_counter, participant)
                damage_counter += 1 # increments moce the x position
            participant.dmg_taken.clear()

            for mana in participant.mana_messages:
                ScreenMessages(self.screen_messages_group, mana, (150, 206, 255), 0, participant)
            participant.mana_messages.clear()

            if participant.critical_hit_messages:
                offset = -2 if participant == self.player else 0.5

                ScreenMessages(self.screen_messages_group, "CRITICAL HIT", (0, 0, 255), offset, participant)
                participant.critical_hit_messages.clear()

            if participant.perfect_block_messages:
                offset = -3.5 if participant == self.player else 1
                ScreenMessages(self.screen_messages_group, "PERFECT BLOCK", (0, 255, 0), offset, participant)
                participant.perfect_block_messages.clear()



    def draw_ui(self):
        self.timer_()

        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar.set_hp(self.enemy.hp)
        self.player_hp_bar.set_mana(self.player.mana)  
        self.enemy_hp_bar.update()
        self.player_hp_bar.update()

        if self.state == BattleState.PLAYER_TURN or self.state == BattleState.END_SCREEN:
            self.combat_menu.draw(self.window, self.player.mana)

        self.player_hp_bar.draw(self.window)
        self.enemy_hp_bar.draw(self.window)
        self.screen_messages()



    def handle_input(self):
        if self.block and pygame.time.get_ticks() >= self.block_cooldown_end:
            self.block = False
            self.player.blocking = False

    def hotkeys(self, event):
            current_time = pygame.time.get_ticks()

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
        self.state = BattleState.PLAYER_ANIMATION
        self.player.current_attack = self.player_attack_option
        self.player.mana -= moves[self.player_attack_option]["mana"]

        if moves[self.player_attack_option]["type"] == "physical":
            self.player.animation_state = AnimationState.APPROACH
        elif moves[self.player_attack_option]["type"] == "buff":
            self.player.spawn_projectile = False
            self.player.animation_state = AnimationState.BUFF
        elif moves[self.player_attack_option]["type"] == "special":
            if self.player.current_attack == "combustion":
                self.player.animation_state = AnimationState.APPROACH
            else:
                self.player.spawn_projectile = False
                self.delay = pygame.time.get_ticks() + 1000
                self.player.animation_state = AnimationState.WAIT



    def animation(self):
        if self.state == BattleState.PLAYER_ANIMATION:
            if self.player.animation_state == AnimationState.APPROACH:
                self.player.approach_animation(self.enemy)
                self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking


            if self.enemy.hp <= 0 and not self.enemy.death:
                self.enemy.death_animation()

            elif self.player.animation_state == AnimationState.WAIT:

                self.player.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.player.animation_state = AnimationState.ATTACK
                    self.delay = None

            elif self.player.animation_state == AnimationState.ATTACK:
                self.player.attack_animation(self.enemy, self.player_attack_option) # self.player_attack

                self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking

            elif self.player.animation_state == AnimationState.BUFF:
                self.player.buff_animation()
                self.delay = pygame.time.get_ticks() + 1000  # wait time before attacking


            elif self.player.animation_state == AnimationState.RETURN:
                if not self.enemy.hp <= 0: self.enemy.action = "idle"
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.player.return_animation(self.player_position)

            elif self.enemy.hp <= 0:
                self.state = BattleState.END_SCREEN

            elif self.player.animation_state == AnimationState.IDLE:
                if not self.enemy.hp <= 0: self.enemy.action = "idle"

                if not self.delay: self.delay = pygame.time.get_ticks() + 1000  # wait time enemy attacking
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.delay = None

                    self.state = BattleState.ENEMY_TURN

        elif self.state == BattleState.ENEMY_ANIMATION:
            if self.enemy.animation_state == AnimationState.APPROACH:
                self.enemy.approach_animation(self.player)
                self.delay = pygame.time.get_ticks() + random.randint(500, 3000) # random wait time before attacking

            elif self.enemy.animation_state == AnimationState.WAIT:
                if not self.player.hp <= 0: self.player.action = "idle"
                self.enemy.wait()
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.enemy.animation_state = AnimationState.ATTACK
                    self.delay = None  # Reset! = True

            elif self.enemy.animation_state == AnimationState.ATTACK:
                self.enemy.attack_animation(self.player, self.enemy_attack_option)

                self.delay = pygame.time.get_ticks() + 1000

            elif self.enemy.animation_state == AnimationState.BUFF:
                self.enemy.buff_animation()
                self.delay = pygame.time.get_ticks() + 1000  # wait time before player turn

            elif self.enemy.animation_state == AnimationState.RETURN:
                if not self.player.hp <= 0: self.player.action = "idle"
                if self.delay and pygame.time.get_ticks() >= self.delay:
                    self.enemy.return_animation(self.enemy_position)

            if self.player.hp <= 0:
                self.player.death_animation()

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
                    self.player.mana += 1
                    self.player.mana_messages.append(1)
                    self.delay = None
                    self.clock_time = pygame.time.get_ticks() + 20000



    def enemy_turn(self):
        self.state = BattleState.ENEMY_ANIMATION
        self.enemy_attack_option = random.choice(self.enemy.moves)
        self.enemy.current_attack = self.enemy_attack_option

        if moves[self.enemy_attack_option]["type"] == "physical":
            self.enemy.animation_state = AnimationState.APPROACH
        elif moves[self.enemy_attack_option]["type"] == "buff":
            self.enemy.spawn_projectile = False
            self.enemy.animation_state = AnimationState.BUFF




