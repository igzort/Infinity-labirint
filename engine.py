import pygame
import math

def check_wall(x, y, TILE, world_map):
    return (int(x // TILE) * TILE, int(y // TILE) * TILE) in world_map

def render_world(sc, px, py, pa, TILE, NUM_RAYS, FOV, PROJ_COEFF, SCALE, W, H, world_map, enemies):
    pygame.draw.rect(sc, (20, 20, 40), (0, 0, W, H // 2))
    pygame.draw.rect(sc, (40, 40, 40), (0, H // 2, W, H // 2))

    z_buffer = [9999.0] * NUM_RAYS
    
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

        for _ in range(25):  
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
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
            z_buffer[ray] = corrected_dist

            wall_height = int(PROJ_COEFF / corrected_dist)
            
            if wall_type == 1: base_color = [130, 40, 40]
            elif wall_type == 2: base_color = [70, 80, 90]
            else: base_color = [40, 90, 50]

            if side == 1:
                base_color = [int(c * 0.7) for c in base_color]

            shadow_coeff = 1 / (1 + corrected_dist * corrected_dist * 0.00002)
            color = (
                int(base_color[0] * shadow_coeff),
                int(base_color[1] * shadow_coeff),
                int(base_color[2] * shadow_coeff)
            )

            # SCALE + 2 убирает пустые вертикальные швы
            pygame.draw.rect(sc, color, (ray * SCALE, H // 2 - wall_height // 2, SCALE + 2, wall_height))

    for en in enemies:
        if en['alive']:
            # Исправлено обращение к элементам списка координат врага
            vx, vy = en['pos'][0] - px, en['pos'][1] - py
            dist = math.hypot(vx, vy)
            angle_en = math.atan2(vy, vx)
            diff = (angle_en - pa + math.pi) % (2 * math.pi) - math.pi
            if abs(diff) < FOV:
                ray_idx = int((diff + FOV/2) / (FOV/NUM_RAYS))
                if 0 <= ray_idx < NUM_RAYS:
                    if dist < z_buffer[ray_idx]:
                        h = PROJ_COEFF / (dist + 0.0001)
                        c = 255 / (1 + dist * dist * 0.00002)
                        pygame.draw.circle(sc, (int(c), 0, 0), (ray_idx * SCALE, H//2), int(h//4))
