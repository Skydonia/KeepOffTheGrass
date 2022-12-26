from src import Game
import numpy as np
import mock
import pytest


def get_size_mock(game):
    return 10, 10


def get_state_mock(game):
    scrap_amount = np.random.randint(1, 4)
    owner = np.random.randint(-1, 2)
    units = (0, np.random.randint(4))[np.random.rand() > 0.7]
    recycler = np.random.randint(3)
    can_build = bool(np.random.randint(2))
    can_spawn = bool(np.random.randint(2))
    in_range_of_recycler = bool(np.random.randint(2))
    return scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler


@mock.patch.object(Game, 'get_size', get_size_mock)
def test_game_creation():
    test_game = Game()
    assert test_game.gamer.name == 'Gamer'


@mock.patch.object(Game, 'get_size', get_size_mock)
@mock.patch.object(Game, 'get_state', get_state_mock)
def test_game_update():
    test_game = Game()
    test_game.update()
    assert (len(test_game.gamer.tiles) > 0 or test_game.opponent.tiles > 0 or test_game.neutral_tiles > 0)


@mock.patch.object(Game, 'get_size', get_size_mock)
@mock.patch.object(Game, 'get_state', get_state_mock)
def test_game_getitem():
    test_game = Game()
    test_game.update()
    feedback = test_game[[(1, 2), (3, 8)]]
    unit_feedback = test_game[4, 5]
    assert (unit_feedback.x, unit_feedback.y) == (4, 5)
    assert len(feedback) == 2
    assert (feedback[0].x, feedback[0].y) == (1, 2)
    assert (feedback[1].x, feedback[1].y) == (3, 8)


@mock.patch.object(Game, 'get_size', get_size_mock)
@mock.patch.object(Game, 'get_state', get_state_mock)
def test_play():
    test_game = Game()
    test_game.update()
    assert test_game.gamer.play() == "WAIT"


@mock.patch.object(Game, 'get_size', get_size_mock)
@mock.patch.object(Game, 'get_state', get_state_mock)
def test_recursive():
    test_game = Game()
    test_game.update()
    test_game.setup()
    # isle_size = len(test_game[5, 5].neighborhood(test_game, test_game.tiles, isle_id='test'))
    assert True
