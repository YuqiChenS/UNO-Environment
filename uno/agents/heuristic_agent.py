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
        hand_colors = [c.split('-')[0] for c in state['hand'] if 'wild' not in c]
        hand_color_counts = Counter(hand_colors)

        opp_idx = self.state['current_player'] + self.state['direction'] if self.state['direction'] != -1 else self.state['num_players'] - 1
        opp_hand_size = self.state['num_cards'][opp_idx]
        # cards in my hand that match action's color
        
        # opponent hand size x is attacking card (skip, wild swap, wild shuffle, draw2, draw4) 

        # round x legal action number x is_draw 

        
        if 'draw' in legal_actions:
            return 'draw'
        return 'keep'

    def score(action, hand_color_counts, opp_hand_size, num_round, len_normal_actions, is_draw):
        action_color, action_trait = action.split('-')[0], action.split('-')[1]
        is_attack = 1 if action_trait in ('skip', 
                                          'reverse',
                                          'draw_2',
                                          'wild_draw_4',
                                          'wild_shuffle',
                                          'wild_swap',
                                          'wild_draw_until') else 0
        
        feature_0 = hand_color_counts[action_color]
        feature_1 = opp_hand_size * is_attack
        feature_2 = (1 / num_round + 1 / len_normal_actions) * is_draw
        return feature_0 + feature_1 + feature_2

