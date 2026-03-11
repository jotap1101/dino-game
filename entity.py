from abc import ABC, abstractmethod

import pygame


class GameEntity(ABC):
    """Interface base de todos os objetos do jogo.

    Define o contrato mínimo que qualquer entidade deve cumprir,
    permitindo que Game opere sobre abstrações em vez de tipos concretos (DIP).
    """

    @abstractmethod
    def update(self, speed: float) -> None:
        """Atualiza o estado interno para o próximo frame."""

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Renderiza o objeto na superfície recebida."""

    @property
    @abstractmethod
    def rect(self) -> pygame.Rect:
        """Hitbox atual em coordenadas absolutas da tela."""
