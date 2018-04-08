'''
This program is to demonstrate the RLRisk package
is fully working after installation
'''

from rlrisk.environment import risk
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human

# generate 6 players, one of them human
# players must be initialized with a player #
# ie player 0->5 for 6 players
user = Human()
other_players = [BaseAgent() for x in range(5)]
all_players = [user] + other_players

# create a game of Risk using standard ruleset
# must include a list of players
env = risk.Risk.standard_game(all_players, has_gui=True)

# begin game
# by defualt the game has the GUI set to False
results = env.play()

