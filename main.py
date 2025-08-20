from classes.level import Level
from other.settings import *

class Game:
    def __init__(self):
        """General setup"""
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self) -> None:
        """Run the game."""
        while True:
            self.window.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


                if not self.level.visible_sprites.battle_loop:
                    self.level.menu.keybinds(event)
                    self.level.overworld_ui.hotkeys(event)

                if self.level.player.in_battle:
                    self.level.player.blocking_critical_hotkey(event)


                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    if not self.level.player.hp_bar.visible:
                        for ally in self.level.player.active_allies:
                            ally.hp_bar.visible = True

                        self.level.player.hp_bar.visible = True
                    else:

                        for ally in self.level.player.active_allies:
                            ally.hp_bar.visible = False
                        self.level.player.hp_bar.visible = False


            delta_time = self.clock.tick(FPS)

            self.level.player.get_dt(delta_time)
            for npc in self.level.visible_sprites.npc_sprites:
                npc.get_dt(delta_time)

            self.level.run()

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()