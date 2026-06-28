import pygame
import math

# Глобальные переменные для хранения текстур
sky_texture = None
floor_texture = None

def check_wall(x, y, TILE, world_map):
    return (int(x // TILE) * TILE, int(y // TILE) * TILE) in world_map

def generate_night_sky(W, H):
    sky_w = W * 4
    sky_h = H // 2
    sky_surf = pygame.Surface((sky_w, sky_h))
    
    for y in range(sky_h):
        color_coeff = y / sky_h
        r = int(5 + 10 * color_coeff)
        g = int(5 + 15 * color_coeff)
        b = int(12 + 25 * color_coeff)
        pygame.draw.line(sky_surf, (r, g, b), (0, y), (sky_w, y))
        
    for i in range(150):
        star_x = int((math.sin(i * 453.12) * 0.5 + 0.5) * sky_w)
        star_y = int((math.cos(i * 761.34) * 0.5 + 0.5) * (sky_h - 40))
        star_alpha = int((math.sin(i) * 0.5 + 0.5) * 155) + 100
        pygame.draw.circle(sky_surf, (star_alpha, star_alpha, 255), (star_x, star_y), 1)

    moon_x = sky_w // 4  
    moon_y = sky_h // 3
    
    for radius in range(40, 24, -2):
        alpha = int((40 - radius) * 3)
        pygame.draw.circle(sky_surf, (240, 240, 255), (moon_x, moon_y), radius, 1)
        
    pygame.draw.circle(sky_surf, (255, 255, 240), (moon_x, moon_y), 24)
    return sky_surf

def generate_floor_texture(W, H):
    """
    Генерирует пол ОДИН РАЗ при старте.
    """
    floor_h = H // 2
    floor_surf = pygame.Surface((W, floor_h))
    floor_surf.fill((24, 24, 26)) 
    
    y = 0
    step = 1
    while y < floor_h:
        step = max(2, int(y * 0.15))
        y += step
        if y < floor_h:
            pygame.draw.line(floor_surf, (16, 16, 18), (0, y), (W, y), 1)
            
    center_x = W // 2
    for x in range(-W, W * 2, 60):
        pygame.draw.line(floor_surf, (16, 16, 18), (center_x, 0), (x, floor_h), 2)
        
    return floor_surf

def render_world(sc, px, py, pa, TILE, NUM_RAYS, FOV, PROJ_COEFF, SCALE, W, H, world_map, enemies, player_z, bullets):
    global sky_texture, floor_texture
    
    if sky_texture is None:
        sky_texture = generate_night_sky(W, H)
    if floor_texture is None:
        floor_texture = generate_floor_texture(W, H)

    # === РЕНДЕРИНГ НЕБА ===
    sky_offset = int((pa % (2 * math.pi)) / (2 * math.pi) * (W * 4))
    sc.blit(sky_texture, (-sky_offset, 0))
    if sky_offset > W * 3:
        sc.blit(sky_texture, ((W * 4) - sky_offset, 0))

    # === СВЕРХБЫСТРЫЙ РЕНДЕРИНГ ПОЛА ===
    sc.blit(floor_texture, (0, H // 2))

    z_buffer = [9999.0] * NUM_RAYS
    MAX_DEPTH = 650  

    for ray in range(NUM_RAYS):
        angle = pa - FOV/2 + ray * (FOV / NUM_RAYS)
        sin_a = math.sin(angle) if math.sin(angle) != 0 else 0.0001
        cos_a = math.cos(angle) if math.cos(angle) != 0 else 0.0001

        step_x = 1 if cos_a > 0 else -1
        step_y = 1 if sin_a > 0 else -1

        delta_dist_x = abs(TILE / cos_a)
        delta_dist_y = abs(TILE / sin_a)

        map_x, map_y = int(px // TILE), int(py // TILE)

        if cos_a > 0: side_dist_x = ((map_x + 1) * TILE - px) / cos_a
        else: side_dist_x = (px - map_x * TILE) / abs(cos_a)

        if sin_a > 0: side_dist_y = ((map_y + 1) * TILE - py) / sin_a
        else: side_dist_y = (py - map_y * TILE) / abs(sin_a)

        hit = False
        wall_type = 1
        side = 0  

        for _ in range(32):  
            if side_dist_x < side_dist_y:
                if side_dist_x > MAX_DEPTH: break
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                if side_dist_y > MAX_DEPTH: break
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            wall_pos = (map_x * TILE, map_y * TILE)
            if wall_pos in world_map:
                hit = True
                wall_type = world_map[wall_pos]  
                break

        if hit:
            if side == 0: wall_dist = (map_x * TILE - px + (1 - step_x) * TILE / 2) / cos_a
            else: wall_dist = (map_y * TILE - py + (1 - step_y) * TILE / 2) / sin_a

            corrected_dist = max(0.1, wall_dist * math.cos(pa - angle))
            
            if corrected_dist > MAX_DEPTH:
                continue

            z_buffer[ray] = corrected_dist
            wall_height = int(PROJ_COEFF / corrected_dist)
            
            # === ЦВЕТА СТЕН (ВОССТАНОВЛЕНЫ ПОСЛЕ ПЕРЕВОДА) ===
            if wall_type == 1: base_color = [130, 40, 40]
            elif wall_type == 2: base_color = [70, 80, 90]
            else: base_color = [40, 90, 50]

            if side == 1:
                base_color = [int(c * 0.7) for c in base_color]

            shadow_coeff = 1 / (1 + corrected_dist * corrected_dist * 0.00003)
            color = (
                int(base_color[0] * shadow_coeff),
                int(base_color[1] * shadow_coeff),
                int(base_color[2] * shadow_coeff)
            )

            pygame.draw.rect(sc, color, (ray * SCALE, (H // 2) + int(player_z) - wall_height // 2, SCALE + 2, wall_height))

    for en in enemies:
        if en['alive']:
            vx, vy = en['pos'][0] - px, en['pos'][1] - py
            dist = math.hypot(vx, vy)
            
            if dist > MAX_DEPTH: continue
            
            angle_en = math.atan2(vy, vx)
            diff = (angle_en - pa + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) < FOV:
                ray_idx = int((diff + FOV/2) / (FOV/NUM_RAYS))
                if 0 <= ray_idx < NUM_RAYS:
                    if dist < z_buffer[ray_idx]:
                        h = PROJ_COEFF / (dist + 0.0001)
                        shadow_coeff = 1 / (1 + dist * dist * 0.00002)
                        c = int(255 * shadow_coeff)
                        pygame.draw.circle(sc, (c, 0, 0), (ray_idx * SCALE, (H // 2) + int(player_z)), int(h // 4))

    for b in bullets:
        vx, vy = b['x'] - px, b['y'] - py
        dist = math.hypot(vx, vy)
        
        if dist > MAX_DEPTH: continue
        
        angle_b = math.atan2(vy, vx)
        diff = (angle_b - pa + math.pi) % (2 * math.pi) - math.pi
        
        if abs(diff) < FOV:
            ray_idx = int((diff + FOV/2) / (FOV/NUM_RAYS))
            if 0 <= ray_idx < NUM_RAYS:
                if dist < z_buffer[ray_idx]:
                    h = PROJ_COEFF / (dist + 0.0001)
                    bullet_size = max(2, int(h // 16)) 
                    
                    bullet_x = ray_idx * SCALE - bullet_size // 2
                    bullet_y = H // 2 + int(h // 6) - bullet_size // 2
                    
                    if 'v_offset' in b:
                        bullet_y += int((H // 7) * b['v_offset'])
                    
                    pygame.draw.rect(sc, (255, 255, 255), (bullet_x, bullet_y, bullet_size, bullet_size))
