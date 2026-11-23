'''
A rule based agent that strictly acts following rule. Play the most plentiful color of card. Use wild cards if only no playable normal cards exist.
Play the wild card and set color to most plentiful color
'''
import random
from collections import Counter

class RuleBasedAgent:

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.name = "Rule Based Agent"

    def step(self, state):
        legal_actions = state['legal_actions']
        card_actions = [a for a in legal_actions if a not in ('draw', 'keep')]
        normal_actions = [a for a in card_actions if 'wild' not in a]
        wild_actions = [a for a in card_actions if 'wild' in a]

        hand_colors = [c.split('-')[0] for c in state['hand'] if 'wild' not in c]
        hand_color_counts = Counter(hand_colors)
        colors_sorted = [c for c, _ in hand_color_counts.most_common()]

        for c in colors_sorted:
            actions_in_color = [a for a in normal_actions if a.split('-')[0] == c]
            if actions_in_color:
                return self.rng.choice(actions_in_color)

        if wild_actions:
            if not colors_sorted:
                return self.rng.choice(wild_actions)
            best_color = colors_sorted[0]
            wilds_best_color = [a for a in wild_actions if a.split('-')[0] == best_color]
            return self.rng.choice(wilds_best_color)

        if 'draw' in legal_actions:
            return 'draw'