import pygame
import os
import re
from config import *

class GameView:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("二合")
        
        self.font_big = pygame.font.SysFont("microsoftyahei", 28, bold=True)
        self.font_med = pygame.font.SysFont("microsoftyahei", 22, bold=True)
        self.font_small = pygame.font.SysFont("microsoftyahei", 18, bold=True)
        
        self.images = self.load_images(TILE_SIZE)
        self.item_images = self.load_item_images(TILE_SIZE)

    def load_images(self, size):
        images = {}
        for lv in range(1, 7):
            path = os.path.join("assets", f"lv{lv}.png")
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (size - 8, size - 8))
                images[lv] = img
        return images

    def load_item_images(self, size):
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

    def get_available_items(self):
        return sorted(self.item_images.keys())

    def draw_rect(self, x, y, w, h, color, radius=8):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, w, h), border_radius=radius)

    def draw_text_center(self, text, font, color, rect):
        surf = font.render(text, True, color)
        r = surf.get_rect(center=rect.center)
        self.screen.blit(surf, r)

    def draw(self, model):
        self.screen.fill(BG_COLOR)
        
        # Header Area
        self.draw_rect(MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEADER - MARGIN, GRID_BG, radius=12)
        score_rect = pygame.Rect(WIDTH - MARGIN - 160, MARGIN + 16, 144, 64)
        self.draw_rect(score_rect.x, score_rect.y, score_rect.w, score_rect.h, SCORE_BG, radius=8)
        self.draw_text_center(str(model.score), self.font_med, TEXT_COLOR_LIGHT, score_rect)
        
        tip = "点击两个相同合成升级  按R重开"
        tip_surf = self.font_small.render(tip, True, TEXT_COLOR_LIGHT)
        self.screen.blit(tip_surf, (MARGIN + 20, MARGIN + 30))

        # Grid Area
        grid_x = MARGIN
        grid_y = HEADER
        self.draw_rect(grid_x, grid_y, WIDTH - 2 * MARGIN, HEIGHT - HEADER - MARGIN, GRID_BG, radius=12)

        for r in range(ROWS):
            for c in range(COLS):
                x = grid_x + MARGIN + c * (TILE_SIZE + MARGIN)
                y = grid_y + MARGIN + r * (TILE_SIZE + MARGIN)
                
                v = model.grid[r][c]
                lvl = v[1] if isinstance(v, tuple) else 0
                color = TILE_COLORS.get(lvl, EMPTY_COLOR) if v else EMPTY_COLOR
                
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.draw_rect(x, y, TILE_SIZE, TILE_SIZE, color, radius=8)
                
                if v:
                    if isinstance(v, tuple):
                        item_id, level = v
                        # Try item specific image -> level generic image -> text
                        img = self.item_images.get(item_id, {}).get(level)
                        if img is None:
                            img = self.images.get(level)
                        
                        if img is not None:
                            ix = x + (TILE_SIZE - img.get_width()) // 2
                            iy = y + (TILE_SIZE - img.get_height()) // 2
                            self.screen.blit(img, (ix, iy))
                        else:
                            name = LEVEL_NAMES.get(level, f"Lv{level}")
                            color_text = TEXT_COLOR_DARK if level <= 2 else TEXT_COLOR_LIGHT
                            self.draw_text_center(name, self.font_med, color_text, rect)
                
                if (r, c) in model.selected:
                    pygame.draw.rect(self.screen, SELECTED_BORDER_COLOR, rect, width=4, border_radius=8)

        # Game Over Overlay
        if model.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(OVERLAY_COLOR)
            self.screen.blit(overlay, (0, 0))
            
            msg_rect = pygame.Rect(0, 0, WIDTH, 120)
            msg_rect.center = (WIDTH // 2, HEIGHT // 2 - 40)
            self.draw_text_center("无可合成，游戏结束", self.font_big, TEXT_COLOR_DARK, msg_rect)
            
            tip_rect = pygame.Rect(0, 0, WIDTH, 60)
            tip_rect.center = (WIDTH // 2, HEIGHT // 2 + 20)
            self.draw_text_center("按 R 重开", self.font_med, TEXT_COLOR_DARK, tip_rect)

        pygame.display.flip()

    def cell_at(self, mx, my):
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
