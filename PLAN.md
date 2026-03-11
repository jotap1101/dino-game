# Plano de Criação — Réplica do Jogo do Dino

Réplica fiel do jogo offline do Chrome (T-Rex Runner) usando **Python + Pygame**.  
O jogo é construído de forma **incremental**: cada etapa entrega uma versão jogável e funcional, expandindo a anterior.

---

## Princípios de Design

| Princípio | Aplicação |
|---|---|
| **SRP** (Single Responsibility) | Cada classe tem exatamente uma responsabilidade: `Dino` gerencia apenas o dino, `ScoreManager` apenas a pontuação, `ObstacleSpawner` apenas o spawn |
| **OCP** (Open/Closed) | `Obstacle` é aberta para extensão (`Cactus`, `Pterodactyl`) e fechada para modificação |
| **LSP** (Liskov Substitution) | `Cactus` e `Pterodactyl` são substitutos perfeitos de `Obstacle` — `Game` nunca verifica o tipo concreto |
| **ISP** (Interface Segregation) | `GameEntity` define apenas `update` + `draw` + `rect`; entidades estáticas de UI não implementam `update` |
| **DIP** (Dependency Inversion) | `Game` depende da abstração `GameEntity` / `Obstacle`, não das classes concretas |
| **DRY** | Lógica de animação encapsulada em `Obstacle`; carregamento de sprites centralizado em `settings.py` |

---

## Arquitetura Final de Arquivos

```
dino-game/
├── main.py            # Ponto de entrada
├── game.py            # Orquestrador: loop, estados, colisão
├── dino.py            # Classe Dino (movimento, animação, física)
├── entity.py          # ABC GameEntity — interface compartilhada por todos os objetos do jogo  <- NOVO
├── obstacle.py        # ABC Obstacle (herda GameEntity) + lógica comum a todos os obstáculos
├── cactus.py          # Cactus (herda Obstacle)
├── pterodactyl.py     # Pterodactyl (herda Obstacle)
├── scenery.py         # Ground e Cloud (herdam GameEntity)
├── score.py           # ScoreManager — pontuação, high score, flash  <- NOVO
├── spawner.py         # ObstacleSpawner — lógica de spawn desacoplada do Game  <- NOVO
├── settings.py        # Constantes, caminhos de assets, helpers de carregamento
├── requirements.txt   # pygame==2.6.1
└── assets/
    ├── dino/
    ├── obstacles/
    ├── scenery/
    └── elements/
```

---

## Constantes Globais — `settings.py`

### Tela e Loop
| Constante | Valor | Descrição |
|---|---|---|
| `SCREEN_WIDTH` | 1200 | Largura da janela (px) |
| `SCREEN_HEIGHT` | 400 | Altura da janela (px) |
| `FPS` | 60 | Frames por segundo |
| `BG_COLOR` | `(247, 247, 247)` | Cor de fundo (cinza claro) |

### Física
| Constante | Valor | Descrição |
|---|---|---|
| `GROUND_Y` | 330 | Y base do chão — pé do dino em repouso |
| `GRAVITY` | 1.5 | Aceleração gravitacional (px/frame²) |
| `JUMP_VELOCITY` | -22 | Velocidade inicial do salto |

### Velocidade
| Constante | Valor | Descrição |
|---|---|---|
| `INITIAL_SPEED` | 6 | Velocidade inicial (px/frame) |
| `MAX_SPEED` | 20 | Teto da velocidade |
| `SPEED_INCREMENT` | 0.001 | Acréscimo de velocidade por frame |

### Obstáculos
| Constante | Valor | Descrição |
|---|---|---|
| `PTERODACTYL_MIN_SCORE` | 400 | Score mínimo para pterodáctilos surgirem |
| `SPAWN_INTERVAL_MIN` | 60 | Mínimo de frames entre obstáculos |
| `SPAWN_INTERVAL_MAX` | 150 | Máximo de frames entre obstáculos |

### Caminhos dos Assets
```python
ASSETS_DIR     = "assets/"
DINO_RUN       = [ASSETS_DIR + "dino/dino-run-01.png",   ASSETS_DIR + "dino/dino-run-02.png"]
DINO_DUCK      = [ASSETS_DIR + "dino/dino-duck-01.png",  ASSETS_DIR + "dino/dino-duck-02.png"]
DINO_JUMP      = ASSETS_DIR + "dino/dino-jump.png"
DINO_DEAD      = ASSETS_DIR + "dino/dino-dead.png"
DINO_START     = ASSETS_DIR + "dino/dino-start.png"
SMALL_CACTUS   = [ASSETS_DIR + "obstacles/small-cactus-0{}.png".format(i) for i in range(1, 4)]
LARGE_CACTUS   = [ASSETS_DIR + "obstacles/large-cactus-0{}.png".format(i) for i in range(1, 4)]
PTERO_IMGS     = [ASSETS_DIR + "obstacles/pterodactyl-0{}.png".format(i) for i in range(1, 3)]
CLOUD_IMG      = ASSETS_DIR + "scenery/cloud.png"
TRACK_IMG      = ASSETS_DIR + "scenery/track.png"
GAME_OVER_IMG  = ASSETS_DIR + "elements/game-over.png"
RESET_IMG      = ASSETS_DIR + "elements/reset.png"

# Alturas de voo do pterodáctilo (Y absoluto)
PTERO_HEIGHTS  = [GROUND_Y - 50, GROUND_Y - 100, GROUND_Y - 150]
```

### Helper de carregamento (DRY)
```python
def load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()

def load_images(paths: list[str]) -> list[pygame.Surface]:
    return [load_image(p) for p in paths]
```

---

## Interface Base — `entity.py`

ABC que define o contrato de todos os objetos do jogo.  
Garante o **DIP**: `Game` opera sobre `GameEntity`, nunca diretamente sobre tipos concretos.

```python
from abc import ABC, abstractmethod
import pygame

class GameEntity(ABC):

    @abstractmethod
    def update(self, speed: float) -> None:
        """Atualiza estado interno para o próximo frame."""

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Renderiza o objeto na tela."""

    @property
    @abstractmethod
    def rect(self) -> pygame.Rect:
        """Retorna a hitbox atual."""
```

---

## Estados do Jogo

```
WAITING   ->  (SPACE / UP)      ->  RUNNING
RUNNING   ->  (colisão)         ->  GAME_OVER
GAME_OVER ->  (SPACE / ENTER)   ->  RUNNING  (chama reset())
```

Implementados como `enum.Enum` em `game.py`:
```python
from enum import Enum, auto

class GameState(Enum):
    WAITING   = auto()
    RUNNING   = auto()
    GAME_OVER = auto()
```

---

---

# ETAPA 1 — MVP Jogável

> **Meta:** jogo completo e jogável do zero.  
> Dino corre, pula, colide com cactos, game over e reinício funcionam.

### Arquivos desta etapa
`settings.py` · `entity.py` · `dino.py` · `obstacle.py` · `cactus.py` · `scenery.py` (só `Ground`) · `game.py` · `main.py`

---

### `entity.py`
Implementar exatamente como descrito na seção de interface base acima.

---

### `dino.py` — Classe `Dino(GameEntity)`

#### Atributos
| Atributo | Tipo | Descrição |
|---|---|---|
| `_x`, `_y` | `float` | Posição (Y varia durante o salto) |
| `_vel_y` | `float` | Velocidade vertical atual |
| `_is_jumping` | `bool` | True enquanto no ar |
| `_is_dead` | `bool` | True após colisão |
| `_step` | `int` | Contador de frames para troca de sprite |
| `_frame` | `int` | Índice do frame atual (0 ou 1) |
| `_image` | `Surface` | Sprite atual |
| `_rect` | `Rect` | Hitbox relativa à imagem |

> Atributos privados com prefixo `_`; expostos via `@property` quando necessário (encapsulamento).

#### Sprites nesta etapa
| Estado | Imagem(ns) |
|---|---|
| Aguardando | `dino-start.png` |
| Correndo | `dino-run-01.png` <-> `dino-run-02.png` (alterna a cada 5 frames) |
| Saltando | `dino-jump.png` |
| Morto | `dino-dead.png` |

#### Métodos públicos
| Método | Descrição |
|---|---|
| `jump() -> None` | Inicia o salto se `_is_jumping == False` |
| `die() -> None` | Marca `_is_dead = True`, trava animação em `dino-dead.png` |
| `reset() -> None` | Restaura todos os atributos ao estado inicial |
| `update(speed) -> None` | Aplica gravidade; avança animação; limita Y ao chão |
| `draw(screen) -> None` | Renderiza `_image` em `(_x, _y)` |
| `rect -> Rect` | Property: retorna hitbox absoluta |

#### Física do salto
```
_vel_y += GRAVITY          # gravidade acumula a cada frame
_y     += _vel_y           # aplica deslocamento vertical
if _y >= GROUND_Y:
    _y        = GROUND_Y
    _vel_y    = 0
    _is_jumping = False
```

#### Controles (gerenciados pelo `Game`)
| Evento | Chamada |
|---|---|
| `KEYDOWN SPACE / UP` | `dino.jump()` |

---

### `obstacle.py` — Classe `Obstacle(GameEntity)` (ABC)

Contém toda a lógica compartilhada entre obstáculos (DRY + OCP).  
Subclasses só precisam implementar `__init__` e, se houver animação, sobrescrever `update`.

```python
class Obstacle(GameEntity, ABC):
    def __init__(self, images: list[Surface], x: int, y: int) -> None:
        self._images = images
        self._image  = images[0]
        self._x, self._y = x, y
        self._rect = self._image.get_rect()

    def update(self, speed: float) -> None:
        self._x -= speed           # desloca para a esquerda

    def draw(self, screen: Surface) -> None:
        screen.blit(self._image, (self._x, self._y))

    def is_off_screen(self) -> bool:
        return self._x + self._rect.width < 0

    @property
    def rect(self) -> Rect:
        return self._rect.move(int(self._x), int(self._y))
```

---

### `cactus.py` — Classe `Cactus(Obstacle)`

Etapa 1: apenas cactos pequenos. Sem animação — sprite estático.

```python
class Cactus(Obstacle):
    def __init__(self) -> None:
        image = random.choice(load_images(SMALL_CACTUS))
        super().__init__(
            images=[image],
            x=SCREEN_WIDTH + 10,
            y=GROUND_Y - image.get_height()
        )
```

---

### `scenery.py` — Classe `Ground(GameEntity)`

Dois tiles de `track.png` em scroll infinito.  
Quando um tile sai pela esquerda, é reposicionado imediatamente à direita do outro.

```python
class Ground(GameEntity):
    def __init__(self) -> None:
        self._image = load_image(TRACK_IMG)
        w = self._image.get_width()
        self._x1, self._x2 = 0, w
        self._y = GROUND_Y

    def update(self, speed: float) -> None:
        self._x1 -= speed
        self._x2 -= speed
        w = self._image.get_width()
        if self._x1 + w < 0:
            self._x1 = self._x2 + w
        if self._x2 + w < 0:
            self._x2 = self._x1 + w

    def draw(self, screen: Surface) -> None:
        screen.blit(self._image, (self._x1, self._y))
        screen.blit(self._image, (self._x2, self._y))

    @property
    def rect(self) -> Rect:
        return pygame.Rect(0, 0, 0, 0)   # Ground não participa de colisão
```

---

### `game.py` — Classe `Game`

#### Atributos (Etapa 1)
| Atributo | Tipo | Descrição |
|---|---|---|
| `_screen` | `Surface` | Superfície de renderização |
| `_clock` | `Clock` | Controle de FPS |
| `_state` | `GameState` | Estado atual |
| `_speed` | `float` | Velocidade atual do jogo |
| `_dino` | `Dino` | Instância do dinossauro |
| `_obstacles` | `list[Obstacle]` | Obstáculos ativos |
| `_ground` | `Ground` | Instância do chão |
| `_spawn_timer` | `int` | Frames até o próximo obstáculo |

#### Loop principal
```python
def run(self) -> None:
    while True:
        self._handle_events()
        if self._state == GameState.RUNNING:
            self._update()
        self._draw()
        self._clock.tick(FPS)
```

#### `_handle_events()`
```
QUIT                     -> pygame.quit(); sys.exit()
KEYDOWN SPACE / UP:
    WAITING   -> _state = RUNNING
    RUNNING   -> _dino.jump()
    GAME_OVER -> _reset()
```

#### `_update()`
```python
self._speed = min(self._speed + SPEED_INCREMENT, MAX_SPEED)
self._dino.update(self._speed)
self._ground.update(self._speed)

self._spawn_timer -= 1
if self._spawn_timer <= 0:
    self._obstacles.append(Cactus())
    self._spawn_timer = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

for obs in self._obstacles[:]:
    obs.update(self._speed)
    if obs.is_off_screen():
        self._obstacles.remove(obs)
    elif self._check_collision(self._dino, obs):
        self._dino.die()
        self._state = GameState.GAME_OVER
```

#### `_check_collision(dino, obstacle) -> bool`
Etapa 1: bounding box com margem de tolerância de 4 px em cada lado.
```python
dino_rect = dino.rect.inflate(-8, -8)
return dino_rect.colliderect(obstacle.rect)
```

#### `_draw()`
```python
self._screen.fill(BG_COLOR)
self._ground.draw(self._screen)
for obs in self._obstacles:
    obs.draw(self._screen)
self._dino.draw(self._screen)
pygame.display.flip()
```

#### `_reset()`
```python
self._speed = INITIAL_SPEED
self._dino.reset()
self._obstacles.clear()
self._spawn_timer = SPAWN_INTERVAL_MIN
self._state = GameState.RUNNING
```

---

### `main.py`
```python
import pygame, sys
from game import Game
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dino Game")
    Game(screen).run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
```

### Resultado da Etapa 1
- Janela abre com dino parado na tela de espera.
- SPACE inicia: dino corre, chão faz scroll, cactos pequenos surgem.
- SPACE no ar: dino pula sobre cactos.
- Colisão para o jogo (dino com X nos olhos).
- SPACE reinicia o jogo do zero.

---

---

# ETAPA 2 — Dino Completo + Pontuação

> **Meta:** adicionar agachamento, cactos grandes, pontuação crescente com high score e flash de milestone.

### Arquivos modificados / criados
`dino.py` · `cactus.py` · `score.py` (novo) · `game.py`

---

### `dino.py` — Adições de agachamento

#### Novo sprite
| Estado | Imagem(ns) |
|---|---|
| Agachando | `dino-duck-01.png` <-> `dino-duck-02.png` (alterna a cada 5 frames) |

#### Novo atributo: `_is_ducking: bool`

#### Novos métodos
| Método | Descrição |
|---|---|
| `start_duck() -> None` | Ativa agachamento se `_is_jumping == False` |
| `stop_duck() -> None` | Desativa agachamento |

> O sprite muda para 60 px de altura — `_rect` deve ser recalculado no momento da troca para evitar hitbox incorreta.

Ordem de prioridade ao selecionar sprite:
```
_is_dead     -> dino-dead.png
_is_jumping  -> dino-jump.png
_is_ducking  -> dino-duck-[frame].png
else         -> dino-run-[frame].png
```

#### Controles adicionados no `Game`
| Evento | Chamada |
|---|---|
| `KEYDOWN DOWN` | `dino.start_duck()` |
| `KEYUP DOWN` | `dino.stop_duck()` |

---

### `cactus.py` — Cactos grandes adicionados

Sorteia entre todos os 6 sprites (3 pequenos + 3 grandes):
```python
_ALL_CACTUS = load_images(SMALL_CACTUS + LARGE_CACTUS)  # carregado uma vez na classe

class Cactus(Obstacle):
    def __init__(self) -> None:
        image = random.choice(self._ALL_CACTUS)
        super().__init__(
            images=[image],
            x=SCREEN_WIDTH + 10,
            y=GROUND_Y - image.get_height()
        )
```

---

### `score.py` — Classe `ScoreManager`

Responsabilidade única: toda a lógica de pontuação (SRP).

```python
class ScoreManager:
    _DISPLAY_DIVISOR = 5      # score_raw // 5 = pontos exibidos
    _MILESTONE       = 100    # pisca a cada 100 pontos exibidos
    _FLASH_DURATION  = 30     # frames de flash

    def __init__(self, font: pygame.font.Font) -> None:
        self._raw         = 0
        self._high        = 0
        self._flash_timer = 0
        self._font        = font

    def update(self) -> None:
        prev = self.display
        self._raw += 1
        if self._flash_timer > 0:
            self._flash_timer -= 1
        if self.display % self._MILESTONE == 0 and self.display > prev:
            self._flash_timer = self._FLASH_DURATION

    def draw(self, screen: pygame.Surface) -> None:
        if self._flash_timer > 0:
            return                  # não renderiza durante o flash
        text = f"HI {self._high:05}  {self.display:05}"
        surf = self._font.render(text, True, (83, 83, 83))
        screen.blit(surf, (SCREEN_WIDTH - surf.get_width() - 20, 20))

    def reset(self) -> None:
        self._high = max(self._high, self.display)
        self._raw  = 0

    @property
    def display(self) -> int:
        return self._raw // self._DISPLAY_DIVISOR

    @property
    def raw(self) -> int:
        return self._raw
```

---

### `game.py` — Integrações da Etapa 2

1. Instanciar `ScoreManager` em `__init__`.
2. Em `_update()`: `self._score.update()` quando `RUNNING`.
3. Em `_draw()`: `self._score.draw(self._screen)`.
4. Em `_reset()`: `self._score.reset()`.
5. Adicionar eventos `KEYDOWN K_DOWN` / `KEYUP K_DOWN`.

### Resultado da Etapa 2
- Dino agacha ao pressionar seta baixo (bloqueado no ar).
- Cactos grandes surgem junto com os pequenos (6 variações).
- Pontuação exibida no canto superior direito: `HI 00000  00000`.
- High score mantido entre runs.
- Score desaparece brevemente a cada 100 pontos.

---

---

# ETAPA 3 — Cenário Completo e UI de Game Over

> **Meta:** nuvens com parallax, tela de Game Over com imagens oficiais e hint na tela inicial.

### Arquivos modificados
`scenery.py` · `game.py`

---

### `scenery.py` — Classe `Cloud(GameEntity)`

| Atributo | Valor / Descrição |
|---|---|
| `_x` | `SCREEN_WIDTH + random(0, 300)` |
| `_y` | `random(100, 220)` px |
| `_SPEED_FACTOR` | `0.3` — parallax mais lento que o chão |

```python
class Cloud(GameEntity):
    _Y_MIN        = 100
    _Y_MAX        = 220
    _SPEED_FACTOR = 0.3

    def __init__(self) -> None:
        self._x     = SCREEN_WIDTH + random.randint(0, 300)
        self._y     = random.randint(self._Y_MIN, self._Y_MAX)
        self._image = load_image(CLOUD_IMG)

    def update(self, speed: float) -> None:
        self._x -= speed * self._SPEED_FACTOR

    def is_off_screen(self) -> bool:
        return self._x + self._image.get_width() < 0

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._image, (self._x, self._y))

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, 0, 0)    # Cloud não colide
```

#### Gerenciamento de nuvens no `Game`
```python
_MAX_CLOUDS = 3

# em _update():
if len(self._clouds) < self._MAX_CLOUDS and random.randint(0, 200) == 0:
    self._clouds.append(Cloud())
self._clouds = [c for c in self._clouds if not c.is_off_screen()]
for cloud in self._clouds:
    cloud.update(self._speed)
```

---

### UI de Game Over no `game.py`

Carregado no `__init__`:
```python
self._game_over_img = load_image(GAME_OVER_IMG)
self._reset_img     = load_image(RESET_IMG)
```

Método privado adicionado:
```python
def _draw_game_over(self) -> None:
    cx = SCREEN_WIDTH  // 2
    cy = SCREEN_HEIGHT // 2
    go_rect    = self._game_over_img.get_rect(center=(cx, cy - 30))
    reset_rect = self._reset_img.get_rect(center=(cx, cy + 30))
    self._screen.blit(self._game_over_img, go_rect)
    self._screen.blit(self._reset_img,     reset_rect)
```

### Hint na tela de espera
```python
def _draw_waiting(self) -> None:
    font = pygame.font.Font(None, 28)
    surf = font.render("Pressione ESPACO para iniciar", True, (83, 83, 83))
    rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    self._screen.blit(surf, rect)
```

Em `_draw()`:
```python
if self._state == GameState.WAITING:
    self._draw_waiting()
if self._state == GameState.GAME_OVER:
    self._draw_game_over()
```

### Resultado da Etapa 3
- Nuvens flutuam a velocidade menor que o chão (efeito de profundidade).
- Game Over exibe banner `game-over.png` + ícone `reset.png` centralizados.
- Tela inicial exibe instrução de início.

---

---

# ETAPA 4 — Pterodáctilo e `ObstacleSpawner`

> **Meta:** introduzir o pterodáctilo como obstáculo aéreo e desacoplar a lógica de spawn do `Game`.

### Arquivos criados / modificados
`pterodactyl.py` · `spawner.py` (novo) · `game.py`

---

### `pterodactyl.py` — Classe `Pterodactyl(Obstacle)`

#### Alturas de voo (3 níveis — definidas em `settings.py` como `PTERO_HEIGHTS`)
| Nível | Y absoluto | Estratégia do jogador |
|---|---|---|
| Baixo | `GROUND_Y - 50` | Saltar por cima |
| Médio | `GROUND_Y - 100` | Saltar ou agachar (ambos funcionam) |
| Alto | `GROUND_Y - 150` | Agachar (passa por baixo se agachado) |

#### Animação de 2 frames
```python
class Pterodactyl(Obstacle):
    _ANIM_INTERVAL = 10   # frames entre trocas de sprite

    def __init__(self) -> None:
        images = load_images(PTERO_IMGS)
        y = random.choice(PTERO_HEIGHTS)
        super().__init__(images=images, x=SCREEN_WIDTH + 10, y=y)
        self._anim_counter = 0
        self._frame        = 0

    def update(self, speed: float) -> None:
        super().update(speed)                  # move x -= speed
        self._anim_counter += 1
        if self._anim_counter >= self._ANIM_INTERVAL:
            self._frame  = 1 - self._frame
            self._image  = self._images[self._frame]
            self._anim_counter = 0
```

---

### `spawner.py` — Classe `ObstacleSpawner`

**SRP**: toda a lógica de "quando e o que spawnar" fica aqui, isolada do `Game`.

```python
class ObstacleSpawner:
    def __init__(self) -> None:
        self._timer   = SPAWN_INTERVAL_MIN
        self._pending: list[Obstacle] = []

    def update(self, score: int) -> None:
        self._timer -= 1
        if self._timer <= 0:
            self._pending.append(self._create(score))
            self._timer = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def _create(self, score: int) -> Obstacle:
        can_ptero = score >= PTERODACTYL_MIN_SCORE
        if can_ptero and random.random() < 0.4:
            return Pterodactyl()
        return Cactus()

    def pop_ready(self) -> list[Obstacle]:
        """Retorna e limpa a fila de obstáculos prontos para entrar em jogo."""
        ready, self._pending = self._pending, []
        return ready

    def reset(self) -> None:
        self._timer = SPAWN_INTERVAL_MIN
        self._pending.clear()
```

#### Integração no `game.py` (substitui o spawn inline das etapas anteriores)
```python
# __init__
self._spawner = ObstacleSpawner()

# _update()
self._spawner.update(self._score.display)
self._obstacles.extend(self._spawner.pop_ready())

# _reset()
self._spawner.reset()
```

### Resultado da Etapa 4
- Pterodáctilos surgem após 400 pontos, em 3 alturas diferentes.
- Agachar permite passar por baixo dos altos.
- Toda a lógica de spawn está isolada em `ObstacleSpawner`.

---

---

# ETAPA 5 — Colisão Pixel-Perfect e Polimento Final

> **Meta:** substituir colisão por bounding box por máscara de pixel, ajustar hitboxes e adicionar modo noturno.

### Arquivos modificados
`game.py` · `dino.py` · `obstacle.py`

---

### Colisão por Máscara de Pixel

Adicionar `mask` property em `Dino` e `Obstacle`:
```python
@property
def mask(self) -> pygame.Mask:
    return pygame.mask.from_surface(self._image)
```

Substituir `_check_collision` no `game.py`:
```python
def _check_collision(self, dino: Dino, obs: Obstacle) -> bool:
    # 1ª passagem rápida: bounding box com margem (barato)
    dino_rect = dino.rect.inflate(-8, -8)
    if not dino_rect.colliderect(obs.rect):
        return False
    # 2ª passagem precisa: máscara de pixel (só se BB colidir)
    offset = (obs.rect.x - dino_rect.x, obs.rect.y - dino_rect.y)
    return bool(dino.mask.overlap(obs.mask, offset))
```

---

### Modo Noturno

O jogo original inverte as cores (fundo escuro, sprites claros) a cada ~700 pontos.

Em `settings.py`:
```python
BG_COLOR_DAY   = (247, 247, 247)
BG_COLOR_NIGHT = (35,  35,  35)
NIGHT_INTERVAL = 700
```

Em `game.py`:
```python
# __init__
self._night_mode = False

# _update()
if self._score.display > 0 and self._score.display % NIGHT_INTERVAL == 0:
    self._night_mode = not self._night_mode

# _draw()
bg = BG_COLOR_NIGHT if self._night_mode else BG_COLOR_DAY
self._screen.fill(bg)

# _reset()
self._night_mode = False
```

---

### Resumo das Etapas

| Etapa | Funcionalidade adicionada | Jogável? |
|---|---|---|
| **1** | Dino corre e pula · Cactos pequenos · Scroll do chão · Colisão básica · Game Over / Restart | Sim |
| **2** | Agachamento · Cactos grandes · Pontuação + High Score · Flash de milestone | Sim |
| **3** | Nuvens com parallax · UI de Game Over (imagens) · Hint na tela inicial | Sim |
| **4** | Pterodáctilo (3 alturas, animado) · `ObstacleSpawner` desacoplado | Sim |
| **5** | Colisão pixel-perfect · Hitboxes ajustadas · Modo noturno | Sim |

---

## Fidelidade ao Jogo Original

| Comportamento do original | Implementação |
|---|---|
| Velocidade crescente até o teto | `speed = min(speed + SPEED_INCREMENT, MAX_SPEED)` a cada frame |
| Pterodáctilo apenas em pontuações altas | `ObstacleSpawner._create()` bloqueia até `score >= 400` |
| Scroll do chão sem emenda visível | Dois tiles de `track.png` reposicionados em loop |
| Nuvens mais lentas que o chão | Fator `0.3` aplicado na velocidade de `Cloud` |
| Colisão "perdoável" | `inflate(-8, -8)` + máscara de pixel (Etapa 5) |
| High score persiste durante a sessão | `ScoreManager._high` nunca zerado no `reset()` |
| Score pisca ao atingir 100 pts | `_flash_timer` em `ScoreManager` |
| Agachamento bloqueado no ar | `start_duck()` retorna se `_is_jumping == True` |
| 3 alturas de voo do pterodáctilo | Constante `PTERO_HEIGHTS` com 3 valores em `settings.py` |
| Modo noturno invertido | Alternância de paleta a cada 700 pts (Etapa 5) |
