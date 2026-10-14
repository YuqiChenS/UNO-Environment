''' A terminal player for UNO. Adapted from rlcard's UNO human agent to read the
state from UnoGame.get_state directly instead of an env's raw_obs.
'''
from ..card import UnoCard

QUIT_COMMANDS = ('q', 'quit', 'exit')


class UnoHumanAgent:
    ''' Shows the state in the terminal and asks the human for an action.
    step returns the action string (e.g. 'r-7', 'b-wild', 'draw'), not an action id.
    '''
    use_raw = True

    def __init__(self, num_actions):
        self.num_actions = num_actions
        self.name = "Human Agent"

    @staticmethod
    def step(state):
        print_state(state)
        legal_actions = state['legal_actions']
        while True:
            try:
                choice = input('>> Choose an action (0-{}, q to quit): '.format(len(legal_actions) - 1))
            except EOFError:
                raise KeyboardInterrupt
            choice = choice.strip().lower()
            if choice in QUIT_COMMANDS:
                raise KeyboardInterrupt
            if choice.isdigit() and int(choice) < len(legal_actions):
                return legal_actions[int(choice)]
            print('Not a legal choice.')

    def eval_step(self, state):
        return self.step(state), {}


def print_action(player_id, action):
    ''' Print one player's move, e.g. ">> Player 1 chooses r-7" '''
    print('>> Player {} chooses '.format(player_id), end='')
    UnoCard.print_cards(action, wild_color=True)
    print()


def print_state(state):
    ''' Print the current player's hand, the card to match, other players' card counts and the legal actions '''
    print('\n=============== Your Hand ===============')
    UnoCard.print_cards(state['hand'])
    print()
    print('=============== Last Card ===============')
    UnoCard.print_cards(state['target'], wild_color=True)
    print()
    if state['drawn_card'] is not None:
        print('You drew ', end='')
        UnoCard.print_cards(state['drawn_card'])
        print(': play it or keep it?')
    print('========== Players Card Number ===========')
    for player_id in range(state['num_players']):
        if player_id != state['current_player']:
            print('Player {} has {} cards.'.format(player_id, state['num_cards'][player_id]))
    print('======== Actions You Can Choose =========')
    for index, action in enumerate(state['legal_actions']):
        print('{}: '.format(index), end='')
        UnoCard.print_cards(action, wild_color=True)
        if index < len(state['legal_actions']) - 1:
            print(', ', end='')
    print('\n')
