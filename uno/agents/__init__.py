''' Agents copied from rlcard 1.2.0.

RandomAgent expects rlcard env-style states (state['legal_actions'] as a dict of action ids),
so it needs an env wrapper around UnoGame. UnoHumanAgent works on UnoGame.get_state directly.
'''
from .human_agent import UnoHumanAgent
from .random_agent import RandomAgent
