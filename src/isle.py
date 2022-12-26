class Isle:
    def __init__(self, isle_id, tiles):
        self.id = isle_id
        self.tiles = tiles

    def __len__(self):
        return len(self.tiles)
