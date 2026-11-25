''' Play UNO in the terminal against random or rule based agents,
or play 1000 games between agents.

  python play.py                 # you vs 1 opponent
  python play.py --players 4 --opponent rule
  python play.py --eval rule --opponent random
'''
import argparse
import csv
import os

from uno import Game, match
from uno.agents import UnoHumanAgent, UnoRandomAgent, RuleBasedAgent, HeuristicAgent
from uno.utils import ROOT_PATH

PATH = os.path.join(ROOT_PATH, 'results', 'result.csv')
NUM_GAMES = 1000
AGENTS = {'random': UnoRandomAgent, 'rule': RuleBasedAgent, 'heuristic': HeuristicAgent}


def evaluate(eval_class, opponent_class, log):
    for num_players in (2, 3, 4):
        for rules in (False, True):
            wins = 0
            for seed in range(NUM_GAMES):
                eval_player_id = seed % num_players
                agents = [opponent_class(seed * 10 + i) for i in range(num_players)]
                agents[eval_player_id] = eval_class(seed)
                if eval_class is HeuristicAgent and seed % 100 == 0:
                    agents[eval_player_id] = eval_class(seed, log_flag=True)
                result = match(agents, seed=seed, house_rules=rules)
                if result['winner'] == eval_player_id:
                    wins += 1

            win_pct = round(wins / NUM_GAMES, 3)
            if log:
                is_new_file = not os.path.exists(PATH)
                with open(PATH, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if is_new_file:
                        writer.writerow(['self_agent', 'opponent_agent', 'num_agents', 'win_pct', 'house_rule'])
                    writer.writerow([eval_class().name, opponent_class().name, num_players, win_pct, rules])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--players', type=int, default=2, choices=[2, 3, 4])
    parser.add_argument('--house-rules', action='store_true', help='add Wild Shuffle, Swap, Discard and Draw Until cards')
    parser.add_argument('--opponent', default='random', choices=list(AGENTS), help='the agent type of every opponent')
    parser.add_argument('--eval', choices=list(AGENTS), help='play 1000 games for each player count and rule set')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()
    opponent_class = AGENTS[args.opponent]

    if args.eval:
        evaluate(AGENTS[args.eval], opponent_class, args.log)
        return

    agents = [UnoHumanAgent(Game.get_num_actions())] + [opponent_class() for _ in range(args.players - 1)]
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
