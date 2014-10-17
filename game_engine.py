import sys
from argparse import ArgumentParser, REMAINDER as rem
from importlib import import_module
from random import shuffle

cards = 'D2D3D4D5D6D7D8D9DTDJDQDKDA'
cards += 'C2C3C4C5C6C7C8C9CTCJCQCKCA'
cards += 'H2H3H4H5H6H7H8H9HTHJHQHKHA'
cards += 'S2S3S4S5S6S7S8S9STSJSQSKSA'

def shuffle_deck():
    """Returns a random list of indexes pointing to the positions in the cards deck"""
    deck = [i for i in range(0, 52)]
    shuffle(deck)
    return [cards[c*2:c*2+2] for c in deck]

def deal_cards(agent, param, bet_hist):
    """Calls the deal methods for the agent, with the relevant parameters"""
    return agent.deal(param, bet_hist)

def flop_round(agents, param, bet_hist):
    """Calls the flop methods for the agent, with the relevant parameters"""
    return agent.flop(param, bet_hist)

def turn_round(agents, param, bet_hist):
    """Calls the turn methods for the agent, with the relevant parameters"""
    return agent.turn(param, bet_hist)

def river_round(agents, param, bet_hist):
    """Calls the river methods for the agent, with the relevant parameters"""
    return agent.river(param, bet_hist)

def betting_round(agents, chips, method, params):
    """Simulates the betting round"""
    bet_history = []
    in_play = [True] * len(agents)
    in_play_count = len(agents)
    bet_history = [normalize_bet(method(agent[0], param[0], bet_history))]
    max_bet = max(0, bet_history[0])

    raised_player = 0
    i = (raised_player + 1) % len(agents)

    while i != raised_player and in_play_count > 1:
        if inplay[i]:
            bet = normalize_bet(method(agent[i], param[i], bet_history))
            chips[i] -= bet
            bet_history += [bet]
            
            if bet > max_bet:
                raised_player = i
                max_bet = bet

            if bet == 0:
                in_play[i] = False
                in_play_count -= 1

        i = (i + 1) % len(agents)

    agents_left = []
    chips_left = []
    for i in range(0, len(agents)):
        if in_play[i]:
            agents_left += [agents[i]]
            chips_left += [chips[i]]
            
    return (agents_left, chips_left)

def normalize_bet(chips, bet):
    """Normalize the bet and make sure that the bets are within limits"""
    return bet if bet <= chips and bet >= chips else 0

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
    global_agents = [getattr(import_module('agents.' + a), a.title())(buy_in) for a in args.agents]
    global_chips = [buy_in] * len(global_agents)

    # Set up the current game
    agents = global_agents[:]
    chips = global_chips[:]
    shuffle(agents)
    deck = shuffle_deck()
    pot = 0

    for i in range(0, len(agents)):
        agents[i].new_game(len(agents), i)

    params = [(deck.pop(), deck.pop()) for i in range(0, len(agents))]
    agents, chips = betting_round(agents, chips, deal_cards, params)

    params = [deck.pop(), deck.pop(), deck.pop()] * len(agents)
    agents, chips = betting_round(agents, chips, flop_round, params)

    params = [deck.pop()] * len(agents)
    agents, chips = betting_round(agents, chips, turn_round, params)

    params = [deck.pop()] * len(agents)
    agents, chips = betting_round(agents, chips, river_round, params)

    # Evaluate
