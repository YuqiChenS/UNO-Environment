''' UnoHumanAgent and UnoRandomAgent work with uno.match.
RandomAgent is rlcard's, unchanged; it needs an rlcard-style env, so it can't play through match.
'''
from .human_agent import UnoHumanAgent
from .random_agent import RandomAgent, UnoRandomAgent
