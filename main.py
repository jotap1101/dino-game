import sys

import pygame

from game import Game
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dino Game")
    Game(screen).run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
