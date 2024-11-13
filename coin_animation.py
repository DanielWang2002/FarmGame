# coin_animation.py

import pygame


class CoinAnimation:
    def __init__(self, x, y, text, font, color, duration=1000):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.duration = duration  # 動畫持續時間（毫秒）
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255  # 透明度

    def update(self):
        # 計算經過的時間
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed < self.duration:
            # 更新位置，例如向上移動
            self.y -= 1  # 每次調用向上移動 1 像素
            # 更新透明度
            self.alpha = int(255 * (1 - elapsed / self.duration))
        else:
            # 動畫結束
            self.alpha = 0

    def draw(self, screen):
        if self.alpha > 0:
            # 繪製文字
            text_surface = self.font.render(self.text, True, self.color)
            # 設置透明度
            text_surface.set_alpha(self.alpha)
            screen.blit(text_surface, (self.x, self.y))
