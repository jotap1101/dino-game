import pygame

from entity import GameEntity
from settings import GROUND_Y, TRACK_IMG, load_image


class Ground(GameEntity):
    """Faixa do chão com scroll infinito.

    Dois tiles de track.png posicionados lado a lado. Quando um tile sai
    pela borda esquerda, é reposicionado imediatamente à direita do outro,
    criando um loop contínuo sem emenda visível.
    """

    def __init__(self) -> None:
        self._image: pygame.Surface = load_image(TRACK_IMG)
        w = self._image.get_width()
        self._x1: float = 0.0
        self._x2: float = float(w)
        self._y: int = GROUND_Y

    def update(self, speed: float) -> None:
        self._x1 -= speed
        self._x2 -= speed
        w = self._image.get_width()
        if self._x1 + w < 0:
            self._x1 = self._x2 + w
        if self._x2 + w < 0:
            self._x2 = self._x1 + w

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, (int(self._x1), self._y))
        screen.blit(self._image, (int(self._x2), self._y))

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, 0, 0)  # Ground não participa de colisão
