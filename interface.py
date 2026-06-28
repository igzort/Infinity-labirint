import pygame
import math

def draw_weapon(sc, W, H, weapon_type, shot_timer, anim_frame, bobbing_y):
    by = int(bobbing_y)
    st = int(shot_timer)
    
    if weapon_type == 0:  
        # === ПИСТОЛЕТ СТРОГО ПО ЦЕНТРУ ЭКРАНА (ОПУЩЕН НИЖЕ) ===
        gun_w = 80
        gun_h = 500
        
        gun_x = W // 2 - gun_w // 2
        # Изменили базовую высоту с H-450 на H-350 (опустили ствол ниже на 100 пикселей)
        gun_y = H - 350 + (st * 5) + by
        
        # Вспышка на конце дула теперь опустилась вслед за стволом
        if st > 0:
            flash_x = W // 2
            flash_y = H - 360 + by
            pygame.draw.circle(sc, (255, 255, 0), (flash_x, flash_y), 45)
            pygame.draw.circle(sc, (255, 150, 0), (flash_x, flash_y), 65, 5)
            
        # Отрисовка ствола
        pygame.draw.rect(sc, (50, 50, 50), (gun_x, gun_y, gun_w, gun_h))
        pygame.draw.rect(sc, (75, 75, 75), (gun_x + 5, gun_y, gun_w - 10, 150))
        pygame.draw.rect(sc, (220, 0, 0), (W // 2 - 2, gun_y - 4, 4, 4))
        
    else:  
        # === КАТАНА ===
        if anim_frame > 0:
            if anim_frame <= 3: pygame.draw.line(sc, (200, 200, 200), (W, H//2), (W//2, H//4), 20)
            elif anim_frame <= 6: pygame.draw.line(sc, (220, 220, 220), (W, H), (W//3, H//3), 25)
            elif anim_frame <= 9: pygame.draw.line(sc, (255, 255, 255), (W, H), (W//4, H//2), 30)
            elif anim_frame <= 12: pygame.draw.line(sc, (180, 180, 180), (W, H), (W//5, int(H*0.8)), 20)
        else:
            pygame.draw.line(sc, (150, 150, 150), (W, H + by), (int(W*0.7), int(H*0.6) + by), 15)

def draw_ui(sc, W, H, font, weapon_type, kills, joystick_active, jx, jy):
    is_pc = (jx == 0 and jy == 0)

    if not is_pc:
        pygame.draw.circle(sc, (255, 255, 255), (int(W*0.15), int(H*0.8)), 80, 2)
        if joystick_active:
            pygame.draw.circle(sc, (0, 255, 0), (int(jx), int(jy)), 40)

        fire_x = int(W * 0.85)
        fire_y = int(H * 0.66)
        pygame.draw.circle(sc, (200, 0, 0), (fire_x, fire_y), 70, 4)
        txt_fire = font.render("FIRE", True, (200, 0, 0))
        sc.blit(txt_fire, (fire_x - txt_fire.get_width() // 2, fire_y - txt_fire.get_height() // 2))

        jump_x = int(W * 0.85)
        jump_y = int(H * 0.75)
        pygame.draw.circle(sc, (0, 150, 255), (jump_x, jump_y), 70, 4)
        txt_jump = font.render("JUMP", True, (0, 150, 255))
        sc.blit(txt_jump, (jump_x - txt_jump.get_width() // 2, jump_y - txt_jump.get_height() // 2))
    
    pygame.draw.rect(sc, (100, 0, 0) if weapon_type==0 else (50,50,50), (int(W*0.3), 10, int(W*0.2), 60))
    sc.blit(font.render("GUN", True, "white"), (int(W*0.35), 20))
    pygame.draw.rect(sc, (100, 0, 0) if weapon_type==1 else (50,50,50), (int(W*0.5), 10, int(W*0.2), 60))
    sc.blit(font.render("KATANA", True, "white"), (int(W*0.55), 20))

    sc.blit(font.render(f"KILLS: {kills}", True, "yellow"), (50, 50))
