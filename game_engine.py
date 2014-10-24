import sys
from argparse import ArgumentParser, REMAINDER as rem
from importlib import import_module
from random import shuffle
from deuces import Card, Evaluator, Deck

cards = '2d3d4d5d6d7d8d9dTdJdQdKdAd'
cards += '2c3c4c5c6c7c8c9cTcJcQcKcAc'
cards += '2h3h4h5h6h7h8h9hThJhQhKhAh'
cards += '2s3s4s5s6s7s8s9sTsJsQsKsAs'

big_blind = 100
small_blind = 50

class GameEngine:
    def __init__(self, agents, buyin):
        self.agents = agents[:]
        shuffle(self.agents);
        self.chips = [buyin] * len(agents)

    def new_game(self):
        """Sets  up a new game for the players"""
        self.bet_history = []
        self.in_game = [True] * len(self.agents)
        self.in_game_count = len(self.agents)
        self.bet_hist = []
        self.pot = big_blind + small_blind
        self.chips[-2] -= big_blind
        self.chips[-1] -= small_blind
        self.all_in = [False] * len(self.agents)

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

    def normalize_bet(self, chips, bet, curr_bet):
        """Normalize the bet and make sure that the bets are within limits"""
        bet = bet if bet <= chips and bet >= curr_bet else 0
        all_in = (bet == chips)
        return (all_in, bet)

    def betting_round(self, method, params):
        """Simulates the betting round"""
        self.bet_history += [[]]
        current_bets = [0] * len(self.agents)
        
        (self.all_in[0], bet) = self.normalize_bet(self.chips[0], method(self.agents[0], params[0]), 0)
        self.in_game[0] = (not self.all_in[0])
        current_bets[0] = bet
        self.chips[0] -= bet
        check = True if bet == 0 else False
        max_bet = max(0, bet)
        self.pot += bet
        self.bet_history[-1] += [bet]

        raised_player = 0
        i = (raised_player + 1) % len(agents)

        while (i != raised_player) and (not self.all_in[i]) and (current_bets[i] <= max_bet):
            if self.in_game[i]:
                (self.all_in[i], bet) = self.normalize_bet(self.chips[i], method(self.agents[i], params[i]), max_bet)
                self.in_game[i] = (not self.all_in[i])
                delta_bet = max(0, bet - current_bets[i])
                current_bets[i] = bet
                self.chips[i] -= delta_bet
                self.pot += delta_bet
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
        self.betting_round(self.deal_cards, self.hands)
        self.community_cards = []
        if self.in_game_count <= 1:
            return

        params = [(self.deck.pop(), self.deck.pop(), self.deck.pop())] * len(self.agents)
        self.community_cards.extend(params[0])
        self.betting_round(self.flop_round, params)
        if self.in_game_count <= 1:
            return

        params = [self.deck.pop()] * len(self.agents)
        self.community_cards += [params[0]]
        self.betting_round(self.turn_round, params)
        if self.in_game_count <= 1:
            return

        params = [self.deck.pop()] * len(self.agents)
        self.community_cards += [params[0]]
        self.betting_round(self.river_round, params)
        if self.in_game_count <= 1:
            return

    def evaluate_hands(self):
        agent_hands = []
        if self.in_game_count > 1:
            evaluator = Evaluator()
            board = []
            scores = []
            hand_types = []

            for c in self.community_cards:
                board.append(Card.new(c))
            for i in range(0, len(self.agents)):
                agent = self.agents[i]
                agent_hand = []

                for c in agent.hand:
                    agent_hand.append(Card.new(c))

                if self.in_game[i]:
                    agent_hands.append(agent.hand)
                    agent_score = evaluator.evaluate(board, agent_hand)
                    agent_hand_type = evaluator.class_to_string(evaluator.get_rank_class(agent_score))
                    scores.append(agent_score)
                    hand_types.append(agent_hand_type)
                else:
                    agent_hands += [None]
                    scores.append(9999999999999)
            
            lowest_rank = scores[0]
            winner = 0
            for i in range(0, len(self.agents)):
                if lowest_rank > scores[i]:
                    lowest_rank = scores[i]
                    winner = i
                    
            return (winner, agent_hands)
        else: # Only 1 remaining player
            winner = 0
            for i in range(0, len(self.agents)):
                if (self.in_game[i]):
                    winner = i
                    break
            return winner, agent_hands
                # print Card.print_pretty_cards(agent_hand)
            # print Card.print_pretty_cards(board)
            # print scores
            # print hand_types

    def perform_end_game(self, winner, hand):
        self.chips[winner] += self.pot
        self.pot = 0
        
        for agent in self.agents:
            agent.end_game(self.bet_history, winner, hand)

def parse_args():
    """Parses the arguments given from the command line"""
    parser = ArgumentParser()
    parser.add_argument('buyin', help='Amount of buyin chips each agent get at the start')
    parser.add_argument('agents', help='List of agents to simulate', nargs=rem)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Instantiate all the agent classes
    buyin = int(args.buyin)
    agents = [getattr(import_module('agents.' + a), a.title())(buyin) for a in args.agents]

    game = GameEngine(agents, buyin)
    game.new_game()
    game.run_game()
    winner, hand = game.evaluate_hands()
    game.perform_end_game(winner, hand)
