from classes.level import Level
from classes.mouse import Mouse
from classes.states import BattleState
from other.settings import *

class Game:
    def __init__(self):
        """General setup"""
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.mouse = Mouse()
        pygame.mouse.set_visible(False)

    def run(self) -> None:
        """Run the game."""
        while True:
            self.display_surface.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


                if not self.level.visible_sprites.battle_loop:
                    self.level.menu.keybinds(event)
                    self.level.overworld_ui.hotkeys(event)
                else:
                    self.level.visible_sprites.battle_loop.selecting_target_hotkeys(event)

                    if (self.level.visible_sprites.battle_loop.state in [BattleState.PLAYER_ANIMATION, BattleState.ENEMY_ANIMATION]
                            and self.level.player in [self.level.visible_sprites.battle_loop.target, self.level.visible_sprites.battle_loop.performer]):

                        self.level.player.blocking_critical_hotkey(event)
                    self.level.visible_sprites.battle_loop.battle_menu.hotkeys(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    if not self.level.player.status_bar.visible:
                        for ally in self.level.player.active_allies:
                            ally.status_bar.visible = True

                        self.level.player.status_bar.visible = True
                    else:

                        for ally in self.level.player.active_allies:
                            ally.status_bar.visible = False
                        self.level.player.status_bar.visible = False


            delta_time = self.clock.tick(FPS)

            self.level.player.get_dt(delta_time)
            for npc in self.level.visible_sprites.npc_sprites:
                npc.get_dt(delta_time)

            self.level.run()

            self.mouse.draw(self.display_surface)

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()