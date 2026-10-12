''' Agents copied from rlcard 1.2.0.

RandomAgent, DQNAgent and NFSPAgent expect rlcard env-style states (state['obs'] and
state['legal_actions'] as a dict of action ids), so they need an env wrapper around UnoGame.
UnoHumanAgent works on UnoGame.get_state directly.
'''
import importlib.util

from .human_agent import UnoHumanAgent
from .random_agent import RandomAgent
'''
# the learning agents need torch; skip them when it isn't installed
if importlib.util.find_spec('torch') is not None:
    from .dqn_agent import DQNAgent
    from .nfsp_agent import NFSPAgent
'''