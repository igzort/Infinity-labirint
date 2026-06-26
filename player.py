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
        self.x = TILE + 30
        self.y = TILE + 30
        self.angle = 0
        self.current_speed = 0
        self.walk_cycle = 0
