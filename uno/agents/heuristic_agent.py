'''
A heuristic based agent that picks the action with highest score.
Heuristics 
'''
import random
from collections import Counter

ATTACK_TRAITS = ('skip', 'reverse', 'draw_2', 'wild_draw_4', 'wild_shuffle', 'wild_swap', 'wild_draw_until')


def is_attack_trait(trait, num_players):
    if trait == 'reverse' and num_players > 2:
        return 0
    return 1 if trait in ATTACK_TRAITS else 0


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

        opp_idx = (state['current_player'] + state['direction']) % state['num_players']
        opp_hand_size = state['num_cards'][opp_idx]
        
        scores = []
        for a in legal_actions:
            scores.append(self.score(a, state, hand_color_counts, opp_hand_size, len(normal_actions)))
        return legal_actions[scores.index(max(scores))]

    def score(self, action, state, hand_color_counts, opp_hand_size, len_normal_actions):
        hand_size = len(state['hand'])
        num_players = state['num_players']
        num_rounds = state['num_rounds']
        is_draw = 1 if action == 'draw' else 0
        is_keep = 1 if action == 'keep' else 0

        color_gain = 0
        card_loss = 0
        attack_danger = 0
        special_card_cost = 0

        if is_draw:
            card_loss = -1
        elif not is_keep:
            action_color, action_trait = action.split('-')[0], action.split('-')[1]
            target_color = state['target'].split('-')[0]
            color_gain = hand_color_counts[action_color] - hand_color_counts[target_color]

            card_loss = 1
            if action_trait == 'wild_discard':
                card_loss = 1 + hand_color_counts[action_color]
            elif action_trait == 'wild_swap':
                card_loss = hand_size - opp_hand_size

            is_attack = is_attack_trait(action_trait, num_players)
            attack_danger = is_attack * max(0, hand_size - opp_hand_size)

            is_special = 1 if is_attack or 'wild' in action_trait else 0
            special_card_cost = -is_special / num_rounds

        draw_value = (1 / num_rounds + 1 / (len_normal_actions + 1)) * is_draw

        keep_value = 0
        if is_keep:
            drawn_trait = state['drawn_card'].split('-')[1]
            if is_attack_trait(drawn_trait, num_players) or 'wild' in drawn_trait:
                keep_value = 1

        return color_gain + card_loss + attack_danger + special_card_cost + draw_value + keep_value
