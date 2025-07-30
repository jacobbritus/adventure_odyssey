import random

import pygame

from classes.UI import CombatMenu, HpBar
from classes.states import AnimationState, BattleState, CombatMenuState, AttackType
from classes.screenmessages import ScreenMessages
from other.settings import *
from collections import deque

class BattleLoop:
    def __init__(self, player, enemies, window: pygame.Surface, offset: pygame.Vector2):
        # === general stuff ===
        self.player = player
        self.enemies = enemies
        self.original_enemy = enemies[0]
        self.window: pygame.Surface = window
        self.offset = offset

        # === end battle toggle ===
        self.return_to_overworld: bool = False
        self.winner = None

        # === UI setup ===
        self.combat_menu = CombatMenu(player_skills = self.player.attacks, functions = [self.player_turn, self.end_battle])
        self.player_hp_bar = HpBar(
            owner=self.player,
            side = "left",
            y_offset = 0)


        self.enemy_hp_bars_test = {}

        for index, enemy in enumerate(self.enemies):
            self.enemy_hp_bars_test.update({enemy: HpBar(
                owner = enemy,
                side="right",
                y_offset=index * 64)})

        # === battle state ===
        # player turn, player animation, enemy turn, enemy animation, end screen and end battle.
        participants = self.enemies + [self.player]
        participants.sort(key = lambda x: x.core_stats["speed"], reverse = True)

        self.battle_queue = deque(participants)

        self.performer = self.battle_queue[0]
        self.target = self.original_enemy

        if self.performer.type == "player":
            self.state = BattleState.PLAYER_TURN
        else:
            self.state = BattleState.ENEMY_TURN

        # === state / animation phase delay and the player turn clock ===
        self.current_time: pygame.time = pygame.time.get_ticks()

        start_delay = 1000 if self.state == BattleState.PLAYER_TURN else 2000
        self.delay: pygame.time = self.current_time + start_delay

        self.clock_timer: pygame.time = self.current_time + 20000
        self.clock_font: pygame.font = pygame.font.Font(FONT_TWO, 33)

        # === visual cues ===
        # damage, critical hit and perfect block
        self.screen_messages_group: pygame.sprite.Group = pygame.sprite.Group()

    def set_delay(self, ms):
        self.delay = self.current_time + ms

    def timer_(self) -> None:
        """The timer set and displayed on the player's turn."""
        if self.state == BattleState.PLAYER_TURN and self.clock_timer:
            current_clock_time = ((self.clock_timer - pygame.time.get_ticks()) // 1000)
            time_text = self.clock_font.render(str(current_clock_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            self.window.blit(time_text, (WINDOW_WIDTH // 2 - time_size // 2 + 1, self.player_hp_bar.background_box_pos[1] - 2))

    def get_mouse_input(self) -> None:
        if BattleState.PLAYER_TURN:
            mouse_pos = pygame.mouse.get_pos()
            press = pygame.mouse.get_pressed()[0]

            # debug_surface = pygame.Surface((self.hitbox.width, self.hitbox.height), pygame.SRCALPHA)
            # debug_surface.fill((255, 0, 0, 100))  # RGBA: red with 100 alpha
            # window.blit(debug_surface, (self.hitbox.topleft - offset))


            for enemy in self.enemies:
                pos = pygame.Vector2(enemy.hitbox.topleft - self.offset)
                rect = pygame.Rect(pos.x, pos.y, 32, 32)
                if rect.collidepoint(mouse_pos) and press and not enemy.death:
                    self.target = enemy
                    enemy.image = pygame.mask.from_surface(enemy.image).to_surface(setcolor=(255, 0, 0, 120),
                                                                                     unsetcolor=(0, 0, 0, 0))

    def run(self) -> None:
        """The main loop."""
        self.current_time = pygame.time.get_ticks()
        self.animations()
        self.get_mouse_input()

        if self.current_time >= self.delay:
            if self.state == BattleState.PLAYER_TURN:
                if self.clock_timer and self.current_time >= self.clock_timer:
                    self.battle_queue.rotate(-1)
                    self.performer = self.battle_queue[0]
                    self.state = BattleState.ENEMY_TURN
                    time = 20000
                    self.clock_timer = self.current_time + time

            elif self.state == BattleState.ENEMY_TURN:
                self.enemy_turn()

            elif self.state == BattleState.END_BATTLE:
                self.return_to_overworld = True
                time = 5000
                self.player.post_battle_iframes = pygame.time.get_ticks() + time

            elif self.state == self.state.END_MENU:
                self.combat_menu.state = CombatMenuState.END_MENU

    def screen_messages(self) -> None:
        """Displays and updates screen messages like damage dealt, recovered, critical hits, etc."""
        self.screen_messages_group.update()
        self.screen_messages_group.draw(self.window)

        participants = [self.player] + self.enemies

        for participant in participants:
            number_offset = 0
            for message_type, value, color in participant.screen_messages:
                if message_type in ["hp_dealt", "hp_recovered", "mana_recovered"]:
                    ScreenMessages(self.screen_messages_group, value, color, number_offset, participant)
                    number_offset += 1
                elif message_type == "perfect_block":
                    offset = -4 if participant == self.player else 0.5
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)
                elif message_type == "critical_hit":
                    offset = -2 if participant == self.player else 0.5
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)

            participant.screen_messages.clear()

    def draw_ui(self) -> None:
        """Displays and updates the UI components."""
        self.timer_()

        if self.state == BattleState.PLAYER_TURN or self.state == BattleState.END_MENU:
            self.combat_menu.draw(self.window, self.player.mana)

        # === draw the target's hp_bar when
        if self.state in [BattleState.PLAYER_ANIMATION, BattleState.ENEMY_ANIMATION]:
            if moves[self.performer.current_attack]["type"] in [AttackType.PHYSICAL.value, AttackType.SPECIAL.value]:
               if self.performer == self.player:
                   self.enemy_hp_bars_test[self.target].draw(self.window)

               elif self.performer in self.enemies:
                  self.player_hp_bar.draw(self.window)
            else:
                if self.performer in self.enemies:
                    self.enemy_hp_bars_test[self.performer].draw(self.window)
                elif self.performer == self.player:
                    self.player_hp_bar.draw(self.window)

        elif self.state in [BattleState.PLAYER_TURN, BattleState.ENEMY_TURN]:
            self.player_hp_bar.draw(self.window)
            for hp_bar in self.enemy_hp_bars_test.values():
                hp_bar.draw(self.window)
        self.screen_messages()

    def end_battle(self) -> None:
        """End battle when the player picks run / this function."""
        self.state = BattleState.END_BATTLE

    def player_turn(self, attack) -> None:
        """Takes in the picked attack from the combat menu."""
        internal_attack = attack.replace(" ", "_").lower()
        self.state = BattleState.PLAYER_ANIMATION
        self.player.current_attack = internal_attack
        self.player.mana -= moves[internal_attack]["mana"]

        self.handle_attack(self.player, self.player.current_attack)

    def handle_attack(self, performer, attack_name) -> None:
        """Handles the different animation start phases depending on the attack type."""
        if moves[attack_name]["type"] == AttackType.PHYSICAL.value:
            performer.animation_state = AnimationState.APPROACH
        elif moves[attack_name]["type"] == AttackType.BUFF.value:
            performer.spawn_projectile = False
            performer.animation_state = AnimationState.BUFF
        elif moves[attack_name]["type"] == AttackType.SPECIAL.value:
            performer.spawn_projectile = False
            self.set_delay(1000)
            performer.animation_state = AnimationState.WAIT

    def enemy_turn(self) -> None:
        """Picks a random attack choice for the enemy."""
        self.state = BattleState.ENEMY_ANIMATION
        self.performer.current_attack = random.choice(self.original_enemy.moves)
        self.target = self.player

        self.handle_attack(self.performer, self.performer.current_attack)

    def animation_phases(self, performer, target) -> None:
        """Handles the different animation phases and their delays."""
        # === [ APPROACH ] > WAIT > ATTACK ===
        if performer.animation_state == AnimationState.APPROACH:
            performer.approach_animation(target)
            delay_time = 1000 if performer.type == "player" else random.randint(500, 3000)
            self.set_delay(delay_time)

        # === DEATH ===
        if target.animation_state == AnimationState.DEATH:
            target.death_animation()
            if target in self.battle_queue:
                self.battle_queue.remove(target)

        # === APPROACH or NONE > [ WAIT ] > ATTACK ===
        elif performer.animation_state == AnimationState.WAIT:
            performer.wait()
            if self.current_time >= self.delay:
                if moves[performer.current_attack]["type"] in [AttackType.PHYSICAL.value, AttackType.SPECIAL.value]:
                    performer.animation_state = AnimationState.ATTACK
                else:
                    performer.animation_state = AnimationState.IDLE

        # === WAIT > [ ATTACK ] > RETURN OR IDLE ===
        elif performer.animation_state == AnimationState.ATTACK:
            if target.animation_state == AnimationState.HURT:
                target.hurt_animation()
                if pygame.time.get_ticks() >= target.hurt_time:
                    target.action = "idle"
                    target.animation_state = AnimationState.IDLE
            else:
                target.hurt_time = pygame.time.get_ticks() + 500

            performer.attack_animation(target, performer.current_attack)
            # self.set_delay(500)

        # === [ BUFF ] > IDLE ====
        elif performer.animation_state == AnimationState.BUFF:
            performer.buff_animation()
            self.set_delay(2000)


        # === ATTACK > [ RETURN ] > IDLE ===
        elif performer.animation_state == AnimationState.RETURN:
            if not target.hp <= 0: target.action = "idle" # change to animation state enemy hurt in entity

            if self.current_time >= self.delay:
                performer.return_animation(performer.battle_pos)

        # === END MENU ===
        elif all(enemy.hp <= 0 for enemy in self.enemies) or self.player.death:
            self.winner = self.player
            self.state = BattleState.END_MENU

        # RETURN, ATTACK OR BUFF > [ IDLE ] > END TURN
        elif performer.animation_state == AnimationState.IDLE:
            if not target.hp <= 0: target.action = "idle" # change to animation state enemy hurt in entity
            if self.current_time >= self.delay:


                self.battle_queue.rotate(-1)
                self.performer = self.battle_queue[0]

                if self.performer.type == "player":
                    # === set an enemy target ===
                    self.target = [enemy for enemy in self.enemies if not enemy.death][0]

                    self.state = BattleState.PLAYER_TURN
                    self.combat_menu.state = CombatMenuState.MAIN_MENU
                    self.combat_menu.buttons_group = pygame.sprite.Group()
                    self.player.mana += 1
                    self.player.screen_messages.append(("mana_recovered", 1, (150, 206, 255)))

                    self.clock_timer = pygame.time.get_ticks() + 20000
                else:
                    self.state = BattleState.ENEMY_TURN

                self.set_delay(1000)

    def animations(self) -> None:
        """Runs the player and enemy animation phases."""
        if self.state == BattleState.PLAYER_ANIMATION:

            self.animation_phases(self.player, self.target)

        elif self.state == BattleState.ENEMY_ANIMATION:

            self.animation_phases(self.performer, self.target)








