import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Ball Platformer")
clock = pygame.time.Clock()

# Colors
BG_SKY = (135, 206, 235)
RED_BALL = (231, 76, 60)
BALL_EYE = (255, 255, 255)
PUPIL = (20, 20, 20)
GROUND_COLOR = (46, 204, 113)
SPIKE_COLOR = (192, 57, 43)
STAR_COLOR = (241, 196, 15)
BTN_BG = (44, 62, 80)
BTN_TXT = (236, 240, 241)

font = pygame.font.SysFont('sans-serif', 20, bold=True)
big_font = pygame.font.SysFont('sans-serif', 32, bold=True)

# Touch Buttons
btn_left = pygame.Rect(30, 510, 80, 55)
btn_right = pygame.Rect(130, 510, 80, 55)
btn_jump = pygame.Rect(280, 510, 90, 55)

# Game Levels Data: [platforms, spikes, star_pos, start_pos]
levels = [
    {
        "platforms": [
            pygame.Rect(0, 440, 400, 30),
            pygame.Rect(80, 340, 110, 15),
            pygame.Rect(230, 260, 120, 15),
            pygame.Rect(100, 170, 90, 15),
        ],
        "spikes": [pygame.Rect(200, 425, 40, 15)],
        "star": pygame.Rect(130, 130, 24, 24),
        "start": [40, 390]
    },
    {
        "platforms": [
            pygame.Rect(0, 440, 150, 30),
            pygame.Rect(260, 440, 140, 30),
            pygame.Rect(170, 350, 70, 15),
            pygame.Rect(40, 270, 90, 15),
            pygame.Rect(180, 190, 100, 15),
            pygame.Rect(310, 120, 80, 15),
        ],
        "spikes": [pygame.Rect(150, 450, 110, 20)],
        "star": pygame.Rect(340, 80, 24, 24),
        "start": [30, 390]
    }
]

current_level = 0
player_radius = 16

def load_level(lvl_idx):
    lvl = levels[lvl_idx]
    pos = list(lvl["start"])
    return pos, 0, 0, False

pos, vel_x, vel_y, on_ground = load_level(current_level)
rotation_angle = 0
game_won = False

running = True
move_left = False
move_right = False
jump_pressed = False

while running:
    # Handle Touch & Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            p = event.pos
            if btn_left.collidepoint(p): move_left = True
            elif btn_right.collidepoint(p): move_right = True
            elif btn_jump.collidepoint(p) and on_ground: 
                vel_y = -11.5
        elif event.type == pygame.MOUSEBUTTONUP:
            p = event.pos
            if not btn_left.collidepoint(p): move_left = False
            if not btn_right.collidepoint(p): move_right = False

    # Also handle keyboard for debugging
    keys = pygame.key.get_pressed()
    go_l = move_left or keys[pygame.K_LEFT]
    go_r = move_right or keys[pygame.K_RIGHT]
    if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and on_ground:
        vel_y = -11.5

    if not game_won:
        # Horizontal physics
        if go_l:
            vel_x = -4.5
            rotation_angle -= 8
        elif go_r:
            vel_x = 4.5
            rotation_angle += 8
        else:
            vel_x *= 0.8
            if abs(vel_x) < 0.2: vel_x = 0

        # Gravity
        vel_y += 0.65
        if vel_y > 14: vel_y = 14

        # Apply Horizontal Movement & Collisions
        pos[0] += vel_x
        player_rect = pygame.Rect(pos[0] - player_radius, pos[1] - player_radius, player_radius * 2, player_radius * 2)
        for plat in levels[current_level]["platforms"]:
            if player_rect.colliderect(plat):
                if vel_x > 0:
                    pos[0] = plat.left - player_radius
                elif vel_x < 0:
                    pos[0] = plat.right + player_radius

        # Apply Vertical Movement & Collisions
        pos[1] += vel_y
        on_ground = False
        player_rect = pygame.Rect(pos[0] - player_radius, pos[1] - player_radius, player_radius * 2, player_radius * 2)
        for plat in levels[current_level]["platforms"]:
            if player_rect.colliderect(plat):
                if vel_y > 0:
                    pos[1] = plat.top - player_radius
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    pos[1] = plat.bottom + player_radius
                    vel_y = 0

        # Boundary checks
        if pos[0] < player_radius: pos[0] = player_radius
        if pos[0] > WIDTH - player_radius: pos[0] = WIDTH - player_radius

        # Hazard check (Spikes or falling off-screen)
        hit_spike = any(player_rect.colliderect(spk) for spk in levels[current_level]["spikes"])
        if hit_spike or pos[1] > 480:
            pos, vel_x, vel_y, on_ground = load_level(current_level)

        # Star Collect / Next Level check
        if player_rect.colliderect(levels[current_level]["star"]):
            if current_level + 1 < len(levels):
                current_level += 1
                pos, vel_x, vel_y, on_ground = load_level(current_level)
            else:
                game_won = True

    # --- DRAWING ---
    screen.fill(BG_SKY)

    # Draw Platforms
    for plat in levels[current_level]["platforms"]:
        pygame.draw.rect(screen, GROUND_COLOR, plat, border_radius=6)
        pygame.draw.rect(screen, (39, 174, 96), (plat.x, plat.y, plat.width, 4))

    # Draw Spikes (Triangles)
    for spk in levels[current_level]["spikes"]:
        for sx in range(spk.x, spk.x + spk.width, 15):
            pts = [(sx, spk.bottom), (sx + 7, spk.top), (sx + 14, spk.bottom)]
            pygame.draw.polygon(screen, SPIKE_COLOR, pts)

    # Draw Goal Star
    star = levels[current_level]["star"]
    pygame.draw.circle(screen, STAR_COLOR, star.center, 12)
    pygame.draw.circle(screen, (243, 156, 18), star.center, 7)

    # Draw Red Ball (with cute rolling eyes)
    bx, by = int(pos[0]), int(pos[1])
    pygame.draw.circle(screen, RED_BALL, (bx, by), player_radius)
    
    eye_offset_x = 4 if vel_x >= 0 else -4
    pygame.draw.circle(screen, BALL_EYE, (bx + eye_offset_x - 3, by - 4), 4)
    pygame.draw.circle(screen, BALL_EYE, (bx + eye_offset_x + 5, by - 4), 4)
    pygame.draw.circle(screen, PUPIL, (bx + eye_offset_x - 2, by - 4), 2)
    pygame.draw.circle(screen, PUPIL, (bx + eye_offset_x + 6, by - 4), 2)

    # UI Panel & Touch Buttons
    pygame.draw.rect(screen, (25, 35, 45), (0, 480, WIDTH, 120))
    for btn, lbl in [(btn_left, "◄"), (btn_right, "►"), (btn_jump, "JUMP")]:
        pygame.draw.rect(screen, BTN_BG, btn, border_radius=12)
        txt = font.render(lbl, True, BTN_TXT)
        screen.blit(txt, txt.get_rect(center=btn.center))

    # Header Text
    lvl_txt = font.render(f"Level {current_level + 1}", True, (40, 40, 40))
    screen.blit(lvl_txt, (15, 15))

    if game_won:
        win_txt = big_font.render("ALL LEVELS CLEARED!", True, (39, 174, 96))
        screen.blit(win_txt, win_txt.get_rect(center=(WIDTH // 2, 220)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
