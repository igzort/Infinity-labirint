import pygame
import math

def draw_weapon(sc, W, H, weapon_type, shot_timer, anim_frame, bobbing_y):
    by = int(bobbing_y)
    st = int(shot_timer)
    
    if weapon_type == 0:  
        pygame.draw.rect(sc, (50, 50, 50), (W//2 - 40, H - 450 + (st * 5) + by, 80, 500))
        if st > 10:
            pygame.draw.circle(sc, (255, 255, 0), (W//2, H - 460 + by), 60)
            pygame.draw.circle(sc, (255, 150, 0), (W//2, H - 460 + by), 90, 5)
    else:  
        if anim_frame > 0:
            if anim_frame <= 3: pygame.draw.line(sc, (200, 200, 200), (W, H//2), (W//2, H//4), 20)
            elif anim_frame <= 6: pygame.draw.line(sc, (220, 220, 220), (W, H), (W//3, H//3), 25)
            elif anim_frame <= 9: pygame.draw.line(sc, (255, 255, 255), (W, H), (W//4, H//2), 30)
            elif anim_frame <= 12: pygame.draw.line(sc, (180, 180, 180), (W, H), (W//5, int(H*0.8)), 20)
        else:
            pygame.draw.line(sc, (150, 150, 150), (W, H + by), (int(W*0.7), int(H*0.6) + by), 15)

def draw_ui(sc, W, H, font, weapon_type, kills, joystick_active, jx, jy):
    # Внешний круг джойстика
    pygame.draw.circle(sc, (255, 255, 255), (int(W*0.15), int(H*0.8)), 80, 2)
    
    # Исправлено: Отображение внутренней точки активного джойстика
    if joystick_active:
        pygame.draw.circle(sc, (0, 255, 0), (int(jx), int(jy)), 40)
    
    pygame.draw.rect(sc, (100, 0, 0) if weapon_type==0 else (50,50,50), (int(W*0.3), 10, int(W*0.2), 60))
    sc.blit(font.render("GUN", True, "white"), (int(W*0.35), 20))
    pygame.draw.rect(sc, (100, 0, 0) if weapon_type==1 else (50,50,50), (int(W*0.5), 10, int(W*0.2), 60))
    sc.blit(font.render("KATANA", True, "white"), (int(W*0.55), 20))

    pygame.draw.circle(sc, (200, 0, 0), (int(W*0.85), int(H*0.75)), 100, 5)
    sc.blit(font.render("FIRE", True, "red"), (int(W*0.81), int(H*0.72)))

    sc.blit(font.render(f"KILLS: {kills}", True, "yellow"), (50, 50))
