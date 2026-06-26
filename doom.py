import pygame
import math
import sys
import config
import engine
import interface
from player import init_game_world, Player, TILE

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36, bold=True)

world_map, enemies = init_game_world()
hero = Player()

FPS = config.fps
speed = config.player_speed
rot_speed = config.rot_speed
accel, friction = 0.5, 0.2

FOV = math.pi / 3
NUM_RAYS = 120
PROJ_COEFF = 3 * (NUM_RAYS / (2 * math.tan(FOV/2))) * TILE
SCALE = W // NUM_RAYS

weapon_type, anim_frame, shot_timer, kills = 0, 0, 0, 0

jx, jy = 0, 0            
joystick_active = False  
joystick_finger_id = None 
target_speed_val = 0
dr = 0
mouse_click = False

while True:
    sc.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
            mouse_click = True
            fx = int(event.x * W)
            fy = int(event.y * H)

            if event.type == pygame.FINGERMOTION and joystick_active and event.finger_id == joystick_finger_id:
                angle = math.atan2(fy - jy, fx - jx)
                deg = math.degrees(angle) % 360

                if 292.5 <= deg < 337.5:
                    target_speed_val = speed
                    dr = rot_speed
                    hero.walk_cycle += 0.2
                elif 202.5 <= deg < 247.5:
                    target_speed_val = speed
                    dr = -rot_speed
                    hero.walk_cycle += 0.2
                elif 112.5 <= deg < 157.5:
                    target_speed_val = -speed
                    dr = -rot_speed
                    hero.walk_cycle += 0.2
                elif 22.5 <= deg < 67.5:
                    target_speed_val = -speed
                    dr = rot_speed
                    hero.walk_cycle += 0.2
                elif 247.5 <= deg < 292.5:
                    target_speed_val = speed
                    dr = 0
                    hero.walk_cycle += 0.2
                elif 67.5 <= deg < 112.5:
                    target_speed_val = -speed
                    dr = 0
                    hero.walk_cycle += 0.2
                elif 157.5 <= deg < 202.5:
                    target_speed_val = 0
                    dr = -rot_speed
                else:
                    target_speed_val = 0
                    dr = rot_speed

            elif event.type == pygame.FINGERDOWN:
                if fy < H * 0.15:
                    if W * 0.3 < fx < W * 0.5: weapon_type = 0
                    if W * 0.5 < fx < W * 0.7: weapon_type = 1

                elif fx > W * 0.7 and fy > H * 0.5 and shot_timer == 0:
                    shot_timer = 15
                    if weapon_type == 1: anim_frame = 1
                    for en in enemies:
                        if en['alive']:
                            vx, vy = en['pos'][0] - hero.x, en['pos'][1] - hero.y
                            dist = math.hypot(vx, vy)
                            diff = (math.atan2(vy, vx) - hero.angle + math.pi) % (2 * math.pi) - math.pi
                            limit = 600 if weapon_type == 0 else 200
                            if abs(diff) < 0.5 and dist < limit:
                                en['alive'] = False
                                kills += 1

                elif fx <= W * 0.5 and not joystick_active:
                    jx, jy = fx, fy
                    joystick_active = True
                    joystick_finger_id = event.finger_id

        elif event.type == pygame.FINGERUP:
            if joystick_active and event.finger_id == joystick_finger_id:
                mouse_click = False
                joystick_active = False
                joystick_finger_id = None
                target_speed_val = 0
                dr = 0

    # Физика изменения скорости
    if hero.current_speed < target_speed_val: 
        hero.current_speed = min(hero.current_speed + accel, target_speed_val)
    elif hero.current_speed > target_speed_val:
        hero.current_speed = max(hero.current_speed - accel, target_speed_val)
    
    # Плавное торможение при отпущенном джойстике
    if not joystick_active:
        if hero.current_speed > 0: hero.current_speed = max(hero.current_speed - friction, 0)
        elif hero.current_speed < 0: hero.current_speed = min(hero.current_speed + friction, 0)

    dx, dy = hero.current_speed * math.cos(hero.angle), hero.current_speed * math.sin(hero.angle)
    hero.angle += dr
    if not engine.check_wall(hero.x + dx, hero.y, TILE, world_map): hero.x += dx
    if not engine.check_wall(hero.x, hero.y + dy, TILE, world_map): hero.y += dy

    # Рассчитываем динамическое покачивание FOV (вперед-назад) при ходьбе
    # Если персонаж идет, синус будет плавно менять коэффициент проекции
    if hero.current_speed != 0:
        # 0.05 — это сила отдаления/приближения (можно увеличить для жесткого эффекта)
        dynamic_proj = PROJ_COEFF * (1.1 + math.sin(hero.walk_cycle * 1.5) * 0.08)
    else:
        dynamic_proj = PROJ_COEFF

    # Передаем измененный dynamic_proj вместо статичного PROJ_COEFF
    engine.render_world(sc, hero.x, hero.y, hero.angle, TILE, NUM_RAYS, FOV, dynamic_proj, SCALE, W, H, world_map, enemies)
    
    bobbing_y = math.sin(hero.walk_cycle) * 10 if hero.current_speed != 0 else 0
    interface.draw_weapon(sc, W, H, weapon_type, shot_timer, anim_frame, bobbing_y)
    interface.draw_ui(sc, W, H, font, weapon_type, kills, joystick_active, jx, jy)

    if anim_frame > 0:
        anim_frame += 1
        if anim_frame > 12: anim_frame = 0
    if shot_timer > 0: shot_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)
