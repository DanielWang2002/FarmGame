# plant.py

import pygame


class Plant:
    def __init__(self, image_path, scale=(64, 64)):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)
