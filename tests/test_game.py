''' Tests for the UNO game.

TestUnoGame plays full games; TestDrawRule builds exact hands to check the legal actions.

Run from the repo root:  python -m unittest discover tests -v
'''
import random
import unittest

import numpy as np

from uno import Game
from uno.card import UnoCard
from uno.utils import ACTION_LIST, WILD, WILD_DRAW_4

DECK_SIZE = 108
MAX_STEPS = 2000


def new_game(seed, num_players=2, allow_step_back=False):
    game = Game(allow_step_back=allow_step_back, num_players=num_players)
    game.np_random = np.random.RandomState(seed)
    return game


def total_cards(game):
    return (len(game.dealer.deck) + len(game.round.played_cards)
            + sum(len(player.hand) for player in game.players))


def choose_action(state, pick):
    ''' A random card if any can be played, otherwise draw (or keep a drawn card). Drawing whenever
    it is offered can make games run forever, which would test the player instead of the game.
    '''
    cards = [action for action in state['legal_actions'] if action not in ('draw', 'keep')]
    return pick.choice(cards) if cards else state['legal_actions'][-1]


def play_random_game(game, seed):
    ''' Play until the game ends, checking invariants after every step. Returns the number of steps. '''
    pick = random.Random(seed)
    state, player_id = game.init_game()
    for step in range(MAX_STEPS):
        assert total_cards(game) == DECK_SIZE
        assert 0 <= player_id < game.num_players
        assert state['legal_actions'] and set(state['legal_actions']) <= set(ACTION_LIST)
        if game.is_over():
            return step
        state, player_id = game.step(choose_action(state, pick))
    raise AssertionError('game did not finish in {} steps'.format(MAX_STEPS))


def game_with_hand(hand, target, next_draw=None, num_players=2):
    ''' A started game where the current player holds exactly `hand` and must match `target`.
    `next_draw` is put on top of the deck so it is the next card drawn.
    '''
    game = new_game(0, num_players)
    game.init_game()
    game.players[game.round.current_player].hand = hand
    game.round.target = target
    game.round.played_cards = [target]
    if next_draw is not None:
        game.dealer.deck.append(next_draw)  # the deck deals from the end
    return game


def number(color, trait):
    return UnoCard('number', color, trait)


class TestUnoGame(unittest.TestCase):

    def test_random_games_finish(self):
        for seed in range(300):
            num_players = 2 + seed % 3
            with self.subTest(seed=seed, num_players=num_players):
                game = new_game(seed, num_players)
                play_random_game(game, seed)
                winner = game.round.winner
                self.assertEqual(len(winner), 1)
                self.assertEqual(len(game.players[winner[0]].hand), 0)

    def test_target_shows_chosen_wild_color(self):
        for seed in range(50):
            game = new_game(seed)
            pick = random.Random(seed)
            state, _ = game.init_game()
            for _ in range(MAX_STEPS):
                if game.is_over():
                    break
                self.assertEqual(state['target'].split('-')[0], game.round.target.color)
                state, _ = game.step(choose_action(state, pick))

    def test_two_player_payoffs(self):
        game = new_game(0)
        play_random_game(game, 0)
        winner = game.round.winner[0]
        payoffs = game.get_payoffs()
        self.assertEqual(payoffs[winner], 1)
        self.assertEqual(payoffs[1 - winner], -1)

    def test_same_seed_same_game(self):
        def trace(seed):
            game = new_game(seed, 3)
            pick = random.Random(seed)
            state, player_id = game.init_game()
            states = [(player_id, state)]
            for _ in range(MAX_STEPS):
                if game.is_over():
                    break
                state, player_id = game.step(choose_action(state, pick))
                states.append((player_id, state))
            return states
        self.assertEqual(trace(7), trace(7))

    def test_step_back_restores_state(self):
        game = new_game(1, allow_step_back=True)
        pick = random.Random(1)
        state, player_id = game.init_game()
        for _ in range(20):
            if game.is_over():
                break
            before = game.get_state(player_id)
            game.step(choose_action(state, pick))
            self.assertTrue(game.step_back())
            self.assertEqual(game.get_state(player_id), before)
            state, player_id = game.step(choose_action(state, pick))
        self.assertTrue(game.step_back())


class TestDrawRule(unittest.TestCase):
    ''' Draw is always a legal action. Order of the legal actions is not checked. '''

    def test_draw_offered_with_playable_card(self):
        game = game_with_hand([number('r', '5')], target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), ['r-5', 'draw'])

    def test_only_draw_when_nothing_playable(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), ['draw'])

    def test_draw_offered_with_wild(self):
        game = game_with_hand([UnoCard('wild', 'r', 'wild')], target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), WILD + ['draw'])

    def test_wild_draw_4_when_nothing_else_playable(self):
        game = game_with_hand([number('b', '5'), UnoCard('wild', 'r', 'wild_draw_4')],
                              target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), WILD_DRAW_4 + ['draw'])

    def test_no_wild_draw_4_when_hand_matches_target_color(self):
        game = game_with_hand([number('r', '5'), UnoCard('wild', 'r', 'wild_draw_4')],
                              target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), ['r-5', 'draw'])

    def test_wild_draw_4_with_a_trait_match_of_another_color(self):
        game = game_with_hand([number('b', '3'), UnoCard('wild', 'r', 'wild_draw_4')],
                              target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), ['b-3'] + WILD_DRAW_4 + ['draw'])

    def test_wild_draw_4_with_a_wild(self):
        game = game_with_hand([UnoCard('wild', 'r', 'wild'), UnoCard('wild', 'r', 'wild_draw_4')],
                              target=number('r', '3'))
        self.assertCountEqual(game.get_legal_actions(), WILD + WILD_DRAW_4 + ['draw'])

    def test_drawing_an_unplayable_card_keeps_it_and_passes_the_turn(self):
        drawn = number('b', '9')
        game = game_with_hand([number('r', '5')], target=number('r', '3'), next_draw=drawn)
        player_id = game.round.current_player
        game.step('draw')
        self.assertIn(drawn, game.players[player_id].hand)
        self.assertNotEqual(game.round.current_player, player_id)


class TestReverse(unittest.TestCase):

    def test_two_player_reverse_acts_like_skip(self):
        game = game_with_hand([UnoCard('action', 'r', 'reverse'), number('b', '5')], target=number('r', '3'))
        player_id = game.round.current_player
        _, next_player = game.step('r-reverse')
        self.assertEqual(next_player, player_id)

    def test_three_player_reverse_changes_direction(self):
        game = game_with_hand([UnoCard('action', 'r', 'reverse'), number('b', '5')], target=number('r', '3'),
                              num_players=3)
        player_id = game.round.current_player
        direction = game.round.direction
        _, next_player = game.step('r-reverse')
        self.assertEqual(game.round.direction, -direction)
        self.assertEqual(next_player, (player_id - direction) % 3)


class TestPlayOrKeepDrawnCard(unittest.TestCase):
    ''' After drawing a playable card, the same player chooses to play it or keep it. '''

    def test_playable_drawn_card_asks_play_or_keep(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'), next_draw=number('r', '7'))
        player_id = game.round.current_player
        state, next_player = game.step('draw')
        self.assertEqual(next_player, player_id)
        self.assertEqual(state['drawn_card'], 'r-7')
        self.assertCountEqual(state['legal_actions'], ['r-7', 'keep'])

    def test_keep_leaves_card_in_hand_and_passes_turn(self):
        drawn = number('r', '7')
        game = game_with_hand([number('b', '5')], target=number('r', '3'), next_draw=drawn)
        player_id = game.round.current_player
        game.step('draw')
        state, next_player = game.step('keep')
        self.assertIn(drawn, game.players[player_id].hand)
        self.assertNotEqual(next_player, player_id)
        self.assertIsNone(game.round.drawn_card)
        self.assertIn('draw', state['legal_actions'])

    def test_play_drawn_card(self):
        drawn = number('r', '7')
        game = game_with_hand([number('b', '5')], target=number('r', '3'), next_draw=drawn)
        player_id = game.round.current_player
        game.step('draw')
        _, next_player = game.step('r-7')
        self.assertIs(game.round.target, drawn)
        self.assertNotIn(drawn, game.players[player_id].hand)
        self.assertNotEqual(next_player, player_id)

    def test_drawn_skip_skips_next_player(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'),
                              next_draw=UnoCard('action', 'r', 'skip'), num_players=3)
        player_id = game.round.current_player
        direction = game.round.direction
        game.step('draw')
        _, next_player = game.step('r-skip')
        self.assertEqual(next_player, (player_id + 2 * direction) % 3)

    def test_drawn_wild_offers_every_color_and_keep(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'),
                              next_draw=UnoCard('wild', 'r', 'wild'))
        state, _ = game.step('draw')
        self.assertCountEqual(state['legal_actions'], WILD + ['keep'])
        game.step('g-wild')
        self.assertEqual(game.round.target.color, 'g')

    def test_drawn_wild_draw_4_not_playable_when_hand_has_a_match(self):
        drawn = UnoCard('wild', 'r', 'wild_draw_4')
        game = game_with_hand([number('r', '5')], target=number('r', '3'), next_draw=drawn)
        player_id = game.round.current_player
        _, next_player = game.step('draw')
        self.assertIn(drawn, game.players[player_id].hand)
        self.assertNotEqual(next_player, player_id)

    def test_playing_drawn_card_as_last_card_wins(self):
        game = game_with_hand([], target=number('r', '3'), next_draw=number('r', '7'))
        player_id = game.round.current_player
        game.step('draw')
        game.step('r-7')
        self.assertTrue(game.is_over())
        self.assertEqual(game.round.winner, [player_id])

    def test_other_actions_rejected_while_deciding(self):
        game = game_with_hand([number('r', '5')], target=number('r', '3'), next_draw=number('r', '7'))
        game.step('draw')
        for action in ('draw', 'r-5'):
            with self.assertRaises(ValueError):
                game.step(action)


class TestEmptyDeck(unittest.TestCase):

    def test_reshuffle_keeps_target_on_table(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'))
        target = game.round.target
        old_cards = [number('g', '1'), number('g', '2')]
        game.dealer.deck = []
        game.round.played_cards = old_cards + [target]
        game.step('draw')
        self.assertEqual(game.round.played_cards, [target])
        self.assertNotIn(target, game.dealer.deck)
        self.assertTrue(all(card not in game.round.played_cards for card in old_cards))

    def test_draw_with_no_cards_left_passes_turn(self):
        game = game_with_hand([number('b', '5')], target=number('r', '3'))
        player_id = game.round.current_player
        game.dealer.deck = []
        _, next_player = game.step('draw')
        self.assertEqual(len(game.players[player_id].hand), 1)
        self.assertNotEqual(next_player, player_id)

    def test_penalty_deals_only_the_cards_left(self):
        game = game_with_hand([UnoCard('action', 'r', 'draw_2'), number('b', '5')], target=number('r', '3'))
        victim = game.players[game.round._next_player()]
        before = len(victim.hand)
        game.dealer.deck = []
        game.step('r-draw_2')  # only the old target can be reshuffled
        self.assertEqual(len(victim.hand), before + 1)


if __name__ == '__main__':
    unittest.main()
