import math
import engine

def handle_attack(shooting_active, shot_timer, weapon_type, hero, enemies, bullets, anim_frame, kills):
    if shooting_active and shot_timer == 0:
        shot_timer = 15
        if weapon_type == 0:  # Пистолет
            # v_offset = 1.0 означает, что пуля стартует снизу из дула
            bullets.append({
                'x': hero.x, 
                'y': hero.y, 
                'angle': hero.angle, 
                'dist': 0,
                'v_offset': 1.0  
            })
        elif weapon_type == 1:  # Катана
            anim_frame = 1
            for en in enemies:
                if en['alive']:
                    vx = en['pos'][0] - hero.x
                    vy = en['pos'][1] - hero.y
                    dist = math.hypot(vx, vy)
                    diff = (math.atan2(vy, vx) - hero.angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(diff) < 0.6 and dist < 150:
                        en['alive'] = False
                        kills += 1
                        
    return shot_timer, anim_frame, kills

def update_bullets(bullets, enemies, world_map, TILE, speed, kills):
    bullet_speed = speed * 3.5  # Слегка ускорим пули для лучшей динамики
    max_bullet_dist = 600
    new_bullets = []
    
    for b in bullets:
        bx = b['x'] + bullet_speed * math.cos(b['angle'])
        by = b['y'] + bullet_speed * math.sin(b['angle'])
        b_dist = b['dist'] + bullet_speed
        
        if not engine.check_wall(bx, by, TILE, world_map) and b_dist < max_bullet_dist:
            b['x'] = bx
            b['y'] = by
            b['dist'] = b_dist
            
            # Плавно уменьшаем офсет, чтобы пуля летела к центру прицела
            if 'v_offset' in b:
                b['v_offset'] = max(0.0, b['v_offset'] - 0.15)
            
            hit_enemy = False
            for en in enemies:
                if en['alive']:
                    if math.hypot(en['pos'][0] - bx, en['pos'][1] - by) < 25:
                        en['alive'] = False
                        kills += 1
                        hit_enemy = True
                        break
            if not hit_enemy:
                new_bullets.append(b)
                
    return new_bullets, kills
