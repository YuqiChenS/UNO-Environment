''' Play UNO in the terminal against opponents that pick random legal moves.

  python play.py                 # you vs 1 opponent
  python play.py --players 4
'''
import argparse
import random

from uno import Game
from uno.agents.human_agent import UnoHumanAgent, print_action

HUMAN_ID = 0


def play_game(game, human):
    state, player_id = game.init_game()
    print('\nYou are player {}.'.format(HUMAN_ID))
    while not game.is_over():
        if player_id == HUMAN_ID:
            action = human.step(state)
        else:
            action = random.choice(state['legal_actions'])
            print_action(player_id, action)
        state, player_id = game.step(action)
    winner = game.round.winner[0]
    print('\nYou win!' if winner == HUMAN_ID else '\nPlayer {} wins.'.format(winner))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--players', type=int, default=2, choices=[2, 3, 4])
    args = parser.parse_args()

    game = Game(num_players=args.players)
    human = UnoHumanAgent(game.get_num_actions())
    try:
        while True:
            play_game(game, human)
            input('(enter for next game, ctrl-c to quit) ')
    except (KeyboardInterrupt, EOFError):
        print('\nBye.')


if __name__ == '__main__':
    main()
