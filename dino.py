import pygame

from entity import GameEntity
from settings import (
    DINO_DEAD,
    DINO_JUMP,
    DINO_RUN,
    DINO_START,
    GRAVITY,
    GROUND_Y,
    JUMP_VELOCITY,
    load_image,
    load_images,
)


class Dino(GameEntity):
    """Personagem principal controlado pelo jogador.

    Gerencia posição, física de salto e ciclo de animação.
    Não conhece o estado do jogo — apenas o seu próprio estado interno.
    """

    _X: int = 80  # posição horizontal fixa na tela
    _ANIM_SPEED: int = 5  # frames entre trocas de sprite

    def __init__(self) -> None:
        self._run_imgs: list[pygame.Surface] = load_images(DINO_RUN)
        self._jump_img: pygame.Surface = load_image(DINO_JUMP)
        self._dead_img: pygame.Surface = load_image(DINO_DEAD)
        self._start_img: pygame.Surface = load_image(DINO_START)

        # Y estável para sprites de corrida/salto (altura = 94 px)
        self._floor_y: float = float(GROUND_Y - self._run_imgs[0].get_height())

        self._x: float = float(self._X)
        self._y: float = float(GROUND_Y - self._start_img.get_height())
        self._vel_y: float = 0.0
        self._is_jumping: bool = False
        self._is_dead: bool = False
        self._step: int = 0
        self._frame: int = 0
        self._image: pygame.Surface = self._start_img

    # ------------------------------------------------------------------
    # Controles públicos
    # ------------------------------------------------------------------

    def jump(self) -> None:
        """Inicia o salto. Ignorado se já estiver no ar ou morto."""
        if self._is_jumping or self._is_dead:
            return
        self._vel_y = JUMP_VELOCITY
        self._is_jumping = True

    def die(self) -> None:
        """Marca o dino como morto e trava a animação no sprite de morte."""
        self._is_dead = True
        self._image = self._dead_img

    def reset(self) -> None:
        """Restaura o dino ao estado inicial de corrida."""
        self._y = self._floor_y
        self._vel_y = 0.0
        self._is_jumping = False
        self._is_dead = False
        self._step = 0
        self._frame = 0
        self._image = self._run_imgs[0]

    # ------------------------------------------------------------------
    # GameEntity interface
    # ------------------------------------------------------------------

    def update(self, speed: float) -> None:
        if self._is_dead:
            return

        # Física
        self._vel_y += GRAVITY
        self._y += self._vel_y

        # Limite do chão
        if self._y >= self._floor_y:
            self._y = self._floor_y
            self._vel_y = 0.0
            self._is_jumping = False

        # Avança contador de animação
        self._step += 1
        if self._step >= self._ANIM_SPEED:
            self._step = 0
            self._frame = 1 - self._frame

        # Seleciona sprite de acordo com estado (ordem de prioridade)
        if self._is_jumping:
            self._image = self._jump_img
        else:
            self._image = self._run_imgs[self._frame]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, (int(self._x), int(self._y)))

    @property
    def rect(self) -> pygame.Rect:
        r = self._image.get_rect()
        r.topleft = (int(self._x), int(self._y))
        return r
