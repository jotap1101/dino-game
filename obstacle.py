import pygame

from entity import GameEntity


class Obstacle(GameEntity):
    """Classe base para todos os obstáculos do jogo.

    Encapsula a movimentação horizontal e a detecção de saída de tela (DRY).
    Subclasses definem apenas __init__; se precisarem de animação, sobrescrevem
    update() sem duplicar a lógica de movimento (OCP).

    Pode ser substituída por qualquer subclasse sem que Game precise saber
    qual tipo concreto está em uso (LSP).
    """

    def __init__(
        self,
        images: list[pygame.Surface],
        x: int,
        y: int,
    ) -> None:
        self._images: list[pygame.Surface] = images
        self._image: pygame.Surface = images[0]
        self._x: float = float(x)
        self._y: int = y
        self._rect: pygame.Rect = self._image.get_rect()

    # ------------------------------------------------------------------
    # GameEntity interface
    # ------------------------------------------------------------------

    def update(self, speed: float) -> None:
        """Desloca o obstáculo para a esquerda. Subclasses chamam super() e
        adicionam lógica de animação depois."""
        self._x -= speed

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, (int(self._x), self._y))

    @property
    def rect(self) -> pygame.Rect:
        return self._rect.move(int(self._x), self._y)

    # ------------------------------------------------------------------
    # Extra
    # ------------------------------------------------------------------

    def is_off_screen(self) -> bool:
        """True quando o obstáculo saiu completamente pela borda esquerda."""
        return self._x + self._rect.width < 0
