import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Temp Run")

clock = pygame.time.Clock()
FPS = 60

# Load images (make sure these image files are in your folder)
background_img = pygame.image.load("background.png")
player_img = pygame.image.load("player.png")
log_img = pygame.image.load("log.png")
rock_img = pygame.image.load("rock.png")
pit_img = pygame.image.load("pit.png")
debris_img = pygame.image.load("debris.png")
snake_img = pygame.image.load("snake.png")
coin_img = pygame.image.load("coin.png")

# Scale images to appropriate sizes
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
player_img = pygame.transform.scale(player_img, (50, 60))
log_img = pygame.transform.scale(log_img, (50, 40))
rock_img = pygame.transform.scale(rock_img, (40, 35))
pit_img = pygame.transform.scale(pit_img, (70, 30))
debris_img = pygame.transform.scale(debris_img, (40, 40))
snake_img = pygame.transform.scale(snake_img, (60, 30))
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Player variables
player_x = 100
player_y = HEIGHT - player_img.get_height() - 50
player_vel_y = 0
gravity = 0.8
jump_strength = -15
player_speed = 5 # Horizontal movement speed

# Sliding variables
is_sliding = False
slide_duration = 20 # Frames sliding lasts
slide_timer = 0

# Horizontal movement bounds
player_min_x = 50
player_max_x = 200

# Obstacle speed
obstacle_speed = 7

# Score and fonts
score = 0
coin_score = 0 
font = pygame.font.SysFont(None, 36)

# Game state flags
game_over = False
game_paused = False
game_started = False

# Lives and invincibility after hit
lives = 3
invincible = False
invincibility_duration = 120
invincibility_timer = 0

# Obstacle types dictionary
obstacle_types = {
    "log": log_img,
    "rock": rock_img,
    "pit": pit_img,
    "debris": debris_img,
    "snake": snake_img,
}

# List for obstacles and coins currently on screen
obstacle_list = []
coin_list = []

def create_obstacle():
    """Create new obstacle dict"""
    obstacle_name = random.choice(list(obstacle_types.keys()))
    img = obstacle_types[obstacle_name]
    width, height = img.get_width(), img.get_height()

    if obstacle_name == "pit":
        y_pos = HEIGHT - 50 # Ground level for pits
        rect = pygame.Rect(WIDTH, y_pos, width, height)
    elif obstacle_name == "debris":
        y_pos = HEIGHT - player_img.get_height() - 200 # Starts high in air
        rect = pygame.Rect(WIDTH, y_pos, width, height)
    else:
        y_pos = HEIGHT - height - 50 # Ground obstacles
        if y_pos < 0: # Safety check
            y_pos = 0
        rect = pygame.Rect(WIDTH, y_pos, width, height)

    return{
        "name": obstacle_name,
        "image": img,
        "rect": rect,
        "falling": obstacle_name == "debris",
        "fall_speed": 5 if obstacle_name == "debris" else 0,
    }

def create_coin():
    """Creates a coin at a random horizontal position off right side of screen
       and a vertical position slightly above ground or floating (varies)"""
    x_pos = random.randint(WIDTH + 50, WIDTH + 300) # Spawn off screen right
    # Coins can appear near ground or a bit higher to encourage jumping/sliding
    y_pos = random.choice([
        HEIGHT - player_img.get_height() - 80,
        HEIGHT - player_img.get_height() - 150,
        HEIGHT - player_img.get_height() - 50,
    ])
    rect = pygame.Rect(x_pos, y_pos, coin_img.get_width(), coin_img.get_height())
    return {"rect": rect, "image": coin_img}

def draw_player(x, y, sliding):
    """Draw player sprite on screen. If sliding, draw crouched player. If invincible, player blinks(skips drawing intermittently)"""
    if sliding:
        slide_height = int(player_img.get_height() * 0.3)
        slide_img = pygame.transform.scale(player_img, (player_img.get_width(), slide_height))
        screen.blit(slide_img, (x, y + player_img.get_height() - slide_height))
        if invincible and (pygame.time.get_ticks() // 250) % 2 == 0:
            return # Skip drawing for blink effect
        screen.blit(slide_img, (x, y + player_img.get_height() // 2))
    else:
        if invincible and (pygame.time.get_ticks() // 250) % 2 == 0:
            return
        screen.blit(player_img, (x, y))

def draw_obstacle(obs):
    """Draws an obstacle image at its current position"""
    screen.blit(obs["image"], (obs["rect"].x, obs["rect"].y))

def draw_coin(coin):
    """Draws a coin image at its current position"""
    screen.blit(coin["image"], (coin["rect"].x, coin["rect"].y))

def display_score(current_score):
    """Display the current score in the top left corner"""
    score_text = font.render(f"Score: {current_score}", True, (0,0,0))
    screen.blit(score_text, (10, 10))

def display_coins(total_coins):
    """Displays total coins collected at the top, center right"""
    coin_text = font.render(f"Coins: {total_coins}", True, (255, 165, 0)) # Orange color
    screen.blit(coin_text, (WIDTH - 170, 10))

def display_lives(current_lives):
    """Displays remaning live in the top right corner in red"""
    lives_text = font.render(f"Lives: {current_lives}", True, (255, 0, 0))
    screen.blit(lives_text, (WIDTH - 120, 40))

def reset_game():
    """Reset all game variables to starting values. 
       Called when restarting after game over """
    
    global obstacle_list, coin_list, player_y, player_vel_y, score, coin_score, game_over, is_sliding, slide_timer, player_x
    global lives, invincible, invincibility_timer
    obstacle_list = []
    coin_list = []
    player_y = HEIGHT - player_img.get_height() - 50
    player_vel_y = 0
    score = 0
    coin_score = 0
    game_over = False
    is_sliding =False
    slide_timer = 0
    player_x = 100
    lives = 3
    invincible = False
    invincibility_timer = 0

def draw_start_menu():
    """Draws the start menu screen"""
    screen.fill((200, 200, 255))
    title = font.render("Temp Run", True, (0,0,0))
    instr = font.render("Press Enter to Start", True, (0,0,0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2))

def draw_pause_menu():
    """Draws the pause menu screen"""
    pause_text = font.render("Paused - Press P to Resume", True, (0,0,0))
    screen.blit(pause_text, (WIDTH // 2 -pause_text.get_width() // 2, HEIGHT // 2))

# Main game loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_started:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_started = True
            continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not game_over:
                game_paused = not game_paused

            if not game_paused and not game_over:
                if event.key == pygame.K_SPACE:
                    if player_y >= HEIGHT - player_img.get_height() - 50 and not is_sliding:
                        player_vel_y = jump_strength
                elif event.key == pygame.K_DOWN:
                    if not is_sliding and player_y >= HEIGHT - player_img.get_height() - 50:
                        is_sliding = True
                        slide_timer = slide_duration
    
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                reset_game()

    if not game_started:
        draw_start_menu()
        pygame.display.update()
        continue

    if game_paused:
        screen.blit(background_img, (0, 0))
        draw_pause_menu()
        pygame.display.update()
        continue

    if not game_over:
        # Handle left/right movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        # Clamp player horizontal position
        player_x = max(player_min_x, min(player_x, player_max_x))

        # Apply gravity for jumping/falling
        player_vel_y += gravity
        player_y += player_vel_y

        # Keep player on ground
        if player_y > HEIGHT - player_img.get_height() - 50:
            player_y = HEIGHT - player_img.get_height() - 50
            player_vel_y = 0

        # Handle sliding timer countdown
        if is_sliding:
            slide_timer -= 1
            if slide_timer <= 0:
                is_sliding = False

        # Spawn obstacles
        if len(obstacle_list) == 0 or obstacle_list[-1]["rect"].x < WIDTH - 350:
            new_obs = create_obstacle()
            obstacle_list.append(new_obs)

        # Spawn coins
        if len(coin_list) < 5:
            coin_list.append(create_coin())

        # Move obstacles left and update falling debris
        for obs in obstacle_list:
            obs["rect"].x -= obstacle_speed
            if obs["falling"]:
                obs["rect"].y += obs["fall_speed"]
                ground_y = HEIGHT - player_img.get_height() - 50
                if obs["rect"].y >= ground_y:
                    obs["rect"].y = ground_y
                    obs["fall_speed"] = 0

        # Remove off screen obstacles
        obstacle_list = [obs for obs in obstacle_list if obs["rect"].x + obs["rect"].width > 0]

        # Move coins left
        for coin in coin_list:
            coin["rect"].x -= obstacle_speed

        # Remove off screen coins
        coin_list = [coin for coin in coin_list if coin["rect"].x + coin["rect"].width > 0]

        # Create player collision rectangle, smaller if sliding
        if is_sliding:
            slide_height = int(player_img.get_height() * 0.3)
            player_rect = pygame.Rect(player_x, player_y + player_img.get_height() - slide_height, player_img.get_width(), slide_height)
        else:
            player_rect = pygame.Rect(player_x, player_y, player_img.get_width(), player_img.get_height())

        # Handle collision with obstacles if not invincible
        if not invincible:
            for obs in obstacle_list:
                if obs["name"] == "pit":
                    # Pit collision only if player on ground and overlapping pit
                    if player_rect.colliderect(obs["rect"]) and player_y >= HEIGHT - player_img.get_height() - 50:
                        lives -= 1
                        invincible = True
                        invincibility_timer = invincibility_duration

                else:
                    if player_rect.colliderect(obs["rect"]):
                        lives -= 1
                        invincible = True
                        invincibility_timer = invincibility_duration

            if lives <= 0:
                game_over = True

        # Handle collision with coins (collect coins)
        for coin in coin_list[:]: # Iterate over a copy to remove safely
            if player_rect.colliderect(coin["rect"]):
                coin_list.remove(coin) # Remove collected coin
                coin_score += 1 # Increment coin count
                score += 10 # Bonus points per coin collected

        # Count down invincibility timer
        if invincible:
            invincibility_timer -= 1
            if invincibility_timer <= 0:
                invincible = False

        score += 1 # Increment score every frame survived

    # Draw everything
    screen.blit(background_img, (0, 0))
    draw_player(player_x, player_y, is_sliding)
    # Draw obstacles wit degug rectangles
    for obs in obstacle_list:
        draw_obstacle(obs)
    
    # Draw coins
    for coin in coin_list:
        draw_coin(coin)

    display_score(score)
    display_coins(coin_score)
    display_lives(lives)

    # Game over message
    if game_over:
        over_text = font.render("Game Over! Press enter to Restart", True, (0, 0, 0))
        screen.blit(over_text, (WIDTH// 2 - over_text.get_width()//2, HEIGHT//2))

    pygame.display.update()

pygame.quit()
            
    
