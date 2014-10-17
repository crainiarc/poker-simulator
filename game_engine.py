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

def flop_round(agent, param, bet_hist):
    """Calls the flop methods for the agent, with the relevant parameters"""
    return agent.flop(param, bet_hist)

def turn_round(agent, param, bet_hist):
    """Calls the turn methods for the agent, with the relevant parameters"""
    return agent.turn(param, bet_hist)

def river_round(agent, param, bet_hist):
    """Calls the river methods for the agent, with the relevant parameters"""
    return agent.river(param, bet_hist)

def betting_round(agent, chips, bet_history, method, params):
    """Simulates the betting round"""
    bet_history += [[]]
    in_play = [True] * len(agents)
    in_play_count = len(agents)

    bet_history[-1] = [normalize_bet(chips[0], method(agents[0], params[0], bet_history[-1]), 0)]
    check = True if bet_history[-1][0] == 0 else False
    max_bet = max(0, bet_history[-1][0])

    raised_player = 0
    i = (raised_player + 1) % len(agents)

    while i != raised_player and in_play_count > 1:
        if in_play[i]:
            bet = normalize_bet(chips[i], method(agents[i], params[i], bet_history), max_bet)
            chips[i] -= bet
            bet_history[-1] += [bet]

            if bet > max_bet:
                check = False
                raised_player = i
                max_bet = bet

            if bet == 0 and not check:
                in_play[i] = False
                in_play_count -= 1

        i = (i + 1) % len(agents)

    agents_left = []
    chips_left = []
    for i in range(0, len(agents)):
        if in_play[i] and not check:
            agents_left += [agents[i]]
            chips_left += [chips[i]]

    return (agents_left, chips_left)

def normalize_bet(chips, bet, curr_bet):
    """Normalize the bet and make sure that the bets are within limits"""
    return bet if bet <= chips and bet >= curr_bet else 0

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
    bet_history = []
    pot = 0

    shuffle(agents)
    deck = shuffle_deck()
    for i in range(0, len(agents)):
        agents[i].new_game(len(agents), i)

    hands = [(deck.pop(), deck.pop()) for i in range(0, len(agents))]
    agents, chips = betting_round(agents, chips, bet_history, deal_cards, hands)
    community_cards = []

    params = [(deck.pop(), deck.pop(), deck.pop())] * len(agents)
    community_cards.extend(params[0])
    agents, chips = betting_round(agents, chips, bet_history, flop_round, params)

    params = [deck.pop()] * len(agents)
    community_cards += [params[0]]
    agents, chips = betting_round(agents, chips, bet_history, turn_round, params)

    params = [deck.pop()] * len(agents)
    community_cards += [params[0]]
    agents, chips = betting_round(agents, chips, bet_history, river_round, params)

    # Evaluate
    evaluate_results()
