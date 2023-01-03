import numpy as np
import pandas as pd


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in Singleton.__instances:
            Singleton.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return Singleton.__instances[cls]


def get_tile_without_isle_affectation_and_scrap_amount(tiles: list):
    return [tile for tile in tiles if tile.isle_id is None and tile.scrap_amount > 0]


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
            distances.append(
                {'tile': nearest_tile, 'target': tile, by: distance, 'unit_gap': nearest_tile.units - tile.units})
    if len(distances) == 0:
        return
    distances = pd.DataFrame(distances).sort_values(by, **kwargs)
    return distances


def get_distance_matrix(from_tiles: list, to_tiles: list):
    matrix = {}
    for i, tile in enumerate(from_tiles):
        for j, to_tile in enumerate(to_tiles):
            if (j, to_tile) not in matrix:
                matrix[(j, to_tile)] = {(i, tile): tile.get_distance(to_tile)}
                continue
            matrix[(j, to_tile)][(i, tile)] = tile.get_distance(to_tile)
    return pd.DataFrame(matrix)


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
        scraps.append({'tile': tile, 'scrap': scrap, 'self': tile.scrap_amount})
    distances = pd.DataFrame(scraps).sort_values('scrap', ascending=False)
    return distances


def is_bot(tile):
    if tile.units > 0:
        return True
    return False


def count_bots_in_grid(grid):
    return sum(grid.apply(is_bot))
