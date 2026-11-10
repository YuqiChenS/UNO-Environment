''' Play UNO in the terminal against random agents.

  python play.py                 # you vs 1 opponent
  python play.py --players 4
'''
import argparse

from uno import Game, match
from uno.agents import UnoHumanAgent, UnoRandomAgent


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--players', type=int, default=2, choices=[2, 3, 4])
    parser.add_argument('--house-rules', action='store_true', help='add Wild Shuffle, Swap, Discard and Draw Until cards')
    args = parser.parse_args()

    agents = [UnoHumanAgent(Game.get_num_actions())] + [UnoRandomAgent() for _ in range(args.players - 1)]
    try:
        while True:
            print('\nYou are player 0.')
            winner = match(agents, verbose=True, house_rules=args.house_rules)['winner']
            print('\nYou win!' if winner == 0 else f'\nPlayer {winner} wins.')
            input('(enter for next game, ctrl-c to quit) ')
    except (KeyboardInterrupt, EOFError):
        print('\nBye.')


if __name__ == '__main__':
    main()
