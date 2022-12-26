from src import Game
from src import LOGGER

if __name__ == '__main__':
    game = Game()
    while True:
        LOGGER = []
        game.update()
        game.play()
