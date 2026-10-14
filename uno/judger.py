
class UnoJudger:

    @staticmethod
    def judge_winner(players):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            (list): The player id of the winner
        '''
        fewest = min(len(player.hand) for player in players)
        return [player.player_id for player in players if len(player.hand) == fewest]
