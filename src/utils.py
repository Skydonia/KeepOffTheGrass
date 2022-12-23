import numpy as np


def get_random_tile_from_list(tiles: list):
    i = np.random.randint(len(tiles))
    return tiles[i]


def get_tile_from_list(x, y, tiles: list):
    for tile in tiles:
        if (tile.x, tile.y) == (x, y):
            return tile
    return None
