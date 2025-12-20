from collections import deque
from pygame import Rect
from src.utils import GameSettings

DIRS = [(1,0), (-1,0), (0,1), (0,-1)]

def bfs_path(map_obj, start_tile, goal_tile):
    """
    map_obj: current map
    start_tile: (tx, ty)
    goal_tile: (gx, gy)
    """

    #teleport tiles
    tp_tiles = set()
    for tp in map_obj.teleporters:
        tx = int(tp.pos.x // GameSettings.TILE_SIZE)
        ty = int(tp.pos.y // GameSettings.TILE_SIZE)
        tp_tiles.add((tx, ty))

    tp_tiles = tp_tiles | {(18, 30)}

    

    queue = deque([start_tile])
    visited = {start_tile: None}

    width = map_obj.tmxdata.width
    height = map_obj.tmxdata.height

    while queue:
        x, y = queue.popleft()

        if (x, y) == goal_tile:
            # reconstruct path
            path = []
            cur = (x, y)
            while cur:
                path.append(cur)
                cur = visited[cur]
            return path[::-1]

        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            next_tile = (nx, ny)

            if not (0 <= nx < width and 0 <= ny < height):
                continue

            if next_tile in visited:
                continue

        
            if next_tile in tp_tiles:
                continue

            # collision check
            px = nx * GameSettings.TILE_SIZE
            py = ny * GameSettings.TILE_SIZE
            rect = Rect(px, py, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

            if not map_obj.check_collision(rect):
                visited[next_tile] = (x, y)
                queue.append(next_tile)

    return None

