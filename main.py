import pygame
import random
import math
import json
import time  # Import time for delay

# Initialize pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("UFO.png")
pygame.display.set_icon(icon)

# Load images
game_over_img = pygame.image.load("game_over.png")
replay_img = pygame.image.load("replay.png")
background_img = pygame.image.load("background.png")
player_img = pygame.image.load("enemy.png")
enemy_img = pygame.image.load("UFO.png")
bullet_img = pygame.image.load("bullet.png")
enemy_bullet_img = pygame.image.load("bullet.png")
explosion_img = pygame.image.load("explosion.png")  # Load explosion image

# Load sounds
game_over_sound = pygame.mixer.Sound("game_over.mp3")
bullet_sound = pygame.mixer.Sound("bullet_sounds.mp3")
explosion_sound = pygame.mixer.Sound("explosion.mp3")  # Load explosion sound
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Font setup
font = pygame.font.Font('freesansbold.ttf', 24)
small_font = pygame.font.Font('freesansbold.ttf', 18)

# Game states
MAIN_MENU = "main_menu"
SETTINGS = "settings"
GAME = "game"
current_state = MAIN_MENU

# Settings variables
volume = 0.5  # Default volume (50%)
difficulty = 1.0  # Default difficulty multiplier

# High score
try:
    with open("high_score.json", "r") as file:
        high_score = json.load(file)
except FileNotFoundError:
    high_score = 0  # Default high score if file doesn't exist

# Slider properties
slider_width = 200
slider_height = 10
slider_handle_radius = 10

def show_score_health(score, player_health):
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))  # Display high score
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))  # Display high score below the score
    # Removed the health text rendering

def draw_health_bar(player_health):
    max_health = 3
    health_bar_width = 100
    health_bar_height = 10
    health_bar_x = screen.get_width() - health_bar_width - 10  # 10 pixels from the right edge
    health_bar_y = 10  # 10 pixels from the top
    current_health_width = (player_health / max_health) * health_bar_width
    pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))  # Red background
    pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height))  # Green health
    
def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 16, y))

def fire_enemy_bullet(x, y):
    global enemy_bullet_state
    enemy_bullet_state = "fire"
    screen.blit(enemy_bullet_img, (x + 16, y))

def is_collision(x1, y1, x2, y2, threshold=27):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < threshold

def draw_button(text, x, y, width, height, inactive_color, active_color, radius=10):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)
    
    # Draw rounded rectangle
    pygame.draw.rect(screen, inactive_color, button_rect, border_radius=radius)
    if button_rect.collidepoint(mouse):
        pygame.draw.rect(screen, active_color, button_rect, border_radius=radius)
        if click[0] == 1:
            return True
    
    # Draw text
    text_surf = small_font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    return False

def draw_slider(x, y, value, min_value, max_value):
    global volume, difficulty
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    slider_rect = pygame.Rect(x, y, slider_width, slider_height)
    handle_x = x + int((value - min_value) / (max_value - min_value) * slider_width)
    
    # Draw slider track
    pygame.draw.rect(screen, (200, 200, 200), slider_rect, border_radius=5)
    
    # Draw slider handle
    pygame.draw.circle(screen, (0, 128, 255), (handle_x, y + slider_height // 2), slider_handle_radius)
    
    # Update value if dragging
    if click[0] == 1 and slider_rect.collidepoint(mouse):
        value = min_value + (mouse[0] - x) / slider_width * (max_value - min_value)
        value = max(min_value, min(max_value, value))  # Clamp value
    return value

def main_menu():
    global current_state
    screen.blit(background_img, (0, 0))
    
    title_text = font.render("Space Invaders", True, (255, 255, 255))
    screen.blit(title_text, (150, 100))
    
    if draw_button("Start Game", 200, 200, 100, 50, (0, 255, 0), (0, 200, 0)):
        current_state = GAME
    
    if draw_button("Settings", 200, 270, 100, 50, (0, 255, 0), (0, 200, 0)):
        current_state = SETTINGS
    
    if draw_button("Quit", 200, 340, 100, 50, (255, 0, 0), (200, 0, 0)):
        pygame.quit()
        quit()
    
    pygame.display.update()

def settings_screen():
    global current_state, volume, difficulty
    screen.blit(background_img, (0, 0))
    
    title_text = font.render("Settings", True, (255, 255, 255))
    screen.blit(title_text, (200, 50))
    
    # Volume slider
    volume_text = small_font.render(f"Volume: {int(volume * 100)}%", True, (255, 255, 255))
    screen.blit(volume_text, (50, 150))
    volume = draw_slider(50, 180, volume, 0.0, 1.0)
    pygame.mixer.music.set_volume(volume)
    
    # Difficulty slider
    difficulty_text = small_font.render(f"Difficulty: {difficulty:.1f}x", True, (255, 255, 255))
    screen.blit(difficulty_text, (50, 250))
    difficulty = draw_slider(50, 280, difficulty, 0.5, 2.0)
    
    if draw_button("Back", 200, 400, 100, 50, (0, 255, 0), (0, 200, 0)):
        current_state = MAIN_MENU
    
    pygame.display.update()

def game_loop():
    global current_state, high_score
    player_x = 225
    player_y = 400
    player_speed = 0.5
    player_x_change = 0
    player_y_change = 0
    player_health = 3
    
    enemy_x = random.randint(0, 436)
    enemy_y = 100
    enemy_speed = 0.2 * difficulty  # Adjust enemy speed based on difficulty
    
    bullet_x = 0
    bullet_y = player_y
    bullet_speed = 0.5
    global bullet_state
    bullet_state = "ready"
    
    enemy_bullet_x = 0
    enemy_bullet_y = enemy_y
    enemy_bullet_speed = 0.5
    global enemy_bullet_state
    enemy_bullet_state = "ready"
    
    score = 0
    running = True

    while running:
        screen.blit(background_img, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed
                if event.key == pygame.K_SPACE and bullet_state == "ready":
                    bullet_x = player_x
                    fire_bullet(bullet_x, bullet_y)
                    bullet_sound.play()
            
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    player_x_change = 0
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    player_y_change = 0
        
        player_x = max(0, min(player_x + player_x_change, 436))
        player_y = max(0, min(player_y + player_y_change, 436))
        
        if bullet_state == "fire":
            fire_bullet(bullet_x, bullet_y)
            bullet_y -= bullet_speed
            if bullet_y <= 0:
                bullet_y = player_y
                bullet_state = "ready"
        
        enemy_x += enemy_speed
        if enemy_x <= 0 or enemy_x >= 436:
            enemy_speed *= -1
        
        if enemy_bullet_state == "ready" and random.randint(1, 100) < 2:
            enemy_bullet_x = enemy_x
            enemy_bullet_y = enemy_y
            fire_enemy_bullet(enemy_bullet_x, enemy_bullet_y)
        
        if enemy_bullet_state == "fire":
            fire_enemy_bullet(enemy_bullet_x, enemy_bullet_y)
            enemy_bullet_y += enemy_bullet_speed
            if enemy_bullet_y >= 500:
                enemy_bullet_state = "ready"
        
        if is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
            bullet_y = player_y
            bullet_state = "ready"
            score += 1
            enemy_x = random.randint(0, 436)
            enemy_y = random.randint(50, 150)
        
        if is_collision(player_x, player_y, enemy_bullet_x, enemy_bullet_y, threshold=30):
            player_health -= 1
            enemy_bullet_state = "ready"
            enemy_bullet_y = enemy_y

            # Play explosion sound
            explosion_sound.play()

            # Show explosion image at player's position
            screen.blit(explosion_img, (player_x, player_y))
            pygame.display.update()

            # Add a short delay to show the explosion
            time.sleep(0.5)  # 0.5 seconds delay

            if player_health <= 0:
                # Update high score if current score is higher
                if score > high_score:
                    high_score = score
                    with open("high_score.json", "w") as file:
                        json.dump(high_score, file)
                game_over_screen(score)
                return
        
        screen.blit(player_img, (player_x, player_y))
        screen.blit(enemy_img, (enemy_x, enemy_y))
        show_score_health(score, player_health)
        draw_health_bar(player_health)
        pygame.display.update()

def game_over_screen(score):
    global current_state
    screen.blit(game_over_img, (0, 0))
    screen.blit(replay_img, (180, 300))
    game_over_sound.play()
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 180 <= mouse_x <= 320 and 300 <= mouse_y <= 360:
                    waiting = False
                    current_state = MAIN_MENU

# Main game loop
while True:
    if current_state == MAIN_MENU:
        main_menu()
    elif current_state == SETTINGS:
        settings_screen()
    elif current_state == GAME:
        game_loop()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()