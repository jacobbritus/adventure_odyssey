import pygame
from classes.UI import Hpbar, Button


# Add options like Defend, Use Item, etc.
# Add animations or sounds during attacks.
# Display a battle menu.
# Let the player choose a target if multiple enemies exist.

class BattleLoop:
    def __init__(self, player, enemy, window):
        self.player = player
        self.player_position = (player.x - self.player.width, player.y)
        self.enemy = enemy
        self.enemy_position = (enemy.x, enemy.y)
        self.window = window

        self.turn = "player"

        self.end_battle = False
        self.return_to_overworld = False

        self.player_hp_bar = Hpbar((125, 187), self.player.hp, self.player.max_hp)
        self.player_hp_bar.set_hp(self.player.hp)
        self.enemy_hp_bar = Hpbar((450, 187), self.enemy.hp, self.enemy.hp)

        self.buttons_group = pygame.sprite.Group()

        self.delay = False
        self.delay_time = 0

        self.state = None


    def delay_now(self):
        self.delay_time += 0.1

        if self.delay_time > 5:
            self.delay_time = 0
            self.delay = False


    def update(self):
        if self.delay: self.delay_now()

        self.animation()



        self.draw_ui(self.window)


        if not self.player.close_distance and not self.enemy.close_distance:
            self.player_hp_bar.update()
            self.enemy_hp_bar.update()

        if self.state == "animation":
            return


        if self.end_battle and not self.delay:
            self.return_to_overworld = True

        if self.end_battle:
            return

        if self.turn == "player":
            pass

        elif self.turn == "enemy":
            if not self.delay:
                self.enemy_turn()
                self.turn = "player"

    def draw_ui(self, window):
        self.player_hp_bar.draw(window)
        self.enemy_hp_bar.draw(window)

        if self.buttons_group and not self.state == "animation":
            for button in self.buttons_group:
                button.draw(window)
                button.update()
                if button.delete:
                    for buttons in self.buttons_group:
                        buttons.kill()


    def handle_input(self):
        if self.turn == "player" and not self.buttons_group and not self.end_battle:
            Button(self.buttons_group, (self.window.get_width() // 2, self.window.get_height() // 2), self.player_attack, "Attack")
            Button(self.buttons_group, (self.window.get_width() // 2, self.window.get_height() // 2 + 32), self.player_run, "Run")

    def player_run(self):
        self.delay = True
        self.end_battle = True


    def player_attack(self):
        self.player.close_distance = True
        self.enemy.hp -= self.player.dmg
        if self.enemy.hp <= 0:
            self.end_battle = True

        self.enemy_hp_bar.set_hp(self.enemy.hp)
        self.delay = True

        self.turn = "enemy"


    def animation(self):
        if self.player.close_distance:
            self.state = "animation"
            self.player.move_to(self.enemy)
        elif self.player.attacking:
            self.state = "animation"
            self.player.attack()

        elif self.player.move_back:
            self.state = "animation"
            self.player.go_back(self.player_position)

        elif self.enemy.close_distance:
            self.state = "animation"
            self.enemy.move_to(self.player)

        elif self.enemy.move_back:
            self.state = "animation"
            self.enemy.go_back(self.enemy_position)

        elif self.enemy.attacking:
            self.state = "animation"
            self.enemy.attack()

        else:
            self.state = "ok"


    def enemy_turn(self):
        self.enemy.close_distance = True

        self.player.hp -= self.enemy.dmg

        if self.player.hp <= 0:
            self.end_battle = True

        self.player_hp_bar.set_hp(self.player.hp)
        self.delay = True


