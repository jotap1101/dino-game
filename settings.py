import pygame

# ---------------------------------------------------------------------------
# Screen & Loop
# ---------------------------------------------------------------------------
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60
BG_COLOR: tuple[int, int, int] = (247, 247, 247)

# ---------------------------------------------------------------------------
# Physics
# ---------------------------------------------------------------------------
GROUND_Y: int = 330  # Y absoluto do pé do dino em repouso
GRAVITY: float = 1.5  # px / frame²
JUMP_VELOCITY: float = -22.0  # px / frame (negativo = para cima)

# ---------------------------------------------------------------------------
# Speed
# ---------------------------------------------------------------------------
INITIAL_SPEED: float = 6.0
MAX_SPEED: float = 20.0
SPEED_INCREMENT: float = 0.001  # acréscimo por frame

# ---------------------------------------------------------------------------
# Obstacles & Spawn
# ---------------------------------------------------------------------------
PTERODACTYL_MIN_SCORE: int = 400
SPAWN_INTERVAL_MIN: int = 60  # frames
SPAWN_INTERVAL_MAX: int = 150  # frames

# ---------------------------------------------------------------------------
# Asset paths
# ---------------------------------------------------------------------------
_A = "assets/"

DINO_RUN: list[str] = [
    _A + "dino/dino-run-01.png",
    _A + "dino/dino-run-02.png",
]
DINO_DUCK: list[str] = [
    _A + "dino/dino-duck-01.png",
    _A + "dino/dino-duck-02.png",
]
DINO_JUMP: str = _A + "dino/dino-jump.png"
DINO_DEAD: str = _A + "dino/dino-dead.png"
DINO_START: str = _A + "dino/dino-start.png"

SMALL_CACTUS: list[str] = [_A + f"obstacles/small-cactus-0{i}.png" for i in range(1, 4)]
LARGE_CACTUS: list[str] = [_A + f"obstacles/large-cactus-0{i}.png" for i in range(1, 4)]
PTERO_IMGS: list[str] = [_A + f"obstacles/pterodactyl-0{i}.png" for i in range(1, 3)]

CLOUD_IMG: str = _A + "scenery/cloud.png"
TRACK_IMG: str = _A + "scenery/track.png"
GAME_OVER_IMG: str = _A + "elements/game-over.png"
RESET_IMG: str = _A + "elements/reset.png"

PTERO_HEIGHTS: list[int] = [GROUND_Y - 50, GROUND_Y - 100, GROUND_Y - 150]

# ---------------------------------------------------------------------------
# Helpers de carregamento (DRY — ponto único de I/O de sprites)
# ---------------------------------------------------------------------------


def load_image(path: str) -> pygame.Surface:
    """Carrega uma imagem e converte para o formato de exibição com alpha."""
    return pygame.image.load(path).convert_alpha()


def load_images(paths: list[str]) -> list[pygame.Surface]:
    """Carrega uma lista de imagens em ordem."""
    return [load_image(p) for p in paths]
