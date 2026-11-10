''' Play a whole game between agents. '''
import numpy as np

from .game import UnoGame
from .agents.human_agent import print_action


def match(agents, seed=None, max_steps=10_000, verbose=False, house_rules=False):
    ''' Play one game. agents[i] is player i, and each agent's step(state) returns a legal action.

    Returns the winner (None if the game hit max_steps or ended in a tie), the cards left
    in each hand, and every move as (player_id, action).
    '''
    game = UnoGame(num_players=len(agents), house_rules=house_rules)
    if seed is not None:
        game.np_random = np.random.RandomState(seed)
    state, player_id = game.init_game()

    actions = []
    while not game.is_over() and len(actions) < max_steps:
        action = agents[player_id].step(state)
        if action not in state['legal_actions']:
            raise ValueError(f'player {player_id} chose {action!r}, legal actions are {state["legal_actions"]}')
        actions.append((player_id, action))
        if verbose:
            print_action(player_id, action)
        state, player_id = game.step(action)

    winner = None
    if game.is_over() and len(game.round.winner) == 1:
        winner = game.round.winner[0]

    return {
        'winner': winner,
        'num_cards': [len(player.hand) for player in game.players],
        'actions': actions,
    }
