import sys
import pygame
from model import GameModel
from view import GameView
from config import FPS

class GameController:
    def __init__(self):
        self.view = GameView()
        # Initialize model with items found by view
        items = self.view.get_available_items()
        self.model = GameModel(items_available=items)
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.view.draw(self.model)
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.model.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = self.view.cell_at(*event.pos)
                if pos is not None:
                    self.model.toggle_select(pos)
