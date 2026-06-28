import pygame
import math
import sys
import config
import engine
import interface
import player
import shooting

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36, bold=True)

world_map, enemies = player.init_game_world()
hero = player.Player()

FPS = config.fps
speed = config.player_speed
rot_speed = config.rot_speed
accel, friction = 0.5, 0.2

FOV = math.pi / 3
NUM_RAYS = 120
PROJ_COEFF = 3 * (NUM_RAYS / (2 * math.tan(FOV/2))) * player.TILE
SCALE = W // NUM_RAYS

weapon_type, anim_frame, shot_timer, kills = 0, 0, 0, 0

jx, jy = 0, 0            
joystick_active = False  
joystick_finger_id = None 
target_speed_val = 0
dr = 0
mouse_click = False

bullets = []

player_z = 0
jump_state = "ground"
jump_timer = 0

# Флаги удержания кнопок атаки и прыжка
shooting_active = False
jump_active = False

while True:
    sc.fill((0, 0, 0))

    # === БЛОК УПРАВЛЕНИЯ ДЛЯ ПК (КЛАВИАТУРА) ===
    keys = pygame.key.get_pressed()
    
    if not joystick_active:
        # Ходьба на W / S (Мгновенная остановка при отпускании)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            target_speed_val = speed
            hero.walk_cycle += 0.2
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            target_speed_val = -speed
            hero.walk_cycle += 0.2
        else:
            target_speed_val = 0

        # Повороты камеры на A / D (Мгновенная остановка при отпускании)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dr = -rot_speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dr = rot_speed
        else:
            dr = 0

        # Прыжок на Пробел на ПК
        if keys[pygame.K_SPACE]:
            jump_active = True
        else:
            jump_active = False

        # Стрельба на ENTER на ПК
        if keys[pygame.K_RETURN]:
            shooting_active = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            # Переключение оружия на 1 и 2 на ПК
            elif event.key == pygame.K_1:
                weapon_type = 0
            elif event.key == pygame.K_2:
                weapon_type = 1

        elif event.type == pygame.KEYUP:
            # Сброс стрельбы при отпускании ENTER на ПК
            if event.key == pygame.K_RETURN:
                if not joystick_active:
                    shooting_active = False

        # === МОБИЛЬНОЕ ТАЧ-УПРАВЛЕНИЕ ДЛЯ ANDROID ===
        elif event.type == pygame.FINGERDOWN:
            mouse_click = True
            fx = int(event.x * W)
            fy = int(event.y * H)

            # Выбор оружия (верхняя панель)
            if fy < H * 0.15:
                if W * 0.3 < fx < W * 0.5: weapon_type = 0
                if W * 0.5 < fx < W * 0.7: weapon_type = 1

            # Правая зона экрана (Атака и Прыжок)
            elif fx > W * 0.7 and fy > H * 0.5:
                if fy < H * 0.75:
                    shooting_active = True
                else:
                    jump_active = True

            # Левая зона экрана (Активация джойстика)
            elif fx <= W * 0.5 and not joystick_active:
                jx, jy = fx, fy
                joystick_active = True
                joystick_finger_id = event.finger_id

        elif event.type == pygame.FINGERMOTION:
            fx = int(event.x * W)
            fy = int(event.y * H)

            if joystick_active and event.finger_id == joystick_finger_id:
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

            # Обновление зон скольжения пальца справа
            elif fx > W * 0.7 and fy > H * 0.5:
                shooting_active = (fy < H * 0.75)
                jump_active = (fy >= H * 0.75)
            else:
                if joystick_active:
                    shooting_active = False
                    jump_active = False

        elif event.type == pygame.FINGERUP:
            if joystick_active and event.finger_id == joystick_finger_id:
                mouse_click = False
                joystick_active = False
                joystick_finger_id = None
                target_speed_val = 0
                dr = 0
            else:
                shooting_active = False
                jump_active = False

    # Считываем логику атаки из shooting.py
    shot_timer, anim_frame, kills = shooting.handle_attack(
        shooting_active, shot_timer, weapon_type, hero, enemies, bullets, anim_frame, kills
    )

    # Движение и коллизии пуль
    bullets, kills = shooting.update_bullets(bullets, enemies, world_map, player.TILE, speed, kills)

    # Фазы прыжка из player.py
    jump_state, player_z, jump_timer = player.update_jump(jump_active, jump_state, player_z, jump_timer)

    # Физика инерции перемещения игрока
    if hero.current_speed < target_speed_val: 
        hero.current_speed = min(hero.current_speed + accel, target_speed_val)
    elif hero.current_speed > target_speed_val:
        hero.current_speed = max(hero.current_speed - accel, target_speed_val)
    
    if not joystick_active and target_speed_val == 0:
        if hero.current_speed > 0: hero.current_speed = max(hero.current_speed - friction, 0)
        elif hero.current_speed < 0: hero.current_speed = min(hero.current_speed + friction, 0)

    dx, dy = hero.current_speed * math.cos(hero.angle), hero.current_speed * math.sin(hero.angle)
    hero.angle += dr
    if not engine.check_wall(hero.x + dx, hero.y, player.TILE, world_map): hero.x += dx
    if not engine.check_wall(hero.x, hero.y + dy, player.TILE, world_map): hero.y += dy

    # Расчет покачивания камеры
    if hero.current_speed != 0:
        dynamic_proj = PROJ_COEFF * (1.0 + math.sin(hero.walk_cycle * 2) * 0.05)
    else:
        dynamic_proj = PROJ_COEFF

    # Рендеринг игрового мира, оружия и интерфейса
    engine.render_world(sc, hero.x, hero.y, hero.angle, player.TILE, NUM_RAYS, FOV, dynamic_proj, SCALE, W, H, world_map, enemies, player_z, bullets)
    
    bobbing_y = math.sin(hero.walk_cycle) * 10 if hero.current_speed != 0 else 0
    interface.draw_weapon(sc, W, H, weapon_type, shot_timer, anim_frame, bobbing_y)
    interface.draw_ui(sc, W, H, font, weapon_type, kills, joystick_active, jx, jy)

    # Таймеры анимаций кадров
    if anim_frame > 0:
        anim_frame += 1
        if anim_frame > 12: anim_frame = 0
    if shot_timer > 0: shot_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)
