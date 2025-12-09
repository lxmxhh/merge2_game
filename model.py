import random
from config import ROWS, COLS

class GameModel:
    def __init__(self, items_available=None, item_max_levels=None):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.selected = []
        self.items_available = items_available or [1, 2, 3]
        self.item_max_levels = item_max_levels or {}
        self._init_grid()

    def _init_grid(self):
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

    def toggle_select(self, pos):
        r, c = pos
        # 如果点击的是空格，忽略（除非后续有移动逻辑，目前没有）
        if self.grid[r][c] == 0:
            return False

        if pos in self.selected:
            self.selected.remove(pos)
            return False
        else:
            self.selected.append(pos)
            if len(self.selected) > 2:
                self.selected = self.selected[-2:]
            
            if len(self.selected) == 2:
                a, b = self.selected[0], self.selected[1]
                if self.merge(a, b):
                    return True # Merge happened
                else:
                    self.selected = [pos] # Merge failed, select new
            return False

    def merge(self, a, b):
        r1, c1 = a
        r2, c2 = b
        v1 = self.grid[r1][c1]
        v2 = self.grid[r2][c2]
        
        if isinstance(v1, tuple) and isinstance(v2, tuple):
            item1, lvl1 = v1
            item2, lvl2 = v2
            if item1 == item2 and lvl1 == lvl2:
                next_lvl = lvl2 + 1
                max_lvl = self.item_max_levels.get(item2, 6)
                if next_lvl > max_lvl:
                    # 超过该道具最高等级，禁止合成
                    self.selected = [b]
                    return False
                new_v = (item2, next_lvl)
                self.grid[r2][c2] = new_v
                self.grid[r1][c1] = 0
                self.score += next_lvl * 10
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
            
            is_danger = len(empties) < 5 or not self.can_merge()
            
            spawn_pos = random.choice(empties)
            spawn_val = None
            
            if is_danger:
                r, c = spawn_pos
                neighbors = []
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        nv = self.grid[nr][nc]
                        if isinstance(nv, tuple):
                            neighbors.append(nv)
                
                if neighbors:
                    spawn_val = random.choice(neighbors)
            
            if spawn_val is None:
                item = random.choice(self.items_available)
                roll = random.random()
                if roll < 0.6: lvl = 1
                elif roll < 0.9: lvl = 2
                else: lvl = 3
                max_lvl = self.item_max_levels.get(item, 6)
                lvl = min(lvl, max_lvl)
                spawn_val = (item, lvl)
            
            self.grid[spawn_pos[0]][spawn_pos[1]] = spawn_val

    def reset(self):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.selected = []
        self._init_grid()
