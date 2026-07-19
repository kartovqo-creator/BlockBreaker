__version__ = "1.0.0 BETA"
import pygame
import sys
import os
import webbrowser

# 1. Инициализация на Pygame
pygame.init()
pygame.font.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

# Размери на прозореца
WIDTH = 450  
HEIGHT = 750  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Block Breaker")

# 2. Зареждане на графиките
try:
    raw_paddle_img = pygame.image.load(get_path("paddle.png")).convert_alpha()
    raw_ball_img = pygame.image.load(get_path("ball.png")).convert_alpha()
    raw_brick_img = pygame.image.load(get_path("brick.png")).convert_alpha()
    
    raw_btn_template = pygame.image.load(get_path("Button.png")).convert_alpha()
    raw_btn_continue = pygame.image.load(get_path("ContinueButton.png")).convert_alpha()
    raw_btn_back = pygame.image.load(get_path("BackButton.png")).convert_alpha()
    raw_btn_pause = pygame.image.load(get_path("PauseButton.png")).convert_alpha()
except pygame.error as e:
    print(f"Грешка при зареждане на картинка: {e}")
    sys.exit()

# Скалиране на графиките
brick_img = pygame.transform.scale(raw_brick_img, (64, 24))
paddle_img = pygame.transform.scale(raw_paddle_img, (100, 24))
ball_img = pygame.transform.scale(raw_ball_img, (16, 16))

btn_template = pygame.transform.scale(raw_btn_template, (130, 35))
btn_continue = pygame.transform.scale(raw_btn_continue, (160, 40))
btn_back = pygame.transform.scale(raw_btn_back, (70, 25))
btn_pause = pygame.transform.scale(raw_btn_pause, (35, 35))

BRICK_WIDTH = brick_img.get_width()
BRICK_HEIGHT = brick_img.get_height()
GAP = 4  
COLS = 8
WIDTH = (COLS * BRICK_WIDTH) + ((COLS - 1) * GAP) + 40  
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

# Цветове
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GRAY = (180, 180, 180)  
GREEN = (50, 255, 50)  
clock = pygame.time.Clock()
FPS = 60

SENSITIVITY = 0.5 

# Шрифтове
score_font = pygame.font.Font(None, 32)
loading_title_font = pygame.font.Font(None, 48)  
loading_sub_font = pygame.font.Font(None, 36)    
menu_title_font = pygame.font.Font(None, 48)
game_over_font = pygame.font.Font(None, 64)
restart_font = pygame.font.Font(None, 24)
button_font = pygame.font.Font(None, 18)  
text_font = pygame.font.Font(None, 22)

# Статистики
stats_data = {
    "played_games": 0,
    "destroyed_blocks": 0,
    "lost_balls": 0,
    "highest_score": 0,
    "playtime_seconds": 0,  
    "joined_date": "17/07/2026"
}
score = 0
single_game_destroyed = 0  
game_started_counted = False  

def format_playtime(total_seconds):
    seconds = int(total_seconds % 60)
    minutes = int((total_seconds // 60) % 60)
    hours = int(total_seconds // 3600)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

achievements_data = [
    {"type": "single", "req": 100, "tier": "Common"},
    {"type": "single", "req": 250, "tier": "Common"},
    {"type": "single", "req": 500, "tier": "Rare"},
    {"type": "single", "req": 750, "tier": "Rare"},
    {"type": "single", "req": 1000, "tier": "Rare"},
    {"type": "single", "req": 1500, "tier": "Epic"},
    {"type": "single", "req": 2000, "tier": "Epic"},
    {"type": "single", "req": 3000, "tier": "Epic"},
    {"type": "single", "req": 5000, "tier": "Legendary"},
    {"type": "single", "req": 10000, "tier": "Legendary"},
    {"type": "single", "req": 20000, "tier": "Mythic"},
    {"type": "single", "req": 30000, "tier": "Mythic"},
    
    {"type": "all_time", "req": 10000, "tier": "Common"},
    {"type": "all_time", "req": 25000, "tier": "Rare"},
    {"type": "all_time", "req": 50000, "tier": "Rare"},
    {"type": "all_time", "req": 75000, "tier": "Epic"},
    {"type": "all_time", "req": 100000, "tier": "Epic"},
    {"type": "all_time", "req": 200000, "tier": "Epic"},
    {"type": "all_time", "req": 300000, "tier": "Epic"},
    {"type": "all_time", "req": 500000, "tier": "Legendary"},
    {"type": "all_time", "req": 1000000, "tier": "Mythic"},
    
    {"type": "games", "req": 10, "tier": "Common"},
    {"type": "games", "req": 25, "tier": "Common"},
    {"type": "games", "req": 50, "tier": "Common"},
    {"type": "games", "req": 100, "tier": "Rare"},
    {"type": "games", "req": 250, "tier": "Rare"},
    {"type": "games", "req": 500, "tier": "Rare"},
    {"type": "games", "req": 1000, "tier": "Rare"},
    {"type": "games", "req": 1500, "tier": "Rare"},
    {"type": "games", "req": 2000, "tier": "Rare"},
    {"type": "games", "req": 5000, "tier": "Epic"},
    
    {"type": "playtime", "req": 1, "tier": "Common"},
    {"type": "playtime", "req": 10, "tier": "Rare"},
    {"type": "playtime", "req": 50, "tier": "Epic"},
    {"type": "playtime", "req": 100, "tier": "Epic"},
    {"type": "playtime", "req": 200, "tier": "Legendary"},
    {"type": "playtime", "req": 500, "tier": "Legendary"},
    {"type": "playtime", "req": 1000, "tier": "Mythic"},
    {"type": "playtime", "req": 10000, "tier": "Mythic"}
]

class UI_Button:
    def __init__(self, image, center_x, y, text=""):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x
        self.rect.top = y
        self.text = text

    def draw(self):
        screen.blit(self.image, self.rect)
        if self.text:
            text_surf = button_font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Paddle:
    def __init__(self):
        self.image = paddle_img
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 50

    def update(self):
        rel_x, _ = pygame.mouse.get_rel()
        if ball.active and current_state == "GAMEPLAY":
            self.rect.x += int(rel_x * SENSITIVITY)
        
        if self.rect.left < 10: self.rect.left = 10
        if self.rect.right > WIDTH - 10: self.rect.right = WIDTH - 10

    def draw(self):
        screen.blit(self.image, self.rect)

class Ball:
    def __init__(self):
        self.image = ball_img
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        global game_started_counted
        paddle.reset_position()
        self.rect.centerx = paddle.rect.centerx
        self.rect.bottom = paddle.rect.top - 5
        self.speed_x = 5
        self.speed_y = -5
        self.active = False
        game_started_counted = False  
        
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def update(self):
        if not self.active:
            self.rect.centerx = paddle.rect.centerx
            self.rect.bottom = paddle.rect.top - 5
            return

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.speed_y *= -1

    def draw(self):
        screen.blit(self.image, self.rect)

class Brick:
    def __init__(self, x, y):
        self.image = brick_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hitbox = self.rect.inflate(-2, 0)

    def draw(self):
        screen.blit(self.image, self.rect)

def create_bricks():
    bricks_list = []
    rows, cols = 6, 8
    start_y = 100  
    total_wall_width = (cols * BRICK_WIDTH) + ((cols - 1) * GAP)
    start_x = (WIDTH - total_wall_width) // 2

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (BRICK_WIDTH + GAP)
            y = start_y + row * (BRICK_HEIGHT + GAP)
            bricks_list.append(Brick(x, y))
    return bricks_list

current_state = "LOADING"
loading_frame = 0
TOTAL_LOADING_TIME = 180  

paddle = Paddle()
ball = Ball()
bricks = create_bricks()

pause_icon_rect = btn_pause.get_rect(topright=(WIDTH - 20, 20))
scroll_y = 0
MAX_SCROLL = -1500  

discord_rect = pygame.Rect(40, 260, 250, 25)

def restart_game():
    global score, bricks, single_game_destroyed
    score = 0
    single_game_destroyed = 0
    bricks = create_bricks()
    ball.reset()

def enter_gameplay():
    global current_state
    current_state = "GAMEPLAY"
    if ball.active:
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    else:
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

def enter_menu(menu_state):
    global current_state, scroll_y
    current_state = menu_state
    scroll_y = 0  
    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0  
    stats_data["playtime_seconds"] += dt
    
    mouse_pos = pygame.mouse.get_pos()

    btn_click_achievements = UI_Button(btn_template, WIDTH // 2 - 75, HEIGHT // 2 - 120, "Achievements")
    btn_click_stats = UI_Button(btn_template, WIDTH // 2 + 75, HEIGHT // 2 - 120, "Stats")
    btn_click_more = UI_Button(btn_template, WIDTH // 2, HEIGHT // 2 - 70, "More")
    
    # Бутони за Пауза Менюто
    btn_click_continue = UI_Button(btn_continue, WIDTH // 2, HEIGHT // 2 + 60, "Continue")
    btn_click_exit = UI_Button(btn_template, WIDTH // 2, HEIGHT // 2 + 120, "Exit")
    
    # Бутони за другите екрани
    btn_click_back = UI_Button(btn_back, 60, 40, "Back")
    btn_click_restart = UI_Button(btn_continue, WIDTH // 2, HEIGHT // 2 + 60, "Restart Game")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                if current_state == "GAMEPLAY":
                    if pause_icon_rect.collidepoint(mouse_pos):
                        enter_menu("PAUSE_MENU")
                    elif not ball.active:
                        if not game_started_counted:
                            stats_data["played_games"] += 1
                            game_started_counted = True
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        pygame.mouse.set_pos([WIDTH // 2, HEIGHT // 2])
                        pygame.mouse.get_rel()
                        ball.active = True
                        
                elif current_state == "PAUSE_MENU":
                    if btn_click_continue.is_clicked(mouse_pos): enter_gameplay()
                    elif btn_click_achievements.is_clicked(mouse_pos): enter_menu("ACHIEVEMENTS_MENU")
                    elif btn_click_stats.is_clicked(mouse_pos): enter_menu("STATS_MENU")
                    elif btn_click_more.is_clicked(mouse_pos): enter_menu("MORE_MENU")
                    elif btn_click_exit.is_clicked(mouse_pos): running = False # Изход от играта
                    
                elif current_state in ["STATS_MENU", "ACHIEVEMENTS_MENU", "MORE_MENU"]:
                    if btn_click_back.is_clicked(mouse_pos): enter_menu("PAUSE_MENU")
                
                elif current_state == "GAME_OVER":
                    if btn_click_restart.is_clicked(mouse_pos):
                        restart_game()
                        enter_gameplay()
                
                if current_state == "MORE_MENU" and discord_rect.collidepoint(mouse_pos):
                    webbrowser.open("https://discord.gg/NWhq9m9H65")

            if current_state == "ACHIEVEMENTS_MENU":
                if event.button == 4:  
                    scroll_y = min(0, scroll_y + 35)
                elif event.button == 5:  
                    scroll_y = max(MAX_SCROLL, scroll_y - 35) 

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state == "GAMEPLAY": enter_menu("PAUSE_MENU")
                elif current_state == "PAUSE_MENU": enter_gameplay()
                elif current_state in ["STATS_MENU", "ACHIEVEMENTS_MENU", "MORE_MENU"]: enter_menu("PAUSE_MENU")
            
            if current_state == "GAME_OVER" and event.key == pygame.K_r:
                restart_game()
                enter_gameplay()

    # --- ИЗРИСУВАНЕ ---
    screen.fill(BLACK)

    if current_state == "LOADING":
        letters_to_show = min(loading_frame // 4, len("Block Breaker"))
        title_text = loading_title_font.render("Block Breaker"[:letters_to_show], True, GRAY)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        if letters_to_show >= len("Block Breaker"):
            dots = "." * ((loading_frame // 10) % 4)
            sub_text = loading_sub_font.render("Loading" + dots, True, GRAY)
            screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 50))
        if loading_frame >= TOTAL_LOADING_TIME: enter_gameplay()
        loading_frame += 1

    elif current_state == "GAMEPLAY":
        paddle.update()
        ball.update()
        if ball.rect.bottom >= HEIGHT:
            stats_data["lost_balls"] += 1
            enter_menu("GAME_OVER")
        if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
            ball.speed_y *= -1
            relative_hit = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
            ball.speed_x = relative_hit * 7
        for brick in bricks[:]:
            if ball.rect.colliderect(brick.hitbox):
                if ball.rect.bottom >= brick.rect.top and ball.rect.top <= brick.rect.bottom: ball.speed_y *= -1
                else: ball.speed_x *= -1
                bricks.remove(brick)
                score += 1
                single_game_destroyed += 1
                stats_data["destroyed_blocks"] += 1
                if score > stats_data["highest_score"]: stats_data["highest_score"] = score
                break
        paddle.draw()
        ball.draw()
        for brick in bricks: brick.draw()
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(btn_pause, pause_icon_rect)

    elif current_state == "PAUSE_MENU":
        beta_text = button_font.render("Beta Version", True, GRAY)
        screen.blit(beta_text, (WIDTH - beta_text.get_width() - 20, 20))
        title = menu_title_font.render("Game Paused", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        btn_click_achievements.draw()
        btn_click_stats.draw()
        btn_click_more.draw()
        btn_click_continue.draw()
        btn_click_exit.draw()

    elif current_state == "STATS_MENU":
        title = menu_title_font.render("Stats", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        y_offset = 180
        
        t1 = text_font.render(f"Played Games / {stats_data['played_games']}", True, WHITE)
        screen.blit(t1, (50, y_offset))
        y_offset += 50 
        
        t2 = text_font.render(f"Destroyed Blocks / {stats_data['destroyed_blocks']}", True, WHITE)
        screen.blit(t2, (50, y_offset))
        y_offset += 25
        t3 = text_font.render(f"Lost Balls / {stats_data['lost_balls']}", True, WHITE)
        screen.blit(t3, (50, y_offset))
        y_offset += 50
        
        t4 = text_font.render(f"Highest Score / {stats_data['highest_score']}", True, WHITE)
        screen.blit(t4, (50, y_offset))
        y_offset += 50
        
        time_str = format_playtime(stats_data["playtime_seconds"])
        t5 = text_font.render(f"Playtime / {time_str}", True, WHITE)
        screen.blit(t5, (50, y_offset))
        y_offset += 25
        t6 = text_font.render(f"Joined / {stats_data['joined_date']}", True, WHITE)
        screen.blit(t6, (50, y_offset))
            
        btn_click_back.draw()

    elif current_state == "ACHIEVEMENTS_MENU":
        scroll_surface = pygame.Surface((WIDTH - 80, 2500))
        scroll_surface.fill(BLACK)
        
        y_text = 10
        categories = [
            ("--- Destroyed Blocks (Single Game) ---", "single"),
            ("--- Destroyed Blocks (All Time) ---", "all_time"),
            ("--- Played Games (All Time) ---", "games"),
            ("--- Playtime (All Time) ---", "playtime")
        ]
        
        for title_cat, cat_type in categories:
            t_surf = text_font.render(title_cat, True, WHITE)
            scroll_surface.blit(t_surf, (10, y_text))
            y_text += 35
            
            for ach in achievements_data:
                if ach["type"] == cat_type:
                    if cat_type == "single": current_val = single_game_destroyed
                    elif cat_type == "all_time": current_val = stats_data["destroyed_blocks"]
                    elif cat_type == "games": current_val = stats_data["played_games"]
                    else: current_val = int(stats_data["playtime_seconds"] // 3600)
                        
                    is_done = current_val >= ach["req"]
                    status_str = "DONE" if is_done else "Not Done"
                    status_color = GREEN if is_done else GRAY
                    
                    if cat_type == "games":
                        unit = "Games"
                    elif cat_type == "playtime":
                        unit = "Hour" if ach["req"] == 1 else "Hours"
                    else:
                        unit = "Blocks"
                        
                    line_str = f"{ach['req']:,} {unit} / {status_str} / {ach['tier']}"
                    
                    ach_surf = text_font.render(line_str, True, status_color)
                    scroll_surface.blit(ach_surf, (20, y_text))
                    y_text += 28
            y_text += 20

        screen.blit(scroll_surface, (40, 140), (0, -scroll_y, WIDTH - 80, 540))
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 135)) 
        title = menu_title_font.render("Achievements", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        btn_click_back.draw()

    elif current_state == "MORE_MENU":
        title = menu_title_font.render("More", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        info_text1 = text_font.render("I don't know what more to add :]", True, WHITE)
        info_text2 = text_font.render("Join the Discord Server:", True, WHITE)
        link_text = text_font.render("https://discord.gg/NWhq9m9H65", True, GRAY)
        screen.blit(info_text1, (40, 180))
        screen.blit(info_text2, (40, 230))
        screen.blit(link_text, (discord_rect.x, discord_rect.y))
        btn_click_back.draw()

    elif current_state == "GAME_OVER":
        go_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 3))
        
        final_score_text = score_font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 - 20))
        
        # Визуален бутон за рестарт на телефона
        btn_click_restart.draw()
        
        instructions_text = restart_font.render("Press 'R' to Restart", True, GRAY)
        screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 2 + 130))

    pygame.display.flip()

pygame.event.set_grab(False)
pygame.quit()
sys.exit()
