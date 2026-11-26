'''
A heuristic based agent that picks the action with highest score.
Heuristics 
'''
import random
from collections import Counter
import csv
import os
from uno.utils import ROOT_PATH

ATTACK_TRAITS = ('skip', 'reverse', 'draw_2', 'wild_draw_4', 'wild_shuffle', 'wild_swap', 'wild_draw_until')
PATH = os.path.join(ROOT_PATH, 'results', 'heuristics_v3.csv')

def is_attack_trait(trait, num_players):
    if trait == 'reverse' and num_players > 2:
        return 0
    return 1 if trait in ATTACK_TRAITS else 0


class HeuristicAgent:

    def __init__(self, seed=None, log_flag=False):
        self.rng = random.Random(seed)
        self.name = "Heuristic Agent v3"
        self.log = log_flag

    def step(self, state):
        legal_actions = state['legal_actions']
        card_actions = [a for a in legal_actions if a not in ('draw', 'keep')]
        normal_actions = [a for a in card_actions if 'wild' not in a]
        hand_colors = [c.split('-')[0] for c in state['hand'] if 'wild' not in c]
        hand_color_counts = Counter(hand_colors)
        opp_idx = (state['current_player'] + state['direction']) % state['num_players']
        opp_hand_size = state['num_cards'][opp_idx]
        
        scores = []
        for a in legal_actions:
            score = self.score(a, state, hand_color_counts, opp_hand_size, len(normal_actions))
            scores.append(score)
            if self.log:
                is_new_file = not os.path.exists(PATH)
                with open(PATH, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if is_new_file:
                        writer.writerow(['action', 'target', 'round', 'turn', 'opp_hand_size', 'score'])
                    writer.writerow([a, state['target'], state['num_rounds'], state['num_turns'], opp_hand_size, score])
            
        return legal_actions[scores.index(max(scores))]

    def score(self, action, state, hand_color_counts, opp_hand_size, len_normal_actions):
        hand_size = len(state['hand'])
        num_players = state['num_players']
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
            if action_color != target_color:
                color_left = hand_color_counts[action_color]
                if 'wild' not in action_trait:
                    color_left -= 1
                elif action_trait == 'wild_discard':
                    color_left = 0
                color_gain = color_left - hand_color_counts[target_color]

            card_loss = 1
            if action_trait == 'wild_discard':
                card_loss = 1 + hand_color_counts[action_color]
            elif action_trait == 'wild_swap':
                card_loss = hand_size - opp_hand_size
            elif action_trait == "wild_shuffle":
                card_loss = sum(state['num_cards']) / state['num_players'] - hand_size

            is_attack = is_attack_trait(action_trait, num_players)
            if action_trait == 'skip':
                attack_danger = 1
            elif action_trait == 'draw_2':
                attack_danger = 2
            elif action_trait == 'wild_draw_4':
                attack_danger = 4
            elif action_trait == 'wild_shuffle':
                attack_danger =  sum(state['num_cards']) / state['num_players'] - opp_hand_size
            elif action_trait == 'wild_swap':
                attack_danger = hand_size - opp_hand_size
            elif action_trait == 'wild_draw_until':
                played_count = Counter([i.split('-')[0] for i in state['played_cards'] if i not in ('draw', 'keep')])
                attack_danger = played_count[action_color]
        

            is_wild = 1 if 'wild' in action_trait else 0
            special_card_cost = - len_normal_actions * is_wild

        draw_value = (1 / (len_normal_actions + 1)) * is_draw

        
        if is_keep:
            drawn_trait = state['drawn_card'].split('-')[1]
            if is_attack_trait(drawn_trait, num_players) or 'wild' in drawn_trait:
                card_loss = 0

        return color_gain + card_loss + attack_danger + 3 * special_card_cost + draw_value
