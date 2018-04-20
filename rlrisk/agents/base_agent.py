"""
this is the base agent for playing the
World Domination version of Risk
you can't really play the game with this
see it's sub-classes for actual functionality
"""

import random

class BaseAgent(object):
    """A base agent for Risk"""

    def __init__(self):
        self.player = None
        self.trade_vals = None
        self.turn_order = None
        self.steal_cards = None
        self.board = None
        self.defeated = None
        self.continents = None
        self.continent_rewards = None

    def pregame_setup(self, setup_values):
        #what player this agent is
        self.player = setup_values[0]

        #the sequence from which card set trade in rewards are given
        self.trade_vals = setup_values[1]

        #the order which players take turns
        self.turn_order = setup_values[2]

        #whether or not you get the cards of another player upon their defeat
        self.steal_cards = setup_values[3]

        #game board for reference
        self.board = setup_values[4]

        #the continents and what provinces are in them
        self.continents = setup_values[5]

        #the troop rewards for owning continents
        self.continent_rewards = setup_values[6]

        #at game start player has not been defeated
        self.defeated = False


    def take_action(self, state, action_code, options):
        '''
        The environment provides the state, and requests an action from the agent

        example of what is inside the state tuple
        territories, cards, trade_ins = state

        Action Codes represent what part of the game is requesting an action
        0 = place_troops_during_recruitment
        1 = choose_attack
        2 = press_the_attack_during_combat
        3 = choose_size_of_troops_to_risk_during_attack
        4 = reinforce_from_province
        5 = reinforce_to_province
        6 = distrubte_troops_during_reinforcement
        7 = distrubte_troops_into_conquered_territory_after_attack
        8 = choose_which_arrangement_of_cards_to_trade_in
        9 = choose_initial_territory
        10 = place_initial_troops
        11 = after_attack_choose_another_attack
        '''

        #random action
        return random.choice(options)
