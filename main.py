from classes.UI import MenuBook
from classes.level import Level
from classes.states import BookState
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

                if self.level.visible_sprites.battle_loop:
                    self.level.visible_sprites.battle_loop.blocking_critical_hotkey(event)


            delta_time = self.clock.tick(FPS)

            self.level.player.get_dt(delta_time)
            for enemy in self.level.visible_sprites.enemy_sprites:
                enemy.get_dt(delta_time)

            self.level.run()

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()