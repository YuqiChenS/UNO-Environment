from .judger import UnoJudger
from .utils import cards2list, WILD, WILD_DRAW_4, HOUSE_WILD_TRAITS

WILD_TRAITS = ['wild', 'wild_draw_4'] + HOUSE_WILD_TRAITS
DRAW_PENALTY = {'draw_2': 2, 'wild_draw_4': 4}


class UnoRound:

    def __init__(self, dealer, num_players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.np_random = np_random
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False
        self.winner = None
        self.drawn_card = None
        self.choosing_start_color = False

    def flip_top_card(self):
        ''' Flip the top card of the card pile

        Returns:
            (object of UnoCard): the top card in game
        '''
        top = self.dealer.flip_top_card()
        if top.trait == 'wild':
            self.choosing_start_color = True
        self.target = top
        self.played_cards.append(top)
        return top

    def perform_top_card(self, players, top_card):
        ''' Apply the effect of the first flipped card. Player 0 starts.

        Args:
            players (list): list of UnoPlayer objects
            top_card (object): object of UnoCard
        '''
        if top_card.trait == 'skip':
            self._advance()
        elif top_card.trait == 'reverse':
            self.direction = -1
            self._advance()
        elif top_card.trait == 'draw_2':
            self.dealer.deal_cards(players[self.current_player], 2)
            self._advance()

    def proceed_round(self, players, action):
        ''' Apply one action by the current player

        Args:
            players (list): list of UnoPlayer objects
            action (str): string of legal action
        '''
        if self.choosing_start_color: #choosing the starting color if top card is wild
            if action not in WILD:
                raise ValueError('{} is not legal: choose a color for the starting wild'.format(action))
            self.target.color = action.split('-')[0]
            self.choosing_start_color = False
            return

        if self.drawn_card is not None:
            if action not in self.get_legal_actions(players, self.current_player):
                raise ValueError('{} is not legal: the drawn card must be played or kept'.format(action))
            self.drawn_card = None
            if action == 'keep': #drawn card, player chose 'keep'
                self._advance()
                return
        elif action == 'draw': #player chose 'draw'
            self._perform_draw_action(players)
            return

        player = players[self.current_player] # rest 
        color, trait = action.split('-')
        card = player.hand.pop(self._find_card(player.hand, color, trait))
        if trait in WILD_TRAITS:
            card.color = color
        if not player.hand:
            self.is_over = True
            self.winner = [self.current_player]
        self._play_card(players, card)

    def get_legal_actions(self, players, player_id):
        ''' The playable cards in hand plus 'draw'. Right after drawing a playable card,
        only that card and 'keep' are legal.
        '''
        if self.choosing_start_color and player_id == self.current_player:
            return list(WILD)
        playable = self._playable_actions(players[player_id].hand)
        if self.drawn_card is not None and player_id == self.current_player:
            return self._actions_for_card(self.drawn_card, playable) + ['keep']
        return playable + ['draw']

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of UnoPlayer
            player_id (int): The id of the player
        '''
        return {
            'hand': cards2list(players[player_id].hand),
            'target': self.target.get_str(),
            'played_cards': cards2list(self.played_cards),
            'legal_actions': self.get_legal_actions(players, player_id),
            'num_cards': [len(player.hand) for player in players],
            'drawn_card': self.drawn_card.get_str() if self.drawn_card is not None else None,
            'choosing_start_color': self.choosing_start_color,
        }

    def replace_deck(self):
        ''' Shuffle the played cards back into the deck, except the target, which stays on the table
        '''
        self.dealer.deck.extend(card for card in self.played_cards if card is not self.target)
        self.dealer.shuffle()
        self.played_cards = [self.target]

    def _next_player(self):
        return (self.current_player + self.direction) % self.num_players

    def _advance(self):
        self.current_player = self._next_player()

    @staticmethod
    def _find_card(hand, color, trait):
        ''' Index of the card in hand for an action. Wild cards match on trait alone.
        '''
        for index, card in enumerate(hand):
            if card.trait == trait and (trait in WILD_TRAITS or card.color == color):
                return index
        raise ValueError('No card in hand for action {}-{}'.format(color, trait))

    def _playable_actions(self, hand):
        ''' Cards matching the target's color or trait, plus wilds.
        Wild draw 4 is only playable when no card in hand matches the target's color.
        '''
        target = self.target
        actions = []
        has_wild_draw_4 = False
        has_color_match = False
        for card in hand:
            if card.trait == 'wild_draw_4':
                has_wild_draw_4 = True
            elif card.trait in WILD_TRAITS:
                for color in ['r', 'g', 'b', 'y']:
                    action = f'{color}-{card.trait}'
                    if action not in actions:
                        actions.append(action)
            elif card.color == target.color or card.trait == target.trait:
                actions.append(card.str)
                if card.color == target.color:
                    has_color_match = True

        if has_wild_draw_4 and not has_color_match:
            actions.extend(WILD_DRAW_4)
        return actions

    @staticmethod
    def _actions_for_card(card, playable):
        ''' The actions in `playable` that play this card: one per color for a wild, else just the card '''
        if card.trait in WILD_TRAITS:
            return [action for action in playable if action.split('-')[1] == card.trait]
        return [card.str] if card.str in playable else []

    def _play_card(self, players, card):
        self.played_cards.append(card)
        self.target = card
        if card.type == 'number':
            self._advance()
        else:
            self._perform_non_number_action(players, card)

    def _perform_draw_action(self, players):
        ''' Draw one card into the hand. If it is playable, the same player then decides to play
        or keep it. Otherwise the turn passes.
        '''
        if not self.dealer.deck:
            self.replace_deck()
        if not self.dealer.deck:
            self.is_over = True
            self.winner = UnoJudger.judge_winner(players)
            return

        hand = players[self.current_player].hand
        card = self.dealer.deck.pop()
        hand.append(card)
        if self._actions_for_card(card, self._playable_actions(hand)):
            self.drawn_card = card
        else:
            self._advance()

    def _perform_non_number_action(self, players, card):
        if card.trait == 'reverse':
            self.direction *= -1
            if self.num_players == 2:
                self._advance()
        elif card.trait == 'skip':
            self._advance()
        elif card.trait in DRAW_PENALTY:
            num = DRAW_PENALTY[card.trait]
            if len(self.dealer.deck) < num:
                self.replace_deck()
            if len(self.dealer.deck) < num:
                self.is_over = True
                self.winner = UnoJudger.judge_winner(players)
                return
            self.dealer.deal_cards(players[self._next_player()], num)
            self._advance()
        elif card.trait == 'wild_shuffle' and not self.is_over:
            self._shuffle_hands(players)
        elif card.trait == 'wild_swap' and not self.is_over:
            player = players[self.current_player]
            next_player = players[self._next_player()]
            player.hand, next_player.hand = next_player.hand, player.hand
        elif card.trait == 'wild_discard':
            self._discard_color(players[self.current_player], card.color)
        elif card.trait == 'wild_draw_until':
            self._draw_until_color(players, card.color)
            self._advance()
        self._advance()

    def _shuffle_hands(self, players):
        all_cards = []
        for player in players:
            all_cards.extend(player.hand)
            player.hand = []
        self.np_random.shuffle(all_cards)
        player_id = self._next_player()
        for card in all_cards:
            players[player_id].hand.append(card)
            player_id = (player_id + self.direction) % self.num_players

    def _discard_color(self, player, color):
        kept_cards = []
        for card in player.hand:
            if card.type != 'wild' and card.color == color:
                self.played_cards.append(card)
            else:
                kept_cards.append(card)
        player.hand = kept_cards
        if not player.hand:
            self.is_over = True
            self.winner = [self.current_player]

    def _draw_until_color(self, players, color):
        hand = players[self._next_player()].hand
        while True:
            if not self.dealer.deck:
                self.replace_deck()
            if not self.dealer.deck:
                self.is_over = True
                self.winner = UnoJudger.judge_winner(players)
                return
            card = self.dealer.deck.pop()
            hand.append(card)
            if card.type != 'wild' and card.color == color:
                return
