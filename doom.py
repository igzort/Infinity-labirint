import pygame
import math

# --- НАСТРОЙКИ ЭКРАНА REALME 8 PRO ---
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h

WIDTH = W
HEIGHT = int(H * 0.8) 
OFFSET_Y = (H - HEIGHT) // 2 

sc = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# --- ПАРАМЕТРЫ ДРАЙВА ---
FPS = 35 
TILE = 60 
FOV = math.pi / 3 
NUM_RAYS = 100 
PROJ_COEFF = 2.5 * (NUM_RAYS / (2 * math.tan(FOV/2))) * TILE
SCALE = WIDTH // NUM_RAYS

text_map = [
    '1111111111111111',
    '1000100010002001',
    '1010101011110101',
    '1000000000000001',
    '1011111011111011',
    '1020000020000021',
    '1111111111111111',
]

world_map = {}
enemies = []
for j, row in enumerate(text_map):
    for i, char in enumerate(row):
        if char == '1': world_map[(i * TILE, j * TILE)] = 1
        elif char == '2': enemies.append({'pos': [i * TILE + TILE//2, j * TILE + TILE//2], 'alive': True})

px, py = TILE + 15, TILE + 15
pa = 0
shot_timer = 0
speed = 3.5 
rot_speed = 0.06

def check_wall(x, y):
    return (x // TILE * TILE, y // TILE * TILE) in world_map

while True:
    sc.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT: exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx > WIDTH * 0.5 and shot_timer == 0:
                shot_timer = 5
                for en in enemies:
                    if en['alive']:
                        # ИСПРАВЛЕНО: Обращаемся к индексам [0] и [1]
                        vx, vy = en['pos'][0] - px, en['pos'][1] - py
                        dist = math.hypot(vx, vy)
                        angle_to_en = math.atan2(vy, vx)
                        diff = (angle_to_en - pa + math.pi) % (2 * math.pi) - math.pi
                        if abs(diff) < 0.25 and dist < 500:
                            en['alive'] = False

    dx, dy, dr = 0, 0, 0
    if pygame.mouse.get_pressed():
        mx, my = pygame.mouse.get_pos()
        if mx < WIDTH * 0.5:
            if my < OFFSET_Y + HEIGHT * 0.6:
                dx, dy = speed * math.cos(pa), speed * math.sin(pa)
            if mx < WIDTH * 0.2: dr = -rot_speed
            elif WIDTH * 0.3 < mx < WIDTH * 0.5: dr = rot_speed

    pa += dr
    if not check_wall(px + dx, py): px += dx
    if not check_wall(px, py + dy): py += dy

    # РЕНДЕР
    pygame.draw.rect(sc, (5, 5, 10), (0, OFFSET_Y, WIDTH, HEIGHT // 2)) 
    pygame.draw.rect(sc, (25, 25, 25), (0, OFFSET_Y + HEIGHT // 2, WIDTH, HEIGHT // 2)) 

    cur_a = pa - FOV / 2
    for ray in range(NUM_RAYS):
        sin_a, cos_a = math.sin(cur_a), math.cos(cur_a)
        for depth in range(1, 800, 8):
            tx, ty = px + depth * cos_a, py + depth * sin_a
            if (tx // TILE * TILE, ty // TILE * TILE) in world_map:
                depth *= math.cos(pa - cur_a)
                h = PROJ_COEFF / (depth + 0.0001)
                c = 255 / (1 + depth * depth * 0.00005)
                pygame.draw.rect(sc, (c, c // 2, 40), (ray * SCALE, OFFSET_Y + HEIGHT // 2 - h // 2, SCALE, h))
                break
            
            hit_en = False
            for en in enemies:
                # ИСПРАВЛЕНО: Координаты X и Y разделены
                if en['alive'] and abs(tx - en['pos'][0]) < 12 and abs(ty - en['pos'][1]) < 12:
                    depth *= math.cos(pa - cur_a)
                    h = PROJ_COEFF / (depth + 0.0001)
                    pygame.draw.rect(sc, (255, 0, 0), (ray * SCALE, OFFSET_Y + HEIGHT // 2 - h // 2, SCALE, h))
                    hit_en = True; break
            if hit_en: break
        cur_a += FOV / NUM_RAYS

    # ОРУЖИЕ И ИНТЕРФЕЙС
    gy = OFFSET_Y + HEIGHT - 40
    if shot_timer > 0:
        pygame.draw.circle(sc, (255, 255, 100), (WIDTH // 2, gy - 150), 60)
        gy += 30
        shot_timer -= 1
    
    pygame.draw.rect(sc, (40, 40, 40), (WIDTH // 2 - 40, gy - 140, 80, 200))
    pygame.draw.rect(sc, (20, 20, 20), (WIDTH // 2 - 25, gy - 180, 50, 70))
    
    pygame.draw.circle(sc, (255, 0, 0), (WIDTH // 2, OFFSET_Y + HEIGHT // 2), 6, 1)
    pygame.draw.circle(sc, (200, 0, 0), (WIDTH - 150, H - 150), 80, 4)

    pygame.display.flip()
    clock.tick(FPS)
