import random

import pygame

from obstacle import Obstacle
from settings import GROUND_Y, SCREEN_WIDTH, SMALL_CACTUS, load_images


class Cactus(Obstacle):
    """Cacto estático gerado aleatoriamente na entrada da tela.

    As imagens são carregadas uma única vez por sessão (cache de classe)
    para evitar I/O repetido a cada spawn (DRY).
    """

    _cached_images: list[pygame.Surface] | None = None

    @classmethod
    def _get_images(cls) -> list[pygame.Surface]:
        if cls._cached_images is None:
            cls._cached_images = load_images(SMALL_CACTUS)
        return cls._cached_images

    def __init__(self) -> None:
        image = random.choice(self._get_images())
        super().__init__(
            images=[image],
            x=SCREEN_WIDTH + 10,
            y=GROUND_Y - image.get_height(),
        )
