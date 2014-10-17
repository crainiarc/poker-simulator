import sys
from argparse import ArgumentParser, REMAINDER as rem
from importlib import import_module
from random import shuffle

cards = 'D2D3D4D5D6D7D8D9DTDJDQDKDA'
cards += 'C2C3C4C5C6C7C8C9CTCJCQCKCA'
cards += 'H2H3H4H5H6H7H8H9HTHJHQHKHA'
cards += 'S2S3S4S5S6S7S8S9STSJSQSKSA'

big_blind = 100
small_blind = 50

class GameEngine:
    def __init__(self, agents, buyin):
        self.agents = shuffle(agents);
        self.chips = [buyin] * len(agents)

    def new_game(self):
        self.in_game = [True] * len(self.agents)
        self.in_game_count = len(self.agents)
        self.bet_hist = []
        self.pot = big_blind + small_blind
        self.chips[-2] -= big_blind
        self.chips[-1] -= small_blind

        self.hands = None
        self.community_cards = []

        self.shuffle_deck()

        for i in range(0, len(agents)):
            self.agents[i].new_game(len(agents), i)

    def shuffle_deck(self):
        """Generates a random list of cards deck"""
        deck = [i for i in range(0, 52)]
        shuffle(deck)
        self.deck = [cards[c*2:c*2+2] for c in deck]

    def deal_cards(self, agent, param):
        """Calls the deal methods for the agent, with the relevant parameters"""
        return agent.deal(param, self.bet_hist, self.pot)

    def flop_round(self, agent, param):
        """Calls the flop methods for the agent, with the relevant parameters"""
        return agent.flop(param, self.bet_hist, self.pot)

    def turn_round(self, agent, param):
        """Calls the turn methods for the agent, with the relevant parameters"""
        return agent.turn(param, self.bet_hist, self.pot)

    def river_round(self, agent, param):
        """Calls the river methods for the agent, with the relevant parameters"""
        return agent.river(param, self.bet_hist, self.pot)

    def normalize_bet(chips, bet, curr_bet):
        """Normalize the bet and make sure that the bets are within limits"""
        return bet if bet <= chips and bet >= curr_bet else 0

    def betting_round(self, method, params):
        """Simulates the betting round"""
        self.bet_history += [[]]

        bet = [normalize_bet(chips[0], method(self.agents[0], params[0]), 0)]
        check = True if bet == 0 else False
        max_bet = max(0, bet)
        self.pot -= bet
        self.bet_history[-1] += [bet]

        raised_player = 0
        i = (raised_player + 1) % len(agents)

        while i != raised_player and self.in_game_count > 1:
            if self.in_game[i]:
                bet = normalize_bet(chips[i], method(self.agents[i], params[i]), max_bet)
                chips[i] -= bet
                self.pot -= bet
                self.bet_history[-1] += [bet]

                if bet > max_bet:
                    check = False
                    raised_player = i
                    max_bet = bet

                if bet == 0 and not check:
                    self.in_game[i] = False
                    self.in_game_count -= 1

            i = (i + 1) % len(self.agents)

    def run_game(self):
        self.hands = [(self.deck.pop(), self.deck.pop()) for i in range(0, len(self.agents))]
        betting_round(self.deal_cards, self.hands)
        self.community_cards = []

        params = [(self.deck.pop(), self.deck.pop(), self.deck.pop())] * len(self.agents)
        self.community_cards.extend(params[0])
        betting_round(self.flop_round, params)

        params = [self.deck.pop()] * len(self.agents)
        self.community_cards += [params[0]]
        betting_round(self.turn_round, params)

        params = [self.deck.pop()] * len(self.agents)
        self.community_cards += [params[0]]
        betting_round(self.river_round, params)

    def evaluate_hands(self):
        pass

def parse_args():
    """Parses the arguments given from the command line"""
    parser = ArgumentParser()
    parser.add_argument('buyin', help='Amount of buyin chips each agent get at the start')
    parser.add_argument('agents', help='List of agents to simulate', nargs=rem)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Instantiate all the agent classes
    buy_in = int(args.buyin)
    agents = [getattr(import_module('agents.' + a), a.title())(buy_in) for a in args.agents]

    game = GameEngine(agents, buyin)
    game.new_game()
    game.run_game()
    game.evaluate_hands()
