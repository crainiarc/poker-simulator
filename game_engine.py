import sys
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('agents', help='List of agents to simulate', nargs='+')
    args = parser.parse_args()
    agents = args.agents

    print(agents)
