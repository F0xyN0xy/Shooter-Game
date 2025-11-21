import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

# Sounds
pygame.mixer.music.load("sounds/background_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound("sounds/shooting_effect.mp3")
shoot_sound.set_volume(0.3)
tap_sound = pygame.mixer.Sound("sounds/tap_effect.mp3")
tap_sound.set_volume(0.2)
hit_sound = pygame.mixer.Sound("sounds/hit_effect.wav")
hit_sound.set_volume(0.3)

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Shooter Game")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
title_font = pygame.font.Font(None, 96)

# Player as an Image
player_image = pygame.Surface((50, 30), pygame.SRCALPHA)
pygame.draw.polygon(player_image, (255, 0, 0), [(0, 0), (50, 15), (0, 30)])

# Player
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 7
player_health = 100
max_health = 100

# Bullet
bullets = []
bullets_speed = 10

# Enemies
enemies = []
enemy_spawn_timer = 0
enemy_spawn_interval = 1500  # milliseconds
enemy_speed = 5

# Score
score = 0

# Game State
game_state = "menu"  # "menu", "playing", "game_over"
victory = False

# Menu buttons
start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

def spawn_enemy():
    """Spawn enemy at random edge of screen"""
    side = random.randint(0, 3)
    
    if side == 0:  # Top
        pos = pygame.Vector2(random.randint(0, WIDTH), -20)
    elif side == 1:  # Right
        pos = pygame.Vector2(WIDTH + 20, random.randint(0, HEIGHT))
    elif side == 2:  # Bottom
        pos = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 20)
    else:  # Left
        pos = pygame.Vector2(-20, random.randint(0, HEIGHT))
    
    enemies.append({
        "pos": pos,
        "health": 3,
        "radius": 20
    })

def check_collision(pos1, radius1, pos2, radius2):
    """Check circular collision between two objects"""
    distance = math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)
    return distance < (radius1 + radius2)

def reset_game():
    """Reset all game variables"""
    global player_pos, player_health, bullets, enemies, score, victory, last_spawn_time
    player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    player_health = max_health
    bullets.clear()
    enemies.clear()
    score = 0
    victory = False
    last_spawn_time = pygame.time.get_ticks()

def draw_button(surface, rect, text, mouse_pos, base_color, hover_color):
    """Draw a button with hover effect"""
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (255, 255, 255), rect, 3, border_radius=10)
    
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

running = True
last_spawn_time = pygame.time.get_ticks()

while running:
    dt = clock.tick(60) / 1000
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            # Update button positions
            start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
            quit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
            # Keep player in bounds
            player_pos.x = max(25, min(WIDTH - 25, player_pos.x))
            player_pos.y = max(25, min(HEIGHT - 25, player_pos.y))

        # Menu interactions
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(mouse_pos):
                    game_state = "playing"
                    reset_game()
                elif quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Playing interactions
        elif game_state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = mouse_pos
                shoot_sound.play()
                
                direction = pygame.Vector2(mouse_x - player_pos.x, mouse_y - player_pos.y).normalize()

                bullets.append({
                    "pos": pygame.Vector2(player_pos.x, player_pos.y),
                    "dir": direction
                })
        
        # Game over interactions
        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "playing"
                reset_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "menu"
    
    # Menu State
    if game_state == "menu":
        screen.fill((20, 20, 40))
        
        # Title
        title_text = title_font.render("SHOOTER", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)
        
        # Instructions
        inst_texts = [
            "WASD - Move",
            "Left Click - Shoot",
            "Survive and reach 200 points!"
        ]
        
        for i, text in enumerate(inst_texts):
            inst_surf = font.render(text, True, (200, 200, 200))
            inst_rect = inst_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120 + i * 35))
            screen.blit(inst_surf, inst_rect)
        
        # Buttons
        draw_button(screen, start_button_rect, "START", mouse_pos, (0, 120, 0), (0, 180, 0))
        draw_button(screen, quit_button_rect, "QUIT", mouse_pos, (120, 0, 0), (180, 0, 0))
    
    # Playing State
    elif game_state == "playing":
        # Player Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_pos.y > 25:
            player_pos.y -= player_speed
        if keys[pygame.K_s] and player_pos.y < HEIGHT - 25:
            player_pos.y += player_speed
        if keys[pygame.K_a] and player_pos.x > 25:
            player_pos.x -= player_speed
        if keys[pygame.K_d] and player_pos.x < WIDTH - 25:
            player_pos.x += player_speed
        
        # Mouse Position for player rotation
        mouse_x, mouse_y = mouse_pos
        rel_x = mouse_x - player_pos.x
        rel_y = mouse_y - player_pos.y
        angle = math.degrees(math.atan2(-rel_y, rel_x))

        # Spawn enemies
        if current_time - last_spawn_time > enemy_spawn_interval:
            spawn_enemy()
            last_spawn_time = current_time

        # Update Bullets
        new_bullets = []
        for bullet in bullets:
            bullet["pos"] += bullet["dir"] * bullets_speed
            
            if 0 <= bullet["pos"].x <= WIDTH and 0 <= bullet["pos"].y <= HEIGHT:
                new_bullets.append(bullet)
        bullets = new_bullets
        

        # Update Enemies
        new_enemies = []
        for enemy in enemies:
            # Move enemy towards player
            direction = pygame.Vector2(player_pos.x - enemy["pos"].x, player_pos.y - enemy["pos"].y)
            if direction.length() > 0:
                direction = direction.normalize()
                enemy["pos"] += direction * enemy_speed

            # Check collision with bullets
            hit = False
            new_bullets_after_hit = []
            for bullet in bullets:
                if check_collision(bullet["pos"], 6, enemy["pos"], enemy["radius"]):
                    enemy["health"] -= 1
                    hit = True
                    tap_sound.play()
                    if enemy["health"] <= 0:
                        score += 10
                else:
                    new_bullets_after_hit.append(bullet)
            
            if hit:
                bullets = new_bullets_after_hit
            
            # Check collision with player
            if check_collision(player_pos, 25, enemy["pos"], enemy["radius"]):
                player_health -= 10
                enemies.remove(enemy)
                hit_sound.play()
            elif enemy["health"] > 0:
                new_enemies.append(enemy)
        
        enemies = new_enemies

        # Check game over conditions
        if player_health <= 0:
            game_state = "game_over"
            victory = False
        elif score >= 200:
            game_state = "game_over"
            victory = True

        # Rotate Player Image
        rotated_player = pygame.transform.rotate(player_image, angle)
        rect = rotated_player.get_rect(center=(player_pos.x, player_pos.y))

        # Drawing
        screen.fill((30, 30, 30))

        # Draw Player
        screen.blit(rotated_player, rect)

        # Draw Bullets
        for bullet in bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet["pos"].x), int(bullet["pos"].y)), 6)

        # Draw Enemies
        for enemy in enemies:
            color = (0, 255, 0) if enemy["health"] == 3 else (255, 165, 0) if enemy["health"] == 2 else (255, 0, 0)
            pygame.draw.circle(screen, color, (int(enemy["pos"].x), int(enemy["pos"].y)), enemy["radius"])

        # Draw HUD
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Health bar
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = player_health / max_health
        
        pygame.draw.rect(screen, (100, 100, 100), (10, 50, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (10, 50, health_bar_width * health_percentage, health_bar_height))
        
        health_text = font.render(f"HP: {player_health}/{max_health}", True, (255, 255, 255))
        screen.blit(health_text, (220, 50))
    
    # Game Over State
    elif game_state == "game_over":
        screen.fill((30, 30, 30))
        
        if victory:
            end_text = large_font.render("VICTORY!", True, (0, 255, 0))
        else:
            end_text = large_font.render("GAME OVER", True, (255, 0, 0))
        
        end_rect = end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        screen.blit(end_text, end_rect)

        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(score_text, score_rect)

        restart_text = font.render("Press SPACE to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

        menu_text = font.render("Press ESC for Menu", True, (200, 200, 200))
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(menu_text, menu_rect)

    pygame.display.flip()

pygame.quit()