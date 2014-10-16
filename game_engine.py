import sys
from argparse import ArgumentParser
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

def parse_args():
    """Parses the arguments given from the command line"""
    parser = ArgumentParser()
    parser.add_argument('agents', help='List of agents to simulate', nargs='+')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Instantiate all the agent classes
    agents = [getattr(import_module('agents.' + a), a.title())() for a in args.agents]
