import numpy as np
import pandas as pd


def get_random_tile_from_list(tiles: list):
    i = np.random.randint(len(tiles))
    return tiles[i]


def get_tile_from_list(x, y, tiles: list):
    for tile in tiles:
        if (tile.x, tile.y) == (x, y):
            return tile
    return None


def get_tile_distances(from_tiles: list, to_tiles: list, by='distance', **kwargs):
    distances = []
    for tile in to_tiles:
        nearest_tile = tile.get_nearest_tile(from_tiles)
        if nearest_tile is not None:
            distance = tile.get_distance(nearest_tile)
            distances.append({'tile': nearest_tile, 'target': tile, by: distance})
    if len(distances) == 0:
        return
    distances = pd.DataFrame(distances).sort_values(by, **kwargs)
    return distances


def get_most_sided_tile_from_list(side: str, tiles: list):
    if side.lower() not in ['left', 'right']:
        raise Exception("side must be 'left' or 'right'")
    x_coordinate = [tile.x for tile in tiles]
    if not x_coordinate:
        return None
    if side.lower() == 'right':
        index = np.argmin(x_coordinate)
        return tiles[index]
    index = np.argmax(x_coordinate)
    return tiles[index]


def get_recycling_scrap_infos(tiles, game):
    scraps = []
    for tile in tiles:
        scrap = tile.scrap_around(game)
        scraps.append({'tile': tile, 'scrap': scrap})
    distances = pd.DataFrame(scraps).sort_values('scrap', ascending=False)
    return distances


def is_bot(tile):
    if tile.units > 0:
        return True
    return False


def count_bots_in_grid(grid):
    return sum(grid.apply(is_bot))
