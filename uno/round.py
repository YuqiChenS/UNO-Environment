from .card import UnoCard
from .utils import cards2list, WILD, WILD_DRAW_4

WILD_TRAITS = ('wild', 'wild_draw_4')
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

    def flip_top_card(self):
        ''' Flip the top card of the card pile

        Returns:
            (object of UnoCard): the top card in game
        '''
        top = self.dealer.flip_top_card()
        if top.trait == 'wild':
            top.color = self.np_random.choice(UnoCard.info['color'])
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
            # player 0 draws 2 but still takes the first turn
            self.dealer.deal_cards(players[self.current_player], 2)

    def proceed_round(self, players, action):
        ''' Apply one action by the current player

        Args:
            players (list): list of UnoPlayer objects
            action (str): string of legal action
        '''
        if action == 'draw':
            self._perform_draw_action(players)
            
            return

        player = players[self.current_player]
        color, trait = action.split('-')
        card = player.hand.pop(self._find_card(player.hand, color, trait))
        if trait in WILD_TRAITS:
            card.color = color
        if not player.hand:
            self.is_over = True
            self.winner = [self.current_player]
        self._play_card(players, card)

    def get_legal_actions(self, players, player_id):
        ''' Cards matching the target's color or trait, plus wilds.
        Wild draw 4 is only legal when nothing else is, and draw only when nothing is playable.
        '''
        target = self.target
        legal_actions = []
        has_wild = False
        has_wild_draw_4 = False
        for card in players[player_id].hand:
            if card.trait == 'wild_draw_4':
                has_wild_draw_4 = True
            elif card.trait == 'wild':
                if not has_wild:
                    has_wild = True
                    legal_actions.extend(WILD)
            elif card.color == target.color or card.trait == target.trait:
                legal_actions.append(card.str)


        if not legal_actions and has_wild_draw_4:
            legal_actions = list(WILD_DRAW_4)
        legal_actions.append('draw')
        return legal_actions

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of UnoPlayer
            player_id (int): The id of the player
        '''
        return {
            'hand': cards2list(players[player_id].hand),
            'target': self.target.get_str(),  # not .str: wild cards change color after creation
            'played_cards': cards2list(self.played_cards),
            'legal_actions': self.get_legal_actions(players, player_id),
            'num_cards': [len(player.hand) for player in players],
        }

    def replace_deck(self):
        ''' Add cards have been played to deck
        '''
        self.dealer.deck.extend(self.played_cards)
        self.dealer.shuffle()
        self.played_cards = []

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

    def _play_card(self, players, card):
        self.played_cards.append(card)
        self.target = card
        if card.type == 'number':
            self._advance()
        else:
            self._perform_non_number_action(players, card)

    def _perform_draw_action(self, players):
        ''' Draw one card. A drawn wild or a card matching the target's color is played immediately;
        anything else goes to the hand. Either way the turn passes.
        '''
        if not self.dealer.deck:
            self.replace_deck()
        card = self.dealer.deck.pop()

        if card.type == 'wild':
            # played as a plain wild with a random color, even if it is a wild_draw_4
            card.color = self.np_random.choice(UnoCard.info['color'])
            self.played_cards.append(card)
            self.target = card
            self._advance()
        elif card.color == self.target.color:
            self._play_card(players, card)
        else:
            players[self.current_player].hand.append(card)
            self._advance()

    def _perform_non_number_action(self, players, card):
        if card.trait == 'reverse':
            self.direction *= -1
        elif card.trait == 'skip':
            self._advance()
        elif card.trait in DRAW_PENALTY:
            num = DRAW_PENALTY[card.trait]
            if len(self.dealer.deck) < num:
                self.replace_deck()
            self.dealer.deal_cards(players[self._next_player()], num)
            self._advance()  # the player who drew loses their turn
        self._advance()
