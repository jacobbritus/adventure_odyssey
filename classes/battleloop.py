import random

import pygame.font

from classes.UI import BattleMenu, StatusBar, EnemyStatusBar
from classes.states import AnimationState, BattleState, CombatMenuState, AttackType
from classes.screenmessages import ScreenMessages
from other.play_sound import play_sound
from other.settings import *
from collections import deque

from other.text_bg_effect import text_bg_effect


class BattleLoop:
    def __init__(self, heroes, enemies, window: pygame.Surface, offset: pygame.Vector2):
        # === general stuff ===
        self.heroes = heroes
        self.player = self.heroes[0]
        self.enemies = enemies
        self.original_enemy = enemies[0]
        self.window: pygame.Surface = window
        self.offset = offset

        # === end battle toggle ===
        self.return_to_overworld: bool = False
        self.winner = None

        # === UI setup ===
        self.combat_menu = BattleMenu(performer= heroes[0], functions = [self.get_player_input, self.end_battle])
        self.player_hp_bar = StatusBar(
            owner=self.heroes[0],
            y_offset = 0)


        self.enemy_hp_bars_test = {}

        for index, enemy in enumerate(self.enemies):
            self.enemy_hp_bars_test.update({enemy: EnemyStatusBar(
                owner = enemy)})

        # === battle state ===
        # player turn, player animation, enemy turn, enemy animation, end screen and end battle.
        participants = [*self.enemies, *self.heroes]
        participants.sort(key = lambda x: x.core_stats["speed"], reverse = True)

        self.battle_queue = deque(participants)

        self.performer = self.battle_queue[0]
        self.target = None

        if self.performer.type == "player":
            self.state = BattleState.PLAYER_TURN

        else:
            self.state = BattleState.ENEMY_TURN

        for participant in participants:
            participant.animation_state = AnimationState.IDLE

        # === selecting enemies setup ===
        for other in self.enemies:
            other.selected = True

        # === state / animation phase delay and the player turn clock ===
        self.current_time: pygame.time = pygame.time.get_ticks()

        start_delay = 1000 if self.state == BattleState.PLAYER_TURN else 2000
        self.delay: pygame.time = self.current_time + start_delay

        # === visual cues ===
        # damage, critical hit and perfect block
        self.screen_messages_group: pygame.sprite.Group = pygame.sprite.Group()
        # top screen text
        self.battle_text_string = None
        self.battle_text_surface = None
        self.battle_text_bg = None
        self.battle_text_bg_pos = None
        self.battle_text_pos = None
        self.battle_text_opacity = 0
        self.font = pygame.font.Font(FONT_ONE, 16)

        # === sound ===
        self.click_sound_played = False
        self.hover_sound_played = False



    def set_delay(self, ms):
        self.delay = self.current_time + ms

    def top_screen_description(self, window):
        if self.state in [BattleState.PLAYER_TURN]:
            for button in self.combat_menu.buttons_group:
                internal_name = button.text_string.replace(" ", "_").lower()
                if internal_name in MOVES.keys():
                    # === display the hovered attack's description ===
                    if button.hovering:
                        self.battle_text_bg = UI["battle_message_box"]["large_background"]
                        self.battle_text_string = MOVES[internal_name]["description"].upper()

                    # === display nothing ===
                    elif all(not button.hovering for button in self.combat_menu.buttons_group):
                        self.battle_text_string = None

        # === display the performed attack's name ===
        elif self.state in [BattleState.ENEMY_TURN, BattleState.ENEMY_ANIMATION, BattleState.PLAYER_ANIMATION]:
            if self.performer.current_attack:
                formatted_skill_name = self.performer.current_attack.replace("_", " ").upper()
                self.battle_text_string = f"{self.performer.name.upper()} USED {formatted_skill_name}!"
                self.battle_text_bg = UI["battle_message_box"]["large_background"]

        # === update and render the background and text ===
        if self.battle_text_string and not self.state in [BattleState.END_BATTLE]:
            self.battle_text_bg_pos = pygame.Vector2(WINDOW_WIDTH // 2 - self.battle_text_bg.get_width() // 2,
                           32)
            self.battle_text_surface = self.font.render(self.battle_text_string, True, (255, 255, 255))
            self.battle_text_pos = self.battle_text_bg_pos + (self.battle_text_bg.get_width() // 2 - self.battle_text_surface.get_width() // 2,
                                                              6)
        elif not self.battle_text_string:
            self.battle_text_surface = None
            self.battle_text_opacity = 0


        # === blit the text ===
        if self.battle_text_surface:
            self.battle_text_bg.set_alpha(min(self.battle_text_opacity, UI_OPACITY))
            self.battle_text_surface.set_alpha(min(self.battle_text_opacity, UI_OPACITY))
            self.battle_text_opacity += 20
            window.blit(self.battle_text_bg,self.battle_text_bg_pos)
            window.blit(self.battle_text_surface,self.battle_text_pos)







    def get_mouse_input(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]
        self.battle_text_string = "SELECT A TARGET"
        self.battle_text_bg = UI["battle_message_box"]["small_background"]

        for enemy in self.enemies:
            pos = pygame.Vector2(enemy.hitbox.topleft - self.offset)
            rect = pygame.Rect(pos.x, pos.y, 32, 32)
            if rect.collidepoint(mouse_pos):
                if press and not enemy.death:
                    if not self.click_sound_played:
                        play_sound("ui", "press", None)
                    self.click_sound_played = True

                    for other in self.enemies:
                        other.selected = True
                    self.target = enemy
                    self.player_turn()

                    break
                else:
                    self.battle_text_string = enemy.name.upper()

                    if not self.hover_sound_played:
                        play_sound("ui", "hover", None)
                        self.hover_sound_played = True
                    enemy.selected = True
            else:
                enemy.selected = False

        if all(not enemy.selected for enemy in self.enemies):
            self.hover_sound_played = False
            self.click_sound_played = False


    def run(self) -> None:
        """The main loop."""
        self.current_time = pygame.time.get_ticks()
        self.animations()

        self.draw_ui()



        if self.current_time >= self.delay:
            if self.state == BattleState.PLAYER_TURN:
                if self.performer.current_attack:
                    self.get_mouse_input()


            elif self.state == BattleState.ENEMY_TURN:
                self.enemy_turn()

            elif self.state == BattleState.END_BATTLE:
                self.return_to_overworld = True
                time = 5000
                self.player.post_battle_iframes = pygame.time.get_ticks() + time

            elif self.state == self.state.END_MENU:
                if self.winner == self.heroes:
                    self.battle_text_string = "BATTLE WON"
                else:
                    self.battle_text_string = "BATTLE LOST"

                # branch to win_menu and lose_menu
                self.combat_menu.state = CombatMenuState.END_MENU





    def screen_messages(self) -> None:
        """Displays and updates screen messages like damage dealt, recovered, critical hits, etc."""
        self.screen_messages_group.update()
        self.screen_messages_group.draw(self.window)

        participants = [*self.heroes, *self.enemies]

        for participant in participants:
            number_offset = 0
            for message_type, value, color in participant.screen_messages:
                if message_type in ["hp_dealt", "hp_recovered", "mana_recovered"]:
                    ScreenMessages(self.screen_messages_group, value, color, number_offset, participant)
                    number_offset += 1
                elif message_type == "perfect_block":
                    offset = -4 if participant in self.heroes else 0.5
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)
                elif message_type == "critical_hit":
                    offset = -2 if participant in self.heroes else 0.5
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)

            participant.screen_messages.clear()

    def draw_ui(self) -> None:
        """Displays and updates the UI components."""

        if not self.state in [BattleState.END_MENU, BattleState.END_BATTLE]:
            self.player_hp_bar.draw(self.window, False)

            for enemy, hp_bar in self.enemy_hp_bars_test.items():
                hp_bar.draw(self.window, enemy.screen_position + (12, 12))
        elif self.state in [BattleState.END_MENU]:


            self.player.exp_gain(sum(enemy.exp for enemy in self.enemies))
            self.player_hp_bar.draw(self.window, True)



        if self.state == BattleState.PLAYER_TURN:
            self.combat_menu.visible = True

        elif self.state == BattleState.END_MENU and all(not hero.leveling for hero in self.heroes):
            self.combat_menu.visible = True
        else:
            self.combat_menu.opacity = False

        self.combat_menu.draw(self.window, self.performer)

        self.screen_messages()

    def end_battle(self) -> None:
        """End battle when the player picks run / this function."""
        self.state = BattleState.END_BATTLE

    def get_player_input(self, attack) -> None:
        """Takes in the picked attack from the combat menu."""
        internal_attack = attack.replace(" ", "_").lower()
        self.performer.current_attack = internal_attack

        enemy_count = len([enemy for enemy in self.enemies if enemy in self.battle_queue])

        if MOVES[internal_attack]["type"] == AttackType.BUFF.value or enemy_count == 1:
            self.target = [enemy for enemy in self.battle_queue if enemy.type == "enemy"][0]
            self.player_turn()

    def player_turn(self) -> None:
        self.state = BattleState.PLAYER_ANIMATION
        self.performer.mana -= MOVES[self.performer.current_attack]["mana"]
        self.handle_attack()


    def handle_attack(self) -> None:
        """Handles the different animation start phases depending on the attack type."""
        if MOVES[self.performer.current_attack]["type"] == AttackType.PHYSICAL.value:
            self.performer.animation_state = AnimationState.APPROACH
        elif MOVES[self.performer.current_attack]["type"] == AttackType.BUFF.value:
            self.performer.spawn_projectile = False
            self.performer.animation_state = AnimationState.BUFF
        elif MOVES[self.performer.current_attack]["type"] == AttackType.SPECIAL.value:
            self.performer.spawn_projectile = False
            self.set_delay(1000)
            self.performer.animation_state = AnimationState.WAIT


    def enemy_turn(self) -> None:
        """Picks a random attack choice for the enemy."""
        self.state = BattleState.ENEMY_ANIMATION
        self.performer.current_attack = random.choice(self.performer.moves)
        self.target = random.choice(self.heroes)

        self.handle_attack()

    def animation_phases(self, performer, target) -> None:
        """Handles the different animation phases and their delays."""
        # === [ APPROACH ] > WAIT > ATTACK ===
        if performer.animation_state == AnimationState.APPROACH:
            performer.approach_animation(target)
            delay_time = 1000 if performer.type == "player" else random.randint(500, 3000)
            self.set_delay(delay_time)

        # === HURT ===
        if target.animation_state == AnimationState.HURT:
            target.hurt_animation()

            if pygame.time.get_ticks() >= target.hurt_time:
                target.action = "idle"
                target.animation_state = AnimationState.IDLE
        else:
            target.hurt_time = pygame.time.get_ticks() + 500

        # === DEATH ===
        if target.animation_state == AnimationState.DEATH:
            target.death_animation()
            if target in self.battle_queue:
                self.battle_queue.remove(target)

        # === APPROACH or NONE > [ WAIT ] > ATTACK ===
        elif performer.animation_state == AnimationState.WAIT:
            performer.wait()
            if self.current_time >= self.delay:
                if MOVES[performer.current_attack]["type"] in [AttackType.PHYSICAL.value, AttackType.SPECIAL.value]:
                    performer.animation_state = AnimationState.ATTACK
                else:
                    performer.animation_state = AnimationState.IDLE

        # === WAIT > [ ATTACK ] > RETURN OR IDLE ===
        elif performer.animation_state == AnimationState.ATTACK:

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
        elif all(enemy.hp <= 0 for enemy in self.enemies) or all(hero.hp <= 0 for hero in self.heroes):
            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.winner = self.heroes

                for hero in self.heroes:
                    hero.exp_track = 0
            else:
                self.winner = self.enemies

            self.performer.current_attack = None
            self.state = BattleState.END_MENU

        # RETURN, ATTACK OR BUFF > [ IDLE ] > END TURN
        elif performer.animation_state == AnimationState.IDLE:

            if not target.hp <= 0: target.action = "idle" # change to animation state enemy hurt in entity
            if self.current_time >= self.delay:

                self.performer.current_attack = None

                self.battle_queue.rotate(-1)
                self.performer = self.battle_queue[0]


                if self.performer.type == "player":
                    # === set an enemy target ===
                    self.target = [enemy for enemy in self.enemies if not enemy.death][0]
                    self.state = BattleState.PLAYER_TURN
                    self.combat_menu.state = CombatMenuState.MAIN_MENU
                    self.combat_menu.buttons_group = pygame.sprite.Group()
                    self.performer.mana += 1
                    self.performer.screen_messages.append(("mana_recovered", 1, (150, 206, 255)))

                else:
                    print("check2")

                    self.state = BattleState.ENEMY_TURN
                self.set_delay(1000)
                self.battle_text_string = None

    def animations(self) -> None:
        """Runs the player and enemy animation phases."""
        if self.state == BattleState.PLAYER_ANIMATION:

            self.animation_phases(self.performer, self.target)

        elif self.state == BattleState.ENEMY_ANIMATION:

            self.animation_phases(self.performer, self.target)