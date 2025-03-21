import pygame
import random
import math
import json
import time

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 560
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Inverters")

# Load images
game_over_img = pygame.image.load("game_over.png")
background_img = pygame.image.load("background.jpg").convert()
player_img = pygame.transform.scale(pygame.image.load("enemy.png"), (80, 80))
bullet_img = pygame.image.load("bullet.png")
powerup_imgs = {
    "speed": pygame.image.load("powerup.png"),
    "health": pygame.image.load("powerup_health.png"),
    "bullet": pygame.image.load("powerup_bullet.png"),
    "double": pygame.image.load("powerup_double.png"),
    "triple": pygame.image.load("powerup_triple.png"),
    "ashoot": pygame.image.load("powerup_ashoot.png"),
    "godmode": pygame.image.load("powerup_godmode.png"),
    "supermode": pygame.image.load("powerup_supermode.png")
}
meteor_img = pygame.transform.scale(pygame.image.load("meteor.png"), (40, 40))
icon = pygame.image.load("UFO.png")
pygame.display.set_icon(icon)

# Load sounds
game_over_sound = pygame.mixer.Sound("game_over.mp3")
bullet_sound = pygame.mixer.Sound("bullet_sounds.mp3")
explosion_sound = pygame.mixer.Sound("explosion.mp3")
button_hover_sound = pygame.mixer.Sound("button_hover.mp3")
button_click_sound = pygame.mixer.Sound("button_click.mp3")
powerup_sound = pygame.mixer.Sound("powerup.mp3")
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

# Font setup
font = pygame.font.Font('freesansbold.ttf', 24)
small_font = pygame.font.Font('freesansbold.ttf', 18)
title_font = pygame.font.Font('freesansbold.ttf', 48)
button_font = pygame.font.Font('freesansbold.ttf', 32)

# Game states
INTRO = "intro"
MAIN_MENU = "main_menu"
SETTINGS = "settings"
GAME = "game"
PAUSED = "paused"
SHOP = "shop"
LEADERBOARD = "leaderboard"
MISSIONS = "missions"
MISSION_MODE = "mission_mode"
HOW_TO_PLAY = "how_to_play"
current_state = INTRO

# Settings variables
volume = 0.5
vibration = True
money = 0
high_score = 0
achievements = {
    "Meteor Dodger": False,
    "Power-Up Collector": False,
    "Speed Demon": False
}
try:
    with open("high_score.json", "r") as file:
        high_score = json.load(file)
except FileNotFoundError:
    high_score = 0
try:
    with open("achievements.json", "r") as file:
        achievements.update(json.load(file))
except FileNotFoundError:
    pass

# Slider properties
slider_width = 200
slider_height = 10
slider_handle_radius = 10

# Scrolling background variables
scroll = 0
bg_height = background_img.get_height()

# Game objects
powerups = []
meteors = []
particles = []

# Spaceship setup
spaceships = [pygame.image.load(f"spaceship{i}.png") for i in range(1, 6)]
spaceship_prices = [0, 100, 200, 300, 400]
spaceship_abilities = [
    "Speed Boost (+50%)",
    "Double Damage",
    "Extra Health (+1)",
    "Faster Bullets",
    "Shield (5 sec)"
]
owned_spaceships = [True, False, False, False, False]
current_spaceship = 0

# Leaderboard and user name
leaderboard = {}
try:
    with open("leaderboard.json", "r") as file:
        leaderboard = json.load(file)
except FileNotFoundError:
    leaderboard = {}
user_name = None

# Notification variables
notification_text = None
notification_timer = 0

# Mission variables
missions = [
    {"name": "Destroy 10 Enemies", "goal": "enemies", "target": 10, "reward": 50},
    {"name": "Collect 5 Power-ups", "goal": "powerups", "target": 5, "reward": 30},
    {"name": "Survive 30 Seconds", "goal": "time", "target": 30, "reward": 20},
    {"name": "Destroy 5 Meteors", "goal": "meteors", "target": 5, "reward": 40},
    {"name": "Score 50 Points", "goal": "score", "target": 50, "reward": 60}
]
completed_missions = set()
try:
    with open("completed_missions.json", "r") as file:
        completed_missions = set(json.load(file))
except FileNotFoundError:
    completed_missions = set()

# Fire rate
FIRE_RATE = 0.2
last_shot_time = 0

# Button class with animation
class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, text_color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.text_color = text_color
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
        self.scale = 1.0

    def draw(self, screen):
        color = self.active_color if self.hovered else self.inactive_color
        scaled_width = int(self.width * self.scale)
        scaled_height = int(self.height * self.scale)
        scaled_rect = pygame.Rect(self.x - (scaled_width - self.width) // 2, self.y - (scaled_height - self.height) // 2, scaled_width, scaled_height)
        pygame.draw.rect(screen, color, scaled_rect, border_radius=10)
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.scale = 1.1 if self.hovered else 1.0
        if self.hovered:
            button_hover_sound.play()

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            button_click_sound.play()
            return True
        return False

# Enemy class
class Enemy:
    def __init__(self, x, y, health, color, type="fast"):
        self.x = x
        self.y = y
        self.health = health
        self.color = color
        self.type = type
        self.radius = 20 if type == "fast" else 40 if type == "tank" else 30
        self.speed = 0.3 if type == "fast" else 0.1 if type == "tank" else 0.2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        health_text = font.render(f"{self.health}", True, (255, 255, 255))
        screen.blit(health_text, (self.x - 10, self.y - 40))

# Power-up class
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.speed = 0.3
        self.image = powerup_imgs[type]
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Meteor class
class Meteor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.5
        self.image = meteor_img
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Particle class for explosion and confetti effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 5)
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def animated_title():
    title_text = title_font.render("Space Inverters", True, (255, 255, 255))
    x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    y = 200 + math.sin(time.time() * 3) * 20
    screen.blit(title_text, (x, y))

def show_score_health(score, player_health, elapsed_time):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    money_text = font.render(f"Money: ${money}", True, (255, 255, 255))
    time_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))
    screen.blit(money_text, (10, 70))
    screen.blit(time_text, (10, 100))
    draw_health_bar(player_health)

def draw_health_bar(player_health):
    max_health = 3 + (1 if current_spaceship == 2 else 0)
    health_bar_width = 100
    health_bar_height = 10
    health_bar_x = SCREEN_WIDTH - health_bar_width - 10
    health_bar_y = 60
    current_health_width = (player_health / max_health) * health_bar_width
    pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height))

def fire_bullet(x, y, big_bullet=False, angle=0):
    img = pygame.transform.scale(bullet_img, (20, 40)) if big_bullet else bullet_img
    rotated_img = pygame.transform.rotate(img, angle)
    screen.blit(rotated_img, (x - rotated_img.get_width() // 2, y - rotated_img.get_height() // 2))

def rect_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def show_notification(text, duration=2):
    global notification_text, notification_timer
    notification_text = font.render(text, True, (255, 255, 0))
    notification_timer = time.time() + duration

def draw_notification():
    global notification_text, notification_timer
    if notification_text and time.time() < notification_timer:
        screen.blit(notification_text, (SCREEN_WIDTH // 2 - notification_text.get_width() // 2, SCREEN_HEIGHT - 100))

def draw_slider(x, y, value, min_value, max_value):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    slider_rect = pygame.Rect(x, y, slider_width, slider_height)
    handle_x = x + int((value - min_value) / (max_value - min_value) * slider_width)
    pygame.draw.rect(screen, (200, 200, 200), slider_rect, border_radius=5)
    pygame.draw.circle(screen, (0, 128, 255), (handle_x, y + slider_height // 2), slider_handle_radius)
    if click[0] == 1 and slider_rect.collidepoint(mouse):
        value = min_value + (mouse[0] - x) / slider_width * (max_value - min_value)
        value = max(min_value, min(max_value, value))
    return value

def intro_animation():
    global current_state, scroll
    start_time = time.time()
    virus_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    virus_x = SCREEN_WIDTH // 2
    virus_y = -50
    virus_radius = 10

    while current_state == INTRO:
        screen.blit(background_img, (0, scroll))
        screen.blit(background_img, (0, scroll - bg_height))
        scroll = (scroll + 1) % bg_height

        elapsed_time = time.time() - start_time
        if elapsed_time < 2:
            alpha = int((elapsed_time / 2) * 255)
            title = title_font.render("Space Inverters", True, (255, 255, 255))
            title.set_alpha(alpha)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        elif elapsed_time < 5:
            virus_y += 2
            virus_radius += 1
            pygame.draw.circle(screen, random.choice(virus_colors), (int(virus_x), int(virus_y)), virus_radius)
            story1 = small_font.render("A massive virus, bigger than COVID-19,", True, (255, 255, 255))
            story2 = small_font.render("has invaded space!", True, (255, 255, 255))
            screen.blit(story1, (SCREEN_WIDTH // 2 - story1.get_width() // 2, 400))
            screen.blit(story2, (SCREEN_WIDTH // 2 - story2.get_width() // 2, 430))
        elif elapsed_time < 8:
            pygame.draw.circle(screen, random.choice(virus_colors), (int(virus_x), int(virus_y)), virus_radius)
            mission1 = small_font.render("Your mission: Defeat the viruses", True, (255, 255, 255))
            mission2 = small_font.render("and dodge the meteors!", True, (255, 255, 255))
            screen.blit(mission1, (SCREEN_WIDTH // 2 - mission1.get_width() // 2, 400))
            screen.blit(mission2, (SCREEN_WIDTH // 2 - mission2.get_width() // 2, 430))
        else:
            current_state = MAIN_MENU

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_state = MAIN_MENU

        pygame.display.update()

def main_menu():
    global current_state, user_name
    start_button = Button("Start Game", SCREEN_WIDTH // 2 - 100, 300, 200, 50, (0, 0, 150), (0, 0, 255))
    missions_button = Button("Missions", SCREEN_WIDTH // 2 - 100, 400, 200, 50, (150, 150, 0), (255, 255, 0))
    settings_button = Button("Settings", SCREEN_WIDTH // 2 - 100, 500, 200, 50, (0, 150, 0), (0, 255, 0))
    shop_button = Button("Shop", SCREEN_WIDTH // 2 - 100, 600, 200, 50, (150, 0, 150), (255, 0, 255))
    leaderboard_button = Button("Leaderboard", SCREEN_WIDTH // 2 - 100, 700, 200, 50, (0, 150, 150), (0, 255, 255))
    exit_button = Button("Exit", SCREEN_WIDTH // 2 - 100, 800, 200, 50, (150, 0, 0), (255, 0, 0))
    
    name_input = ""
    input_active = user_name is None

    while current_state == MAIN_MENU:
        screen.blit(background_img, (0, 0))
        animated_title()

        if input_active:
            name_text = font.render("Enter Name: " + name_input, True, (255, 255, 255))
            screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 300))
        else:
            start_button.draw(screen)
            missions_button.draw(screen)
            settings_button.draw(screen)
            shop_button.draw(screen)
            leaderboard_button.draw(screen)
            exit_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name_input:
                    user_name = name_input
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                else:
                    name_input += event.unicode
            if not input_active and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.check_click(mouse_pos):
                    current_state = GAME
                elif missions_button.check_click(mouse_pos):
                    current_state = MISSIONS
                elif settings_button.check_click(mouse_pos):
                    current_state = SETTINGS
                elif shop_button.check_click(mouse_pos):
                    current_state = SHOP
                elif leaderboard_button.check_click(mouse_pos):
                    current_state = LEADERBOARD
                elif exit_button.check_click(mouse_pos):
                    pygame.quit()
                    quit()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                start_button.check_hover(mouse_pos)
                missions_button.check_hover(mouse_pos)
                settings_button.check_hover(mouse_pos)
                shop_button.check_hover(mouse_pos)
                leaderboard_button.check_hover(mouse_pos)
                exit_button.check_hover(mouse_pos)

        pygame.display.update()

def how_to_play_screen():
    global current_state
    back_button = Button("Back", SCREEN_WIDTH // 2 - 100, 700, 200, 50, (150, 0, 0), (255, 0, 0))
    
    instructions = [
        "Controls:",
        "LEFT ARROW: Move Left",
        "RIGHT ARROW: Move Right",
        "UP ARROW: Move Up",
        "DOWN ARROW: Move Down",
        "SPACE: Shoot",
        "Goal: Survive and defeat enemies",
        "Collect power-ups for special abilities!",
        "Watch out for different enemy types!"
    ]

    while current_state == HOW_TO_PLAY:
        screen.blit(background_img, (0, 0))
        for i, line in enumerate(instructions):
            text = small_font.render(line, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 30))
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(pygame.mouse.get_pos()):
                    current_state = MAIN_MENU

        pygame.display.update()

def missions_screen():
    global current_state
    back_button = Button("Back", SCREEN_WIDTH // 2 - 100, 700, 200, 50, (150, 0, 0), (255, 0, 0))
    mission_buttons = [
        Button(m["name"] + (" (Completed)" if i in completed_missions else ""), 50, 150 + i * 100, 460, 50, 
               (0, 150, 0) if i not in completed_missions else (150, 150, 150), 
               (0, 255, 0) if i not in completed_missions else (200, 200, 200))
        for i, m in enumerate(missions)
    ]

    while current_state == MISSIONS:
        screen.blit(background_img, (0, 0))
        back_button.draw(screen)
        for i, btn in enumerate(mission_buttons):
            btn.draw(screen)
            reward_text = small_font.render(f"Reward: ${missions[i]['reward']}", True, (255, 255, 255))
            screen.blit(reward_text, (50, 200 + i * 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_button.check_click(mouse_pos):
                    current_state = MAIN_MENU
                for i, btn in enumerate(mission_buttons):
                    if btn.check_click(mouse_pos) and i not in completed_missions:
                        mission_mode(i)
                        if current_state == MISSIONS:
                            btn.text = missions[i]["name"] + (" (Completed)" if i in completed_missions else "")

        pygame.display.update()

def mission_mode(mission_index):
    global current_state, money, completed_missions, scroll, last_shot_time
    current_state = MISSION_MODE
    mission = missions[mission_index]
    player_x = SCREEN_WIDTH // 2 - 40
    player_y = SCREEN_HEIGHT - 120
    player_speed = 0.3 * (1.5 if current_spaceship == 0 else 1)
    player_health = 3
    player_boost = {"speed": False, "bullet": False, "speed_time": 0, "bullet_time": 0, "shield": current_spaceship == 4, 
                    "shield_time": 0, "double": False, "double_time": 0, "triple": False, "triple_time": 0, 
                    "ashoot": False, "ashoot_time": 0, "godmode": False, "godmode_time": 0, 
                    "supermode": False, "supermode_time": 0}
    player_x_change = 0
    player_y_change = 0
    player_rect = spaceships[current_spaceship].get_rect(topleft=(player_x, player_y))

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    enemies = [Enemy(random.randint(0, SCREEN_WIDTH - 60), -50 - i * 300, 5, random.choice(colors)) for i in range(3)]
    bullets = []
    score = 0
    mission_progress = {"enemies": 0, "powerups": 0, "time": 0, "meteors": 0, "score": 0}
    start_time = time.time()

    pause_button = Button("Pause", SCREEN_WIDTH - 110, SCREEN_HEIGHT - 50, 100, 40, (150, 150, 150), (200, 200, 200))
    firing = False

    while current_state == MISSION_MODE:
        screen.blit(background_img, (0, scroll))
        screen.blit(background_img, (0, scroll - bg_height))
        scroll = (scroll + 1) % bg_height

        current_time = time.time()
        current_fire_rate = 0.05 if player_boost["supermode"] else FIRE_RATE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_UP:
                    player_y_change = -player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_DOWN:
                    player_y_change = player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_SPACE:
                    firing = True
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player_x_change = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    player_y_change = 0
                if event.key == pygame.K_SPACE:
                    firing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button.check_click(pygame.mouse.get_pos()):
                    current_state = PAUSED

        if firing and (current_time - last_shot_time >= current_fire_rate):
            bullet_x = player_x + spaceships[current_spaceship].get_width() // 2 - bullet_img.get_width() // 2
            bullet_speed = 0.7 * (1.5 if current_spaceship == 3 or player_boost["supermode"] else 1)
            if player_boost["godmode"]:
                for angle in range(0, 360, 30):
                    bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": angle})
            elif player_boost["ashoot"]:
                for angle in [-30, -15, 0, 15, 30]:
                    bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": angle})
            elif player_boost["triple"] or player_boost["supermode"]:
                bullets.append({"x": bullet_x - 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x + 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            elif player_boost["double"]:
                bullets.append({"x": bullet_x - 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x + 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            else:
                bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            bullet_sound.play()
            last_shot_time = current_time

        player_x = max(0, min(player_x + player_x_change, SCREEN_WIDTH - spaceships[current_spaceship].get_width()))
        player_y = max(0, min(player_y + player_y_change, SCREEN_HEIGHT - spaceships[current_spaceship].get_height()))
        player_rect.topleft = (player_x, player_y)

        for key in ["speed", "bullet", "shield", "double", "triple", "ashoot", "godmode", "supermode"]:
            if player_boost[key] and current_time - player_boost[f"{key}_time"] > 5:
                player_boost[key] = False

        mission_progress["time"] = current_time - start_time

        for bullet in bullets[:]:
            angle_rad = math.radians(bullet["angle"])
            bullet["x"] += bullet["speed"] * math.sin(angle_rad)
            bullet["y"] -= bullet["speed"] * math.cos(angle_rad)
            fire_bullet(bullet["x"], bullet["y"], bullet["big"], bullet["angle"])
            if bullet["y"] <= 0 or bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.y += enemy.speed
            enemy.draw(screen)
            enemy_rect = pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)
            if rect_collision(player_rect, enemy_rect) and not player_boost["shield"]:
                player_health -= 1
                enemies.remove(enemy)
                enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 60), -50, 5, random.choice(colors)))
                explosion_sound.play()
                for _ in range(10):
                    particles.append(Particle(enemy.x, enemy.y, enemy.color))
            elif enemy.y > SCREEN_HEIGHT:
                enemies.remove(enemy)
                enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 60), -50, 5, random.choice(colors)))

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if rect_collision(pygame.Rect(bullet["x"], bullet["y"], bullet_img.get_width(), bullet_img.get_height()), 
                                  pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)):
                    bullets.remove(bullet)
                    enemy.health -= 2
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 60), -50, 5, random.choice(colors)))
                        score += 10
                        mission_progress["enemies"] += 1
                        mission_progress["score"] = score
                        for _ in range(10):
                            particles.append(Particle(enemy.x, enemy.y, enemy.color))
                    break

        if not powerups and random.randint(1, 200) == 1:
            powerup_type = random.choice(["speed", "health", "bullet", "double", "triple", "ashoot", "godmode", "supermode"])
            powerups.append(PowerUp(random.randint(0, SCREEN_WIDTH - 64), -50, powerup_type))

        for powerup in powerups[:]:
            powerup.y += powerup.speed
            powerup.rect.topleft = (powerup.x, powerup.y)
            powerup.draw(screen)
            if rect_collision(player_rect, powerup.rect):
                if powerup.type == "speed":
                    player_boost["speed"] = True
                    player_boost["speed_time"] = time.time()
                    show_notification("Speed Boost!")
                elif powerup.type == "health":
                    player_health = min(3 + (1 if current_spaceship == 2 else 0), player_health + 1)
                    show_notification("Health Restored!")
                elif powerup.type == "bullet":
                    player_boost["bullet"] = True
                    player_boost["bullet_time"] = time.time()
                    show_notification("Big Bullets!")
                elif powerup.type == "double":
                    player_boost["double"] = True
                    player_boost["double_time"] = time.time()
                    show_notification("Double Shoot!")
                elif powerup.type == "triple":
                    player_boost["triple"] = True
                    player_boost["triple_time"] = time.time()
                    show_notification("Triple Shoot!")
                elif powerup.type == "ashoot":
                    player_boost["ashoot"] = True
                    player_boost["ashoot_time"] = time.time()
                    show_notification("A Shoot!")
                elif powerup.type == "godmode":
                    player_boost["godmode"] = True
                    player_boost["godmode_time"] = time.time()
                    show_notification("God Mode Shoot!")
                elif powerup.type == "supermode":
                    player_boost["supermode"] = True
                    player_boost["supermode_time"] = time.time()
                    show_notification("Super Mode Shoot!")
                powerups.remove(powerup)
                mission_progress["powerups"] += 1
                powerup_sound.play()
            elif powerup.y > SCREEN_HEIGHT:
                powerups.remove(powerup)

        if not meteors and random.randint(1, 300) == 1:
            meteors.append(Meteor(random.randint(0, SCREEN_WIDTH - 40), -50))

        for meteor in meteors[:]:
            meteor.y += meteor.speed
            meteor.rect.topleft = (meteor.x, meteor.y)
            meteor.draw(screen)
            if rect_collision(player_rect, meteor.rect) and not player_boost["shield"]:
                player_health -= 1
                meteors.remove(meteor)
                explosion_sound.play()
                for _ in range(10):
                    particles.append(Particle(meteor.x, meteor.y, (150, 150, 150)))
            elif meteor.y > SCREEN_HEIGHT:
                meteors.remove(meteor)
                mission_progress["meteors"] += 1

        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)

        screen.blit(spaceships[current_spaceship], (player_x, player_y))
        show_score_health(score, player_health, current_time - start_time)
        pause_button.draw(screen)
        mission_text = font.render(f"Mission: {mission['name']} ({mission_progress[mission['goal']]}/{mission['target']})", True, (255, 255, 255))
        screen.blit(mission_text, (10, 130))
        draw_notification()

        if mission_progress[mission["goal"]] >= mission["target"]:
            money += mission["reward"]
            completed_missions.add(mission_index)
            with open("completed_missions.json", "w") as file:
                json.dump(list(completed_missions), file)
            show_notification(f"Mission Completed! Reward: ${mission['reward']}")
            current_state = MISSIONS
            return

        if player_health <= 0:
            show_notification("Mission Failed!")
            current_state = MISSIONS
            return

        pygame.display.update()

def settings_screen():
    global current_state, volume, vibration
    back_button = Button("Back", SCREEN_WIDTH // 2 - 100, 600, 200, 50, (150, 0, 0), (255, 0, 0))
    vibration_button = Button("Vibration: " + ("On" if vibration else "Off"), SCREEN_WIDTH // 2 - 100, 400, 200, 50, (0, 150, 0), (0, 255, 0))

    while current_state == SETTINGS:
        screen.blit(background_img, (0, 0))
        volume_text = small_font.render(f"Volume: {int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(volume_text, (50, 150))
        volume = draw_slider(50, 180, volume, 0.0, 1.0)
        pygame.mixer.music.set_volume(volume)
        vibration_button.draw(screen)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if vibration_button.check_click(mouse_pos):
                    vibration = not vibration
                    vibration_button.text = "Vibration: " + ("On" if vibration else "Off")
                if back_button.check_click(mouse_pos):
                    current_state = MAIN_MENU

        pygame.display.update()

def game_loop():
    global current_state, high_score, scroll, money, user_name, last_shot_time, achievements
    player_x = SCREEN_WIDTH // 2 - 40
    player_y = SCREEN_HEIGHT - 120
    player_speed = 0.3 * (1.5 if current_spaceship == 0 else 1)
    player_health = 3
    player_boost = {"speed": False, "bullet": False, "speed_time": 0, "bullet_time": 0, "shield": current_spaceship == 4, 
                    "shield_time": 0, "double": False, "double_time": 0, "triple": False, "triple_time": 0, 
                    "ashoot": False, "ashoot_time": 0, "godmode": False, "godmode_time": 0, 
                    "supermode": False, "supermode_time": 0}
    player_x_change = 0
    player_y_change = 0
    player_rect = spaceships[current_spaceship].get_rect(topleft=(player_x, player_y))

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
    enemy_types = ["fast", "tank", "shooter"]
    enemies = [Enemy(random.randint(0, SCREEN_WIDTH - 60), -50 - i * 300, 5, random.choice(colors), random.choice(enemy_types)) for i in range(3)]
    bullets = []
    score = 0
    enemies_defeated = 0
    meteors_dodged = 0
    powerups_collected = 0
    spawn_timer = 0
    start_time = time.time()
    powerups.clear()
    meteors.clear()
    particles.clear()

    pause_button = Button("Pause", SCREEN_WIDTH - 110, SCREEN_HEIGHT - 50, 100, 40, (150, 150, 150), (200, 200, 200))
    firing = False

    while current_state == GAME:
        screen.blit(background_img, (0, scroll))
        screen.blit(background_img, (0, scroll - bg_height))
        scroll = (scroll + 1) % bg_height

        current_time = time.time()
        elapsed_time = current_time - start_time
        current_fire_rate = 0.05 if player_boost["supermode"] else FIRE_RATE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_UP:
                    player_y_change = -player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_DOWN:
                    player_y_change = player_speed * (2 if player_boost["speed"] or player_boost["supermode"] else 1)
                if event.key == pygame.K_SPACE:
                    firing = True
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player_x_change = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    player_y_change = 0
                if event.key == pygame.K_SPACE:
                    firing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if pause_button.check_click(mouse_pos):
                    current_state = PAUSED

        if firing and (current_time - last_shot_time >= current_fire_rate):
            bullet_x = player_x + spaceships[current_spaceship].get_width() // 2 - bullet_img.get_width() // 2
            bullet_speed = 0.7 * (1.5 if current_spaceship == 3 or player_boost["supermode"] else 1)
            if player_boost["godmode"]:
                for angle in range(0, 360, 30):
                    bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": angle})
            elif player_boost["ashoot"]:
                for angle in [-30, -15, 0, 15, 30]:
                    bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": angle})
            elif player_boost["triple"] or player_boost["supermode"]:
                bullets.append({"x": bullet_x - 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x + 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            elif player_boost["double"]:
                bullets.append({"x": bullet_x - 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
                bullets.append({"x": bullet_x + 20, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            else:
                bullets.append({"x": bullet_x, "y": player_y, "big": player_boost["bullet"], "speed": bullet_speed, "angle": 0})
            bullet_sound.play()
            last_shot_time = current_time

        player_x = max(0, min(player_x + player_x_change, SCREEN_WIDTH - spaceships[current_spaceship].get_width()))
        player_y = max(0, min(player_y + player_y_change, SCREEN_HEIGHT - spaceships[current_spaceship].get_height()))
        player_rect.topleft = (player_x, player_y)

        for key in ["speed", "bullet", "shield", "double", "triple", "ashoot", "godmode", "supermode"]:
            if player_boost[key] and current_time - player_boost[f"{key}_time"] > 5:
                player_boost[key] = False

        spawn_timer += 1
        if spawn_timer >= 60 and len(enemies) < 10:
            type = random.choice(enemy_types)
            enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 60), -50, 5, random.choice(colors), type))
            spawn_timer = 0

        for bullet in bullets[:]:
            angle_rad = math.radians(bullet["angle"])
            bullet["x"] += bullet["speed"] * math.sin(angle_rad)
            bullet["y"] -= bullet["speed"] * math.cos(angle_rad)
            fire_bullet(bullet["x"], bullet["y"], bullet["big"], bullet["angle"])
            if bullet["y"] <= 0 or bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.y += enemy.speed
            enemy.draw(screen)
            enemy_rect = pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)
            if rect_collision(player_rect, enemy_rect) and not player_boost["shield"]:
                player_health -= 1
                enemies.remove(enemy)
                explosion_sound.play()
                for _ in range(10):
                    particles.append(Particle(enemy.x, enemy.y, enemy.color))
            elif enemy.y > SCREEN_HEIGHT:
                enemies.remove(enemy)
                enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 60), -50, 5, random.choice(colors), random.choice(enemy_types)))

        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if rect_collision(pygame.Rect(bullet["x"], bullet["y"], bullet_img.get_width(), bullet_img.get_height()), 
                                  pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)):
                    bullets.remove(bullet)
                    enemy.health -= 2 if current_spaceship != 1 else 4
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        enemies_defeated += 1
                        score += 10
                        money += 10
                        for _ in range(10):
                            particles.append(Particle(enemy.x, enemy.y, enemy.color))
                    break

        if not powerups and random.randint(1, 200) == 1:
            powerup_type = random.choice(["speed", "health", "bullet", "double", "triple", "ashoot", "godmode", "supermode"])
            powerups.append(PowerUp(random.randint(0, SCREEN_WIDTH - 64), -50, powerup_type))

        for powerup in powerups[:]:
            powerup.y += powerup.speed
            powerup.rect.topleft = (powerup.x, powerup.y)
            powerup.draw(screen)
            if rect_collision(player_rect, powerup.rect):
                if powerup.type == "speed":
                    player_boost["speed"] = True
                    player_boost["speed_time"] = time.time()
                    show_notification("Speed Boost!")
                elif powerup.type == "health":
                    player_health = min(3 + (1 if current_spaceship == 2 else 0), player_health + 1)
                    show_notification("Health Restored!")
                elif powerup.type == "bullet":
                    player_boost["bullet"] = True
                    player_boost["bullet_time"] = time.time()
                    show_notification("Big Bullets!")
                elif powerup.type == "double":
                    player_boost["double"] = True
                    player_boost["double_time"] = time.time()
                    show_notification("Double Shoot!")
                elif powerup.type == "triple":
                    player_boost["triple"] = True
                    player_boost["triple_time"] = time.time()
                    show_notification("Triple Shoot!")
                elif powerup.type == "ashoot":
                    player_boost["ashoot"] = True
                    player_boost["ashoot_time"] = time.time()
                    show_notification("A Shoot!")
                elif powerup.type == "godmode":
                    player_boost["godmode"] = True
                    player_boost["godmode_time"] = time.time()
                    show_notification("God Mode Shoot!")
                elif powerup.type == "supermode":
                    player_boost["supermode"] = True
                    player_boost["supermode_time"] = time.time()
                    show_notification("Super Mode Shoot!")
                powerups.remove(powerup)
                powerups_collected += 1
                if powerups_collected >= 20 and not achievements["Power-Up Collector"]:
                    achievements["Power-Up Collector"] = True
                    show_notification("Achievement Unlocked: Power-Up Collector!")
                powerup_sound.play()
            elif powerup.y > SCREEN_HEIGHT:
                powerups.remove(powerup)

        if not meteors and random.randint(1, 300) == 1:
            meteors.append(Meteor(random.randint(0, SCREEN_WIDTH - 40), -50))

        for meteor in meteors[:]:
            meteor.y += meteor.speed
            meteor.rect.topleft = (meteor.x, meteor.y)
            meteor.draw(screen)
            if rect_collision(player_rect, meteor.rect) and not player_boost["shield"]:
                player_health -= 1
                meteors.remove(meteor)
                explosion_sound.play()
                for _ in range(10):
                    particles.append(Particle(meteor.x, meteor.y, (150, 150, 150)))
            elif meteor.y > SCREEN_HEIGHT:
                meteors.remove(meteor)
                meteors_dodged += 1
                if meteors_dodged >= 10 and not achievements["Meteor Dodger"]:
                    achievements["Meteor Dodger"] = True
                    show_notification("Achievement Unlocked: Meteor Dodger!")

        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)

        screen.blit(spaceships[current_spaceship], (player_x, player_y))
        show_score_health(score, player_health, elapsed_time)
        pause_button.draw(screen)
        draw_notification()

        if player_health <= 0:
            if score > high_score:
                high_score = score
                with open("high_score.json", "w") as file:
                    json.dump(high_score, file)
            leaderboard[user_name] = max(leaderboard.get(user_name, 0), score)
            with open("leaderboard.json", "w") as file:
                json.dump(leaderboard, file)
            with open("achievements.json", "w") as file:
                json.dump(achievements, file)
            game_over_screen(score)
            return

        if elapsed_time > 30 and not achievements["Speed Demon"]:
            achievements["Speed Demon"] = True
            show_notification("Achievement Unlocked: Speed Demon!")

        pygame.display.update()

def shop_screen():
    global current_state, money, current_spaceship, owned_spaceships
    buttons = []
    for i in range(5):
        if owned_spaceships[i]:
            text = "Equip" if i != current_spaceship else "Equipped"
        else:
            text = f"Buy ${spaceship_prices[i]}"
        buttons.append(Button(text, 350, 200 + i * 100, 150, 50, (0, 150, 0), (0, 255, 0)))
    back_button = Button("Back", 180, 750, 200, 50, (150, 0, 0), (255, 0, 0))

    while current_state == SHOP:
        screen.blit(background_img, (0, 0))
        for i, (img, price, btn) in enumerate(zip(spaceships, spaceship_prices, buttons)):
            screen.blit(img, (100, 200 + i * 100))
            btn.draw(screen)
            ability_text = small_font.render(spaceship_abilities[i], True, (255, 255, 255))
            screen.blit(ability_text, (200, 230 + i * 100))
        money_text = font.render(f"Money: ${money}", True, (255, 255, 255))
        screen.blit(money_text, (180, 150))
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, btn in enumerate(buttons):
                    if btn.check_click(pos):
                        if not owned_spaceships[i] and money >= spaceship_prices[i]:
                            money -= spaceship_prices[i]
                            owned_spaceships[i] = True
                            btn.text = "Equip"
                        elif owned_spaceships[i] and i != current_spaceship:
                            current_spaceship = i
                            for j, b in enumerate(buttons):
                                b.text = "Equip" if owned_spaceships[j] and j != current_spaceship else "Equipped" if j == current_spaceship else f"Buy ${spaceship_prices[j]}"
                if back_button.check_click(pos):
                    current_state = MAIN_MENU

        pygame.display.update()

def leaderboard_screen():
    global current_state
    back_button = Button("Back", 180, 700, 200, 50, (150, 0, 0), (255, 0, 0))

    while current_state == LEADERBOARD:
        screen.blit(background_img, (0, 0))
        sorted_scores = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (name, score) in enumerate(sorted_scores):
            text = font.render(f"{i+1}. {name}: {score}", True, (255, 255, 255))
            screen.blit(text, (180, 300 + i * 50))
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(pygame.mouse.get_pos()):
                    current_state = MAIN_MENU

        pygame.display.update()

def game_over_screen(score):
    global current_state
    replay_button = Button("Replay", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 50, (0, 150, 0), (0, 255, 0))
    menu_button = Button("Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 220, 200, 50, (150, 0, 0), (255, 0, 0))
    game_over_y = SCREEN_HEIGHT // 2 - 150
    game_over_x = SCREEN_WIDTH // 2 - game_over_img.get_width() // 2
    animation_offset = math.sin(time.time() * 5) * 15

    while True:
        screen.blit(background_img, (0, 0))
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, game_over_y - 50))
        screen.blit(game_over_img, (game_over_x, game_over_y + animation_offset))
        
        replay_button.draw(screen)
        menu_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if replay_button.check_click(pos):
                    current_state = GAME
                    return
                elif menu_button.check_click(pos):
                    current_state = MAIN_MENU
                    return

        pygame.display.update()

def pause_screen():
    global current_state
    resume_button = Button("Resume", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, (0, 150, 0), (0, 255, 0))
    menu_button = Button("Menu", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 50, (150, 0, 0), (255, 0, 0))

    while current_state == PAUSED:
        screen.blit(background_img, (0, 0))
        resume_button.draw(screen)
        menu_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if resume_button.check_click(pos):
                    current_state = GAME if previous_state == GAME else MISSION_MODE
                elif menu_button.check_click(pos):
                    current_state = MAIN_MENU

        pygame.display.update()

# Main game loop
previous_state = None
while True:
    if current_state == INTRO:
        intro_animation()
    elif current_state == MAIN_MENU:
        main_menu()
    elif current_state == SETTINGS:
        settings_screen()
    elif current_state == GAME:
        previous_state = GAME
        game_loop()
    elif current_state == PAUSED:
        pause_screen()
    elif current_state == SHOP:
        shop_screen()
    elif current_state == LEADERBOARD:
        leaderboard_screen()
    elif current_state == MISSIONS:
        missions_screen()
    elif current_state == MISSION_MODE:
        previous_state = MISSION_MODE
        mission_mode(0)
    elif current_state == HOW_TO_PLAY:
        how_to_play_screen()