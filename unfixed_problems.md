# Unfixed problems

RLCard 1.2.0 problems that are still in our fork. Numbers match `env_drawbacks.txt`.
Checked against the code on 2026-11-09.

## 1. Payoffs are wrong with 3+ players (3.8)

`UnoGame.get_payoffs` in `uno/game.py`:

```python
self.payoffs[winner[0]] = 1
self.payoffs[1 - winner[0]] = -1
```

`1 - winner` is only "the other player" when there are 2 players. With 3 players:

| Winner | `1 - winner` | Payoffs |
|---|---|---|
| 0 | 1 | `[1, -1, 0]`: player 2 lost but gets 0 |
| 1 | 0 | `[-1, 1, 0]`: player 2 lost but gets 0 |
| 2 | -1, the last player, so the winner | `[0, 0, -1]`: the winner gets -1, nobody gets +1 |

Only one loser is ever penalized. When player 2 wins, its +1 is overwritten by -1.
Two-player games are correct (`test_two_player_payoffs`). `match` doesn't use payoffs,
but any RL training with 3 or 4 players would learn from wrong rewards.

Also, `self.payoffs` is only reset in `init_game`. Calling `get_payoffs` before the game
ends returns all zeros, and a tie (`winner` has two ids) also gives all zeros.

## 2. Official rules that are missing (1.5)

- **No "UNO!" call.** There is no action to call it and no 2-card penalty for forgetting.
- **No Wild Draw 4 challenge.** The player hit by a Draw 4 can't challenge it. Our legal-move
  check already blocks an illegal Draw 4 (`_playable_actions`), so the challenge would only
  matter for bluffing, and our agents can't bluff.
- **No point scoring.** A game ends when one hand is empty, with +1 for the winner. The official
  game scores the cards left in the other hands and plays to 500 points.

## 3. No encoded observation (1.6 / 3.9)

`get_state` returns a dict of strings (`hand`, `target`, `played_cards`, `num_cards`, ...).
It now includes the opponents' hand sizes and the played cards, which RLCard's default
observation left out. But nothing turns the dict into a numeric array that a neural network
agent (DQN, NFSP) could use.

`encode_hand`, `encode_target` and `TRAIT_MAP` in `uno/utils.py` are RLCard's old 4x15
encoding. Nothing in the repo calls them, and they would raise `KeyError` on the four
house-rule wilds, because `TRAIT_MAP` only has the 15 standard traits.

## 4. Wild cards keep their last chosen color (1.3)

Playing a Wild sets `card.color` to the chosen color, and the card keeps that color after it
is reshuffled into the deck or swapped into another hand. The rules check `card.type` and
`card.trait` for wilds, so play is not affected, and `get_state` uses `get_str()`, so the
face-up card is shown correctly.

The trap is any new code that compares colors:
- `card.str` on a Wild shows the color it was created with, not the chosen one.
- `card.color` on a Wild in a hand or in the deck is a leftover color.

`_discard_color` and `_draw_until_color` in `uno/round.py` skip `card.type == 'wild'` because
of this.

## Smaller issues in our own code

- The `get_num_actions` docstring in `uno/game.py` says "60 cards, draw and keep", but the
  method returns 78 (the house-rule wilds added 16 actions).
- `tests/` is listed in `.gitignore`, so the tests are not committed.
