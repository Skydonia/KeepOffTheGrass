from src import Game

if __name__ == '__main__':
    game = Game()
    while True:
        game.update()
        game.gamer.play(game)
