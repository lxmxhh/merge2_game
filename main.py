import sys
import random
import os
import re
import pygame

ROWS = 5
COLS = 5
TILE_SIZE = 70
MARGIN = 12
HEADER = 110

GRID_AREA_W = COLS * TILE_SIZE + (COLS + 1) * MARGIN
GRID_AREA_H = ROWS * TILE_SIZE + (ROWS + 1) * MARGIN
WIDTH = GRID_AREA_W + 2 * MARGIN
HEIGHT = HEADER + GRID_AREA_H + MARGIN
FPS = 60

BG_COLOR = (250, 248, 239)
GRID_BG = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TEXT_COLOR_DARK = (119, 110, 101)
TEXT_COLOR_LIGHT = (249, 246, 242)
SCORE_BG = (143, 122, 102)

LEVEL_NAMES = {
    1: "E1",
    2: "E2",
    3: "E3",
    4: "E4",
    5: "E5",
    6: "E6",
}

TILE_COLORS = {
    1: (238, 228, 218),
    2: (237, 224, 200),
    3: (242, 177, 121),
    4: (245, 149, 99),
    5: (246, 124, 95),
    6: (246, 94, 59),
}

class Game:
    def __init__(self, items_available=None):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.selected = []
        self.items_available = items_available or [1, 2, 3]
        all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
        count = (ROWS * COLS) // 3
        for r, c in random.sample(all_cells, count):
            item = random.choice(self.items_available)
            self.grid[r][c] = (item, 1)

    def empty_cells(self):
        return [(r, c) for r in range(ROWS) for c in range(COLS) if self.grid[r][c] == 0]

    def can_merge(self):
        counts = {}
        for r in range(ROWS):
            for c in range(COLS):
                v = self.grid[r][c]
                if v:
                    key = v if isinstance(v, tuple) else (1, v)
                    counts[key] = counts.get(key, 0) + 1
        return any(cnt >= 2 for cnt in counts.values())

    def merge(self, a, b):
        r1, c1 = a
        r2, c2 = b
        v1 = self.grid[r1][c1]
        v2 = self.grid[r2][c2]
        if isinstance(v1, tuple) and isinstance(v2, tuple):
            item1, lvl1 = v1
            item2, lvl2 = v2
            if item1 == item2 and lvl1 == lvl2:
                new_v = (item2, lvl2 + 1)
                self.grid[r2][c2] = new_v
                self.grid[r1][c1] = 0
                self.score += (lvl2 + 1) * 10
                self.spawn_smart_items(1)
                self.selected = []
                self.game_over = not self.can_merge()
                return True
        return False

    def spawn_smart_items(self, count=1):
        for _ in range(count):
            empties = self.empty_cells()
            if not empties:
                break
            
            # Decide what to spawn
            # If board is almost full or no moves possible, force a matchable item
            # Otherwise, spawn random
            
            # Check if we are in "danger" (low space or no moves)
            is_danger = len(empties) < 5 or not self.can_merge()
            
            spawn_pos = random.choice(empties)
            spawn_val = None
            
            if is_danger:
                # Try to spawn something that matches a neighbor of the spawn_pos
                r, c = spawn_pos
                neighbors = []
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        nv = self.grid[nr][nc]
                        if isinstance(nv, tuple):
                            neighbors.append(nv)
                
                if neighbors:
                    # Pick a neighbor's value to enable a merge
                    spawn_val = random.choice(neighbors)
            
            if spawn_val is None:
                # Random spawn
                # 60% Lv1, 30% Lv2, 10% Lv3
                # Random item type
                item = random.choice(self.items_available)
                roll = random.random()
                if roll < 0.6: lvl = 1
                elif roll < 0.9: lvl = 2
                else: lvl = 3
                spawn_val = (item, lvl)
            
            self.grid[spawn_pos[0]][spawn_pos[1]] = spawn_val

def draw_rect(screen, x, y, w, h, color, radius=8):
    pygame.draw.rect(screen, color, pygame.Rect(x, y, w, h), border_radius=radius)

def draw_text_center(screen, text, font, color, rect):
    surf = font.render(text, True, color)
    r = surf.get_rect(center=rect.center)
    screen.blit(surf, r)

def load_images(size):
    images = {}
    for lv in range(1, 7):
        path = os.path.join("assets", f"lv{lv}.png")
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (size - 8, size - 8))
            images[lv] = img
    return images

def load_lv1_variants(size):
    variants = []
    assets_dir = "assets"
    if os.path.isdir(assets_dir):
        for name in os.listdir(assets_dir):
            lower = name.lower()
            if lower.startswith("lv1") and lower.endswith(".png"):
                path = os.path.join(assets_dir, name)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (size - 8, size - 8))
                    variants.append(img)
                except Exception:
                    pass
    return variants

def load_item_images(size):
    patterns = re.compile(r"^item(\d+)_(\d+)\.png$", re.IGNORECASE)
    items = {}
    if os.path.isdir("assets"):
        for name in os.listdir("assets"):
            m = patterns.match(name)
            if m:
                item_id = int(m.group(1))
                lvl = int(m.group(2))
                path = os.path.join("assets", name)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (size - 8, size - 8))
                    items.setdefault(item_id, {})[lvl] = img
                except Exception:
                    pass
    return items

def cell_at(mx, my):
    grid_x = MARGIN
    grid_y = HEADER
    if mx < grid_x or my < grid_y:
        return None
    rx = mx - grid_x - MARGIN
    ry = my - grid_y - MARGIN
    if rx < 0 or ry < 0:
        return None
    step = TILE_SIZE + MARGIN
    c = rx // step
    r = ry // step
    if r < 0 or c < 0 or r >= ROWS or c >= COLS:
        return None
    if (rx - c * step) >= TILE_SIZE or (ry - r * step) >= TILE_SIZE:
        return None
    return int(r), int(c)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("二合")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("arial", 28, bold=True)
    font_med = pygame.font.SysFont("arial", 22, bold=True)
    font_small = pygame.font.SysFont("arial", 18, bold=True)
    images = load_images(TILE_SIZE)
    item_images = load_item_images(TILE_SIZE)
    items_available = sorted(item_images.keys()) or [1, 2, 3]
    game = Game(items_available=items_available)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game = Game()
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = cell_at(*event.pos)
                if pos is not None:
                    r, c = pos
                    if game.grid[r][c] == 0:
                        pass
                    else:
                        if pos in game.selected:
                            game.selected.remove(pos)
                        else:
                            game.selected.append(pos)
                            if len(game.selected) > 2:
                                game.selected = game.selected[-2:]
                            if len(game.selected) == 2:
                                a, b = game.selected[0], game.selected[1]
                                if not game.merge(a, b):
                                    game.selected = [pos]

        screen.fill(BG_COLOR)
        draw_rect(screen, MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEADER - MARGIN, GRID_BG, radius=12)
        score_rect = pygame.Rect(WIDTH - MARGIN - 160, MARGIN + 16, 144, 64)
        draw_rect(screen, score_rect.x, score_rect.y, score_rect.w, score_rect.h, SCORE_BG, radius=8)
        draw_text_center(screen, str(game.score), font_med, TEXT_COLOR_LIGHT, score_rect)
        tip = "点击两个相同合成升级  R重开"
        tip_surf = font_small.render(tip, True, TEXT_COLOR_LIGHT)
        screen.blit(tip_surf, (MARGIN + 20, MARGIN + 30))

        grid_x = MARGIN
        grid_y = HEADER
        draw_rect(screen, grid_x, grid_y, WIDTH - 2 * MARGIN, HEIGHT - HEADER - MARGIN, GRID_BG, radius=12)

        for r in range(ROWS):
            for c in range(COLS):
                x = grid_x + MARGIN + c * (TILE_SIZE + MARGIN)
                y = grid_y + MARGIN + r * (TILE_SIZE + MARGIN)
                v = game.grid[r][c]
                lvl = v[1] if isinstance(v, tuple) else 0
                color = TILE_COLORS.get(lvl, EMPTY_COLOR) if v else EMPTY_COLOR
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                draw_rect(screen, x, y, TILE_SIZE, TILE_SIZE, color, radius=8)
                if v:
                    if isinstance(v, tuple):
                        item_id, level = v
                        img = item_images.get(item_id, {}).get(level)
                        if img is None:
                            img = images.get(level)
                        if img is not None:
                            ix = x + (TILE_SIZE - img.get_width()) // 2
                            iy = y + (TILE_SIZE - img.get_height()) // 2
                            screen.blit(img, (ix, iy))
                        else:
                            name = LEVEL_NAMES.get(level, f"Lv{level}")
                            color_text = TEXT_COLOR_DARK if level <= 2 else TEXT_COLOR_LIGHT
                            draw_text_center(screen, name, font_med, color_text, rect)
                if (r, c) in game.selected:
                    pygame.draw.rect(screen, (255, 215, 0), rect, width=4, border_radius=8)

        if game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            screen.blit(overlay, (0, 0))
            msg_rect = pygame.Rect(0, 0, WIDTH, 120)
            msg_rect.center = (WIDTH // 2, HEIGHT // 2 - 40)
            draw_text_center(screen, "无可合成，游戏结束", font_big, TEXT_COLOR_DARK, msg_rect)
            tip_rect = pygame.Rect(0, 0, WIDTH, 60)
            tip_rect.center = (WIDTH // 2, HEIGHT // 2 + 20)
            draw_text_center(screen, "按 R 重开", font_med, TEXT_COLOR_DARK, tip_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

