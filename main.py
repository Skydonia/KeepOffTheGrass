from src import Game

if __name__ == '__main__':
    width, height = [int(i) for i in input().split()]
    game = Game(width, height)
    while True:
        game.update()
        game.gamer.play()
