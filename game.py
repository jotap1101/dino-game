import random
import sys
from enum import Enum, auto

import pygame

from cactus import Cactus
from dino import Dino
from obstacle import Obstacle
from scenery import Ground
from settings import (
    BG_COLOR,
    FPS,
    INITIAL_SPEED,
    MAX_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPAWN_INTERVAL_MAX,
    SPAWN_INTERVAL_MIN,
    SPEED_INCREMENT,
)


class GameState(Enum):
    WAITING = auto()
    RUNNING = auto()
    GAME_OVER = auto()


class Game:
    """Orquestrador central do jogo.

    Gerencia o loop principal, a máquina de estados e a detecção de colisão.
    Opera sobre a abstração Obstacle no loop — nunca verifica tipos concretos
    diretamente (DIP / LSP).
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen: pygame.Surface = screen
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._font: pygame.font.Font = pygame.font.Font(None, 28)
        self._state: GameState = GameState.WAITING
        self._speed: float = INITIAL_SPEED
        self._dino: Dino = Dino()
        self._ground: Ground = Ground()
        self._obstacles: list[Obstacle] = []
        self._spawn_timer: int = SPAWN_INTERVAL_MIN

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self) -> None:
        while True:
            self._handle_events()
            if self._state == GameState.RUNNING:
                self._update()
            self._draw()
            self._clock.tick(FPS)

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if self._state == GameState.WAITING:
                        self._state = GameState.RUNNING
                    elif self._state == GameState.RUNNING:
                        self._dino.jump()
                if event.key == pygame.K_SPACE:
                    if self._state == GameState.GAME_OVER:
                        self._reset()

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------

    def _update(self) -> None:
        self._speed = min(self._speed + SPEED_INCREMENT, MAX_SPEED)
        self._dino.update(self._speed)
        self._ground.update(self._speed)
        self._tick_spawn()
        self._update_obstacles()

    def _tick_spawn(self) -> None:
        self._spawn_timer -= 1
        if self._spawn_timer <= 0:
            self._obstacles.append(Cactus())
            self._spawn_timer = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def _update_obstacles(self) -> None:
        for obs in self._obstacles[:]:
            obs.update(self._speed)
            if obs.is_off_screen():
                self._obstacles.remove(obs)
            elif self._check_collision(self._dino, obs):
                self._dino.die()
                self._state = GameState.GAME_OVER

    # ------------------------------------------------------------------
    # Colisão
    # ------------------------------------------------------------------

    def _check_collision(self, dino: Dino, obs: Obstacle) -> bool:
        """Bounding box com margem de tolerância de 4 px em cada lado."""
        dino_rect = dino.rect.inflate(-8, -8)
        return bool(dino_rect.colliderect(obs.rect))

    # ------------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        self._screen.fill(BG_COLOR)
        self._ground.draw(self._screen)
        for obs in self._obstacles:
            obs.draw(self._screen)
        self._dino.draw(self._screen)

        if self._state == GameState.WAITING:
            self._draw_waiting()
        elif self._state == GameState.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_waiting(self) -> None:
        surf = self._font.render("Pressione SETA CIMA para iniciar", True, (83, 83, 83))
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self._screen.blit(surf, rect)

    def _draw_game_over(self) -> None:
        surf = self._font.render(
            "GAME OVER  -  ESPACO para reiniciar", True, (83, 83, 83)
        )
        rect = surf.get_rect(midtop=(SCREEN_WIDTH // 2, 20))
        self._screen.blit(surf, rect)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        self._speed = INITIAL_SPEED
        self._dino.reset()
        self._obstacles.clear()
        self._spawn_timer = SPAWN_INTERVAL_MIN
        self._state = GameState.RUNNING
