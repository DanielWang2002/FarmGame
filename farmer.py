# farmer.py

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT


class Farmer:
    def __init__(self):
        # 農夫精靈圖
        self.spritesheet = pygame.image.load("./img/Farmer/Walk-Sheet.png")
        self.frame_width = 21
        self.frame_height = 17
        self.rows = 4
        self.cols = 8
        self.scale_factor = 10
        self.frames = self.load_frames()
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed = 5
        self.direction = 0
        self.current_frame = 0
        self.frame_delay = 10
        self.frame_counter = 0
        self.image_width = self.frame_width * self.scale_factor
        self.image_height = self.frame_height * self.scale_factor

    def load_frames(self):
        frames = []
        for row in range(self.rows):
            row_frames = []
            for col in range(self.cols):
                frame_rect = pygame.Rect(
                    col * self.frame_width,
                    row * self.frame_height,
                    self.frame_width,
                    self.frame_height,
                )
                frame_image = self.spritesheet.subsurface(frame_rect)
                frame_image = pygame.transform.scale(
                    frame_image,
                    (
                        self.frame_width * self.scale_factor,
                        self.frame_height * self.scale_factor,
                    ),
                )
                row_frames.append(frame_image)
            frames.append(row_frames)
        return frames

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = 1
        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = 2
        elif keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = 3
        elif keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = 0

        # 更新動畫幀
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % self.cols
            self.frame_counter = 0

    def draw(self, screen):
        screen.blit(self.frames[self.direction][self.current_frame], (self.x, self.y))
