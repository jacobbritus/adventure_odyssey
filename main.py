import pygame

from classes.level import Level
from other.settings import *


class Game:
    def __init__(self):
        """General setup"""
        pygame.init()
        pygame.mixer.init()
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

            self.level.run()

            self.clock.tick(FPS)
            pygame.display.update()



if __name__ == "__main__":
    game = Game()
    game.run()