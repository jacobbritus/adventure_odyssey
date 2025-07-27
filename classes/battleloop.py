import random
from classes.UI import CombatMenu, HpBar
from classes.states import AnimationState, BattleState, CombatMenuState, AttackType
from classes.screenmessages import ScreenMessages
from other.settings import *

class BattleLoop:
    def __init__(self, player, enemy, window: pygame.Surface, offset: pygame.Vector2):
        # === general stuff ===
        self.player = player
        self.enemy = enemy[0]
        # self.enemy2 = enemy[1]
        self.window: pygame.Surface = window
        self.offset = offset

        # === idle positions ===
        self.player.battle_pos = pygame.Vector2(player.x - self.player.width, player.y)
        self.enemy.battle_pos = pygame.Vector2(self.enemy.x, self.enemy.y)
        # self.enemy2.battle_pos = pygame.Vector2(self.enemy2.x ,self.enemy2.y)

        # === end battle toggle ===
        self.return_to_overworld: bool = False

        # === UI setup ===
        self.combat_menu = CombatMenu(player_skills = self.player.attacks, functions = [self.player_turn, self.end_battle])
        self.player_hp_bar = HpBar(
            side = "left",
            level = self.player.level,
            current_hp = self.player.hp,
            max_hp = self.player.max_hp,
            mana = self.player.mana,
            name = "PLAYER")
        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar = HpBar(
            side = "right",
            level = self.enemy.level,
            current_hp = self.enemy.hp,
            max_hp = self.enemy.hp,
            mana = None,
            name = self.enemy.monster_name.upper())



        # === battle state ===
        # player turn, player animation, enemy turn, enemy animation, end screen and end battle.
        if self.player.speed >= self.enemy.speed:
            self.state = BattleState.PLAYER_TURN
        elif self.enemy.speed >= self.player.speed:
            self.state = BattleState.ENEMY_TURN
        else:
            self.state = random.choice([BattleState.PLAYER_TURN, BattleState.ENEMY_TURN])

        # === state / animation phase delay and the player turn clock ===
        self.current_time: pygame.time = pygame.time.get_ticks()

        start_delay = 1000 if self.state == BattleState.PLAYER_TURN else 2000
        self.delay: pygame.time = self.current_time + start_delay

        self.clock_timer: pygame.time = self.current_time + 20000
        self.clock_font: pygame.font = pygame.font.Font(FONT_TWO, 33)

        # === visual cues ===
        # damage, critical hit and perfect block
        self.screen_messages_group: pygame.sprite.Group = pygame.sprite.Group()

        # === block and critical hit hotkey ===
        self.block_duration: int = 150 # blocking last time
        self.block_cooldown_end: int = 0 # when blocking ends
        self.block_delay: int = 500
        self.enemy_block_duration = None

    def set_delay(self, ms):
        self.delay = self.current_time + ms

    def timer_(self) -> None:
        """The timer set and displayed on the player's turn."""
        if self.state == BattleState.PLAYER_TURN and self.clock_timer:
            current_clock_time = ((self.clock_timer - pygame.time.get_ticks()) // 1000)
            time_text = self.clock_font.render(str(current_clock_time), True, (255, 255, 255))
            time_size = time_text.get_width()
            self.window.blit(time_text, (WINDOW_WIDTH // 2 - time_size // 2 + 1, self.player_hp_bar.background_box_pos[1] - 2))

# to be cleaned when the Spells class is improved.
    def handle_projectiles(self) -> None:
        self.player.projectiles.draw(self.window)
        self.enemy.projectiles.draw(self.window)

        self.player.stationary_spells.update((self.player.hitbox.center - pygame.Vector2(
            int(self.offset.x), int(self.offset.y))))
        self.player.stationary_spells.draw(self.window)

        if self.player.animation_state == AnimationState.ATTACK:
            self.player.projectiles.update(self.player.hitbox.center - self.offset, self.offset, self.enemy)
        elif self.player.animation_state == AnimationState.BUFF:
            self.player.stationary_spells.update(self.player.hitbox.center - self.offset, self.offset, self.player)


            self.player.projectiles.update(self.player.hitbox.center - self.offset, self.offset, self.player)
        elif self.enemy.animation_state == AnimationState.ATTACK:
            self.enemy.projectiles.update(self.enemy.hitbox.center - self.offset, self.offset, self.player)
        elif self.enemy.animation_state == AnimationState.BUFF:
            self.enemy.projectiles.update(self.enemy.hitbox.center - self.offset, self.offset, self.enemy)

    def run(self) -> None:
        """The main loop."""
        self.current_time = pygame.time.get_ticks()
        self.handle_projectiles()
        self.blocking_cooldown()
        self.animations()

        if self.current_time >= self.delay:

            if self.state == BattleState.PLAYER_TURN:
                if self.clock_timer and self.current_time >= self.clock_timer:
                    self.state = BattleState.ENEMY_TURN
                    self.clock_timer = self.current_time + 20000

            elif self.state == BattleState.ENEMY_TURN:
                self.enemy_turn()

            elif self.state == BattleState.END_BATTLE:
                if self.enemy.death: self.enemy.respawn_time = self.current_time + 600000
                self.return_to_overworld = True
                self.player.post_battle_iframes = pygame.time.get_ticks() + 5000

            elif self.state == self.state.END_MENU:
                self.combat_menu.state = CombatMenuState.END_MENU

    def screen_messages(self) -> None:
        """Displays and updates screen messages like damage dealt, recovered, critical hits, etc."""
        self.screen_messages_group.update()
        self.screen_messages_group.draw(self.window)

        for participant in [self.player, self.enemy]:
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

        if self.player.hp != self.player_hp_bar.hp:
            self.player_hp_bar.set_hp(self.player.hp)
        if self.enemy.hp != self.enemy_hp_bar.hp:
            self.enemy_hp_bar.set_hp(self.enemy.hp)
        if self.player.mana != self.player_hp_bar.mana:
            self.player_hp_bar.set_mana(self.player.mana)

        self.enemy_hp_bar.update_hp_bar()
        self.player_hp_bar.update_hp_bar()

        if self.state == BattleState.PLAYER_TURN or self.state == BattleState.END_MENU:
            self.combat_menu.draw(self.window, self.player.mana)

        self.player_hp_bar.draw(self.window)
        self.enemy_hp_bar.draw(self.window)
        self.screen_messages()

    def blocking_cooldown(self) -> None:
        """Handles the player hotkey's and enemy blocking durations."""
        if self.player.blocking and self.current_time >= self.block_cooldown_end:
            self.player.blocking = False

        if self.enemy.blocking:
            if self.current_time >= self.enemy_block_duration: self.enemy.blocking = False
        else:
            self.enemy_block_duration = self.current_time + 500

    def blocking_critical_hotkey(self, event) -> None:
        """The player's block | crit hotkey with its delay."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
            if not self.player.blocking and self.current_time >= self.block_cooldown_end + self.block_delay:
                self.player.blocking = True
                self.block_cooldown_end = self.current_time + self.block_duration  # Next time we can block again

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
        self.enemy.current_attack = random.choice(self.enemy.moves)

        self.handle_attack(self.enemy, self.enemy.current_attack)

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

        # === APPROACH or NONE > [ WAIT ] > ATTACK ===
        elif performer.animation_state == AnimationState.WAIT:
            performer.wait()
            if self.current_time >= self.delay:
                performer.animation_state = AnimationState.ATTACK

        # === WAIT > [ ATTACK ] > RETURN OR IDLE ===
        elif performer.animation_state == AnimationState.ATTACK:
            performer.attack_animation(target, performer.current_attack)
            self.set_delay(1000)

        # === [ BUFF ] > IDLE ====
        elif performer.animation_state == AnimationState.BUFF:
            performer.buff_animation()
            self.set_delay(1000)


        # === ATTACK > [ RETURN ] > IDLE ===
        elif performer.animation_state == AnimationState.RETURN:
            if not target.hp <= 0: target.action = "idle" # change to animation state enemy hurt in entity

            if self.current_time >= self.delay:
                performer.return_animation(performer.battle_pos)

        # === END MENU ===
        elif target.hp <= 0:
            self.state = BattleState.END_MENU

        # RETURN, ATTACK OR BUFF > [ IDLE ] > END TURN
        elif performer.animation_state == AnimationState.IDLE:
            if not target.hp <= 0: target.action = "idle" # change to animation state enemy hurt in entity
            if self.current_time >= self.delay:

                if performer.type == "enemy":
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
            self.animation_phases(self.player, self.enemy)

        elif self.state == BattleState.ENEMY_ANIMATION:
            self.animation_phases(self.enemy, self.player)






