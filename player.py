import pygame
import math
import config

TILE = config.tile_size
text_map = config.text_map

def init_game_world():
    world_map = {}
    enemies = []
    
    for j, row in enumerate(text_map):
        for i, char in enumerate(row):
            if char in ('1', '2', '3'): 
                world_map[(i * TILE, j * TILE)] = int(char)
            elif char == 'E':  # Удален баг с символом '2', спавнившим врагов в металле
                enemies.append({'pos': [i * TILE + 30, j * TILE + 30], 'alive': True})
                
    return world_map, enemies

class Player:
    def __init__(self):
        self.x = TILE * 3 + 30
        self.y = TILE * 1 + 30
        self.angle = 0
        self.current_speed = 0
        self.walk_cycle = 0

def update_jump(jump_active, jump_state, player_z, jump_timer):
    """
    Обрабатывает фазы прыжка игрока: взлет, зависание и падение.
    """
    if jump_active and jump_state == "ground":
        jump_state = "up"

    if jump_state == "up":
        player_z += 8
        if player_z >= 180:
            player_z = 180
            jump_state = "hover"
            # Задаем таймер зависания (например, 5 кадров), чтобы он не уходил в минус
            jump_timer = 5 
            
    elif jump_state == "hover":
        jump_timer -= 1
        if jump_timer <= 0:
            jump_state = "down"
            
    elif jump_state == "down":
        player_z -= 6
        if player_z <= 0:
            player_z = 0
            jump_state = "ground"
            
    return jump_state, player_z, jump_timer
