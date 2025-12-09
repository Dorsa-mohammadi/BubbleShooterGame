import pygame
import random
import sys
import subprocess
import os

# Pygame'i başlat
pygame.init()

# Ekran boyutları
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Çıkış Ekranı")

# Renkler
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
LIGHT_BLUE = (100, 200, 255)

# Yazı tipi
font = pygame.font.Font(None, 36)

# Balonlar için sınıf
class Balloon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(15, 30)
        self.speed = random.uniform(0.1, 1.2)
        self.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.direction = random.choice([-1, 1])

    def move(self):
        self.y -= self.speed
        self.x += self.direction * random.uniform(0.2, 0.6)
        if self.y < -self.size:
            self.reset()

    def reset(self):
        self.y = height + self.size
        self.x = random.randint(50, width - 50)
        self.size = random.randint(15, 30)
        self.speed = random.uniform(0.1, 1.2)
        self.direction = random.choice([-1, 1])

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# Balonları oluşturma
def create_balloons(count=10):
    return [Balloon(random.randint(50, width - 50), height + random.randint(20, 100)) for _ in range(count)]

# Arka Plan
def draw_background():
    screen.fill((20, 20, 50))

# Butonları çizme
def draw_button(text, x, y, width, height, color, action=None):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]

    # Butonun üzerine gelindiğinde yazı rengi değişir
    if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
        text_surface = font.render(text, True, color)  # Hover rengi
        if mouse_click and action:
            action()  # Tıklama işlemi
        pygame.draw.rect(screen, BLUE, (x, y, width, height), 3)  # çerçeve
    else:
        text_surface = font.render(text, True, WHITE)  # Normal renk
        pygame.draw.rect(screen, BLUE, (x, y, width, height), 3)  # çerçeve

    # Butonun yazısını yerleştir
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

# Çıkış ekranı
def draw_exit_screen(balloons):
    draw_background()
    for balloon in balloons:
        balloon.move()
        balloon.draw()

    # Başlık
    title_text = font.render("Oyun Bitti", True, BLUE)
    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 30))

    # Butonlar
    play_again_rect = pygame.Rect(width // 2 - 150, 150, 300, 50)
    quit_game_rect = pygame.Rect(width // 2 - 150, 230, 300, 50)
    
    # Butonları çiz
    draw_button("Tekrar Oyna", play_again_rect.x, play_again_rect.y, play_again_rect.width, play_again_rect.height, LIGHT_BLUE, start_game)
    draw_button("Çıkış", quit_game_rect.x, quit_game_rect.y, quit_game_rect.width, quit_game_rect.height, LIGHT_BLUE, pygame.quit)

    pygame.display.update()
    return play_again_rect, quit_game_rect

# Oyun başlatma
def start_game():
    if os.path.exists("BubbleShooter.py"):
        subprocess.run([sys.executable, "BubbleShooter.py"])
    else:
        print("BubbleShooter.py dosyası bulunamadı!")

# Çıkış ekranı
def exit_game():
    balloons = create_balloons(10)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_again_rect, quit_game_rect = draw_exit_screen(balloons)
                if play_again_rect.collidepoint(event.pos):
                    start_game()
                    return
                if quit_game_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        draw_exit_screen(balloons)
    pygame.quit()

if __name__ == "__main__":
    exit_game()
