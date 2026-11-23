'''
A heuristic based agent that picks the action with highest score.
Heuristics 
'''
import random
from collections import Counter

class HeuristicAgent:

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.name = "Heuristic Agent"

    def step(self, state):
        legal_actions = state['legal_actions']
        card_actions = [a for a in legal_actions if a not in ('draw', 'keep')]
        normal_actions = [a for a in card_actions if 'wild' not in a]
        wild_actions = [a for a in card_actions if 'wild' in a]

        if 'draw' in legal_actions:
            return 'draw'
        return 'keep'