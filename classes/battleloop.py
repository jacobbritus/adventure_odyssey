import random

import pygame.font

from classes.UI import BattleMenu, EnemyStatusBar
from classes.pointer import Pointer
from classes.states import AnimationState, BattleState, BattleMenuState, AttackType
from classes.screenmessages import ScreenMessages
from other.play_sound import play_sound
from other.settings import *
from collections import deque



class BattleLoop:
    def __init__(self, heroes, enemies, window: pygame.Surface, offset: pygame.Vector2):
        # === general stuff ===
        self.heroes = heroes
        self.player = self.heroes[0]
        self.enemies = enemies
        self.original_enemy = enemies[0]
        self.window: pygame.Surface = window
        self.offset = offset
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # === end battle toggle ===
        self.return_to_overworld: bool = False
        self.winner = None

        # === UI setup ===
        self.battle_menu = BattleMenu(self.player, performer=heroes[0], functions=[self.get_player_input, self.end_battle])

        for hero in self.heroes:
            hero.status_bar.visible = True
            # hero.hp_bar.setup_hero_status_bar(0)

        self.enemy_hp_bars_test = {}

        for index, enemy in enumerate(self.enemies):
            self.enemy_hp_bars_test.update({enemy: EnemyStatusBar(
                owner=enemy)})

        # === battle state ===
        # player turn, player animation, enemy turn, enemy animation, end screen and end battle.
        participants = [*self.enemies, *self.heroes]
        participants.sort(key=lambda x: x.core_stats["speed"], reverse=True)

        self.battle_queue = deque(participants)

        self.performer = self.battle_queue[0]
        self.performer.performing = True
        self.target = None

        if self.performer in self.heroes:
            self.state = BattleState.PLAYER_TURN
            self.battle_menu.state = BattleMenuState.MAIN_MENU
        else:
            self.state = BattleState.ENEMY_TURN

        for participant in participants:
            participant.animation_state = AnimationState.IDLE

        # === selecting enemies setup ===
        for other in self.enemies:
            other.selected = True
        self.selected_target_index = 0
        self.mouse_navigation = False

        # === state / animation phase delay ===
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

        # turn pointer
        self.turn_pointer = Pointer(variant = "tick_pointer", direction = "down")
        self.select_pointer = Pointer(variant = "hand_pointer", direction = "down")

        # === sound for selecting target ===
        self.click_sound_played = False
        self.hover_sound_played = False

    def set_delay(self, ms):
        self.delay = self.current_time + round(ms / 2)

    def top_screen_description(self, window):
        if self.state == BattleState.PLAYER_TURN:
            for button in self.battle_menu.buttons_group:

                if button.text_string in self.battle_menu.formatted_skills:
                    internal_name = button.text_string.replace(" ", "_").lower()
                    data = SKILLS
                elif button.text_string[0].replace(" ", "_").lower() in self.player.inventory.items.keys():
                    internal_name = button.text_string[0].replace(" ", "_").lower()
                    data = ITEMS
                else:
                    internal_name = None
                    data = None

                # === display the hovered attack's description ===
                if button.hovering and internal_name:
                    self.battle_text_bg = UI["battle_message_box"]["large_background"]
                    self.battle_text_string = data[internal_name]["description"].upper()

                # === display nothing ===
                elif all(not button.hovering for button in self.battle_menu.buttons_group):
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
            self.battle_text_surface = self.font.render(self.battle_text_string, True, (236, 226, 196))
            self.battle_text_pos = self.battle_text_bg_pos + (
                self.battle_text_bg.get_width() // 2 - self.battle_text_surface.get_width() // 2,
                6)
        elif not self.battle_text_string:
            self.battle_text_surface = None
            self.battle_text_opacity = 0

        # === blit the text ===
        if self.battle_text_surface:
            self.battle_text_bg.set_alpha(min(self.battle_text_opacity, UI_OPACITY))
            self.battle_text_surface.set_alpha(min(self.battle_text_opacity, 255))

            self.battle_text_opacity += 10
            window.blit(self.battle_text_bg, self.battle_text_bg_pos)
            window.blit(self.battle_text_surface, self.battle_text_pos)

    def selecting_target_hotkeys(self, event):
        if event.type == pygame.KEYDOWN and self.state == BattleState.PLAYER_TURN and self.performer.current_attack:

            # === target navigation ===
            if event.key in [pygame.K_w, pygame.K_s]:
                pre = self.selected_target_index

                # === go up ===
                if event.key == pygame.K_w:
                    if not self.enemies[self.selected_target_index - 1].death:
                        self.selected_target_index = max(self.selected_target_index - 1, 0)



                # === go down ===
                elif event.key == pygame.K_s:
                    if not self.selected_target_index == len(self.enemies) - 1 and not self.enemies[self.selected_target_index + 1].death:

                        self.selected_target_index = min(self.selected_target_index + 1, len(self.enemies) - 1)


                post = self.selected_target_index

                if not pre == post:
                    play_sound("ui", "hover", None)

            # === pick target ===
            elif event.key == pygame.K_c:
                self.target = self.enemies[self.selected_target_index]
                self.process_attack_option()

                for enemy in self.enemies:
                    enemy.selected = True




    def selecting_target(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        press = pygame.mouse.get_pressed()[0]

        if self.battle_text_bg_pos:
            rect = UI["battle_message_box"]["small_background"].get_rect(topleft = self.battle_text_bg_pos)

            # === cancel attack ===
            if rect.collidepoint(mouse_pos) and press:
                self.performer.current_attack = None
                self.battle_menu.state = BattleMenuState.MAIN_MENU
                for enemy in self.enemies:
                    enemy.selected = True

        if self.state == BattleState.PLAYER_TURN and self.performer.current_attack:
            self.battle_text_string = "SELECT A TARGET"
            self.battle_text_bg = UI["battle_message_box"]["small_background"]

            for enemy in self.enemies:
                pos = pygame.Vector2(enemy.hitbox.topleft - self.offset)
                rect = pygame.Rect(pos.x, pos.y, 32, 32)
                if rect.collidepoint(mouse_pos):
                    self.mouse_navigation = True

                    if press and not enemy.death:
                        if not self.click_sound_played:
                            play_sound("ui", "press", None)
                        self.click_sound_played = True

                        for other in self.enemies:
                            other.selected = True
                        self.target = enemy
                        self.process_attack_option()

                        break
                    else:
                        self.select_pointer.draw(self.window, enemy.screen_position + (32, -12), "down")

                        self.battle_text_string = enemy.name.upper()

                        if not self.hover_sound_played:
                            play_sound("ui", "hover", None)
                            self.hover_sound_played = True

                        for other_enemy in self.enemies:
                            if other_enemy == enemy:
                                continue
                            other_enemy.selected = False
                        enemy.selected = True
                else:
                    self.mouse_navigation = False
                    enemy.selected = False


            if not self.mouse_navigation:
                enemy = self.enemies[self.selected_target_index]

                self.select_pointer.draw(self.window, enemy.screen_position + (32, -12), "down")

                self.battle_text_string = enemy.name.upper()
                enemy.selected = True

                for other_enemy in self.enemies:
                    if other_enemy == enemy:
                        continue
                    other_enemy.selected = False





            if all(not enemy.selected for enemy in self.enemies):
                self.hover_sound_played = False
                self.click_sound_played = False

    def run(self) -> None:
        """The main loop."""
        self.current_time = pygame.time.get_ticks()
        self.animations()

        self.selecting_target()


        if self.current_time >= self.delay:
            if self.state == BattleState.PLAYER_TURN:
                pass

            elif self.state == BattleState.ENEMY_TURN:
                self.enemy_turn()

            elif self.state == BattleState.END_BATTLE:
                time = 3000
                self.player.post_battle_iframes = pygame.time.get_ticks() + time
                self.return_to_overworld = True


            elif self.state == self.state.END_MENU:
                if self.winner == self.heroes:
                    self.battle_text_string = "BATTLE WON"
                else:
                    self.battle_text_string = "BATTLE LOST"

                # branch to win_menu and lose_menu
                self.battle_menu.state = BattleMenuState.END_MENU


    def screen_messages(self) -> None:
        """Displays and updates screen messages like damage dealt, recovered, critical hits, etc."""
        for screen_message in self.screen_messages_group:
            screen_message.update()
            screen_message.draw(self.window)


        participants = [*self.heroes, *self.enemies]

        for participant in participants:
            number_offset = 0
            for message_type, value, color in participant.screen_messages:
                if message_type in ["hp_dealt", "hp_recovered", "mana_recovered"]:
                    ScreenMessages(self.screen_messages_group, value, color, number_offset, participant)
                    number_offset += 1
                elif message_type == "perfect_block":
                    offset = -4 if participant in self.heroes else 1
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)
                elif message_type == "critical_hit":
                    offset = -2 if participant in self.heroes else 0.5
                    ScreenMessages(self.screen_messages_group, value, color, offset, participant)

            participant.screen_messages.clear()

    def draw_ui(self) -> None:
        """Displays and updates the UI components."""

        # == display heroes status bars ===
        for hero in self.heroes:
            hero.status_bar.draw(self.window)

        # === handle heroes exp gain and display exp on status bar
        if self.winner == self.heroes:
            for hero in self.heroes:
                hero.calculate_exp()

            # === end the sequence ===
            if not all(hero.leveling for hero in self.heroes):
                self.state = BattleState.END_BATTLE
                for hero in self.heroes:
                    hero.status_bar.visible = False

        # === display enemy status bars ===
        for enemy, hp_bar in self.enemy_hp_bars_test.items():
            if enemy.screen_position:
                hp_bar.draw(self.window, pos = enemy.screen_position + (12, 12))

        # === highlight the target's hp bar and dim others whenever a hero attacks ===
        if self.state == BattleState.PLAYER_ANIMATION:
            for enemy, hp_bar in self.enemy_hp_bars_test.items():
                if enemy == self.target:
                    continue
                if not enemy.death:
                    hp_bar.opacity = 100
        else:
            for enemy, hp_bar in self.enemy_hp_bars_test.items():
                if not enemy.death:
                    hp_bar.opacity = UI_OPACITY

        # === turn pointers ===
        if self.performer and not self.performer.current_attack and not self.state in [BattleState.END_BATTLE, BattleState.END_MENU]:
            color = "blue" if self.performer in self.heroes else "red"
            self.turn_pointer.draw(self.window, self.performer.screen_position + (32, -2) , "down", color = color)


        # === display battle menu ===
        if self.state == BattleState.PLAYER_TURN or self.winner == self.enemies:
            self.battle_menu.visible = True
        else:
            self.battle_menu.visible = False

        if not self.winner == self.heroes:
            self.battle_menu.draw(self.window, self.performer)

        self.screen_messages()

    def end_battle(self) -> None:
        """End battle when the player picks run / this function."""
        self.state = BattleState.END_BATTLE

    def get_player_input(self, attack) -> None:
        """Takes in the picked attack from the combat menu."""
        if attack in self.battle_menu.formatted_skills:
            internal_attack = attack.replace(" ", "_").lower()
            self.performer.current_attack = internal_attack

            enemy_count = len([enemy for enemy in self.enemies if enemy in self.battle_queue])

            if SKILLS[internal_attack]["type"] == AttackType.BUFF.value or enemy_count == 1:
                self.target = [enemy for enemy in self.enemies if not enemy.death][0]

        else:
            internal_item = attack[0].replace(" ", "_").lower()
            self.performer.current_attack = internal_item
            self.player.inventory.items[internal_item] -= 1

        self.process_attack_option()


    def process_attack_option(self) -> None:
        if self.performer.current_attack in SKILLS.keys() and self.target:
            self.performer.mana -= SKILLS[self.performer.current_attack]["mana"]
            self.handle_attack_type()
            self.state = BattleState.PLAYER_ANIMATION if self.performer in self.heroes else BattleState.ENEMY_ANIMATION


        elif self.performer.current_attack in ITEMS.keys():
            self.performer.animation_state = AnimationState.ITEM
            self.target = self.performer
            self.set_delay(4000)

            self.state = BattleState.PLAYER_ANIMATION if self.performer in self.heroes else BattleState.ENEMY_ANIMATION

    def handle_attack_type(self) -> None:
        """Handles the different animation start phases depending on the attack type."""

        if SKILLS[self.performer.current_attack]["type"] == AttackType.PHYSICAL.value:
            self.performer.animation_state = AnimationState.APPROACH
        elif SKILLS[self.performer.current_attack]["type"] == AttackType.BUFF.value:
            self.performer.spawn_projectile = False
            self.performer.animation_state = AnimationState.BUFF
        elif SKILLS[self.performer.current_attack]["type"] == AttackType.SPECIAL.value:
            self.performer.spawn_projectile = False
            self.set_delay(1000)
            self.performer.animation_state = AnimationState.WAIT

    def enemy_turn(self) -> None:
        """Picks a random attack choice for the enemy."""
        self.state = BattleState.ENEMY_ANIMATION

        self.target = self.performer.battle_ai([hero for hero in self.heroes if not hero.death])


        self.process_attack_option()


    def animation_phases(self, performer, target) -> None:
        """Handles the different animation phases and their delays."""
        # === [ APPROACH ] > WAIT > ATTACK ===
        if performer.animation_state == AnimationState.APPROACH:
            performer.approach_animation(target)
            delay_time = 500 if performer in self.heroes else random.randint(250, 1500)
            self.set_delay(delay_time)

        if performer.animation_state == AnimationState.ITEM:
            performer.item_animation(self.display_surface)
            if pygame.time.get_ticks() >= self.delay:
                performer.animation_state = AnimationState.IDLE
                performer.used_item = False
                performer.item_name = None



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

        if performer.animation_state == AnimationState.DEATH:
            performer.death_animation()



        # === APPROACH or NONE > [ WAIT ] > ATTACK ===
        elif performer.animation_state == AnimationState.WAIT:
            performer.wait()
            if self.current_time >= self.delay:
                if SKILLS[performer.current_attack]["type"] in [AttackType.PHYSICAL.value, AttackType.SPECIAL.value]:
                    performer.animation_state = AnimationState.ATTACK
                else:
                    performer.animation_state = AnimationState.IDLE

        # === WAIT > [ ATTACK ] > RETURN OR IDLE ===
        elif performer.animation_state == AnimationState.ATTACK:

            performer.attack_animation(target, performer.current_attack)
            self.set_delay(1000)

        # === [ BUFF ] > IDLE ====
        elif performer.animation_state == AnimationState.BUFF:
            performer.buff_animation()
            self.set_delay(2000)


        # === ATTACK > [ RETURN ] > IDLE ===
        elif performer.animation_state == AnimationState.RETURN:
            if not target.hp <= 0: target.action = "idle"  # change to animation state enemy hurt in entity

            if self.current_time >= self.delay:
                performer.return_animation(performer.battle_pos)

        # === END MENU ===
        elif all(enemy.hp <= 0 for enemy in self.enemies) or all(hero.hp <= 0 for hero in self.heroes):
            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.winner = self.heroes
                for hero in self.heroes:
                    hero.total_exp += sum(enemy.exp_given for enemy in self.enemies)
            else:
                self.winner = self.enemies

            self.performer.current_attack = None
            self.performer.performing = False

            self.state = BattleState.END_MENU


        # RETURN, ATTACK OR BUFF > [ IDLE ] > END TURN
        elif performer.animation_state in [AnimationState.IDLE, None]:



            # if not target.hp <= 0: target.action = "idle"  # change to animation state enemy hurt in entity
            if self.current_time >= self.delay:
                self.performer.handle_status_effect()

                if self.performer.hp <= 0 and not self.performer.death:
                    self.performer.animation_state = AnimationState.DEATH
                    return

                # === move the auto selected target ===
                if self.target.death and self.performer in self.heroes:
                    for i in range(len(self.enemies)):
                        if self.enemies[i].death:
                            continue
                        else:
                            self.selected_target_index = i
                            break


                self.performer.current_attack = None
                self.target = None

                self.battle_queue.rotate(-1)

                if not self.performer.mana == self.performer.max_mana:
                    self.performer.mana = self.performer.mana + 1
                    self.performer.screen_messages.append(("mana_recovered", "1 SP", (99, 155, 255)))

                self.performer.performing = False
                self.performer = self.battle_queue[0]
                self.performer.performing = True


                if self.winner:
                    self.battle_menu.state = BattleMenuState.END_MENU
                    self.battle_menu.buttons_group = pygame.sprite.Group()

                elif self.performer in self.heroes:
                    # === set an enemy target ===
                    self.state = BattleState.PLAYER_TURN
                    self.battle_menu.state = BattleMenuState.MAIN_MENU
                    self.battle_menu.buttons_group = pygame.sprite.Group()



                else:
                    self.state = BattleState.ENEMY_TURN


                self.set_delay(2000)
                self.battle_text_string = None

    def animations(self) -> None:
        """Runs the player and enemy animation phases."""
        if self.state in [BattleState.PLAYER_ANIMATION, BattleState.ENEMY_ANIMATION]:
            self.animation_phases(self.performer, self.target)
