"""
this is the base agent for playing the
World Domination version of Risk
you can't really play the game with this
see it's sub-classes for actual functionality
"""

import random

class BaseAgent:
    """A base agent for Risk"""

    def __init__(self):
        self.defeated = False

    def pregame_setup(self, player, trade_vals, turn_order, steal_cards):
        '''
        Static information for the agent's reference that
        are instatiated at the start of every game
        '''
        #what player this agent is
        self.player = player
        #the sequence from which card set trade in rewards are given
        self.trade_vals = trade_vals
        #the order which players take turns
        self.turn_order = turn_order
        #whether or not you get the cards of another player upon their defeat
        self.steal_cards = steal_cards

    def take_action(self, state, action_code, options):
        '''The environment provides the state, and requests an action from the agent'''

        #example of what is inside the state tuple
        territories, cards, trade_ins = state

        '''
        Action Codes represent what part of the game is requesting an action
        0 = place_troops_during_recruitment
        1 = choose_attack
        2 = press_the attack_during_combat
        3 = choose_size_of_troops_to_risk_during_attack
        4 = reinforce_from_province
        5 = reinforce_to_province
        6 = distrubte_troops_during_reinforcement
        7 = distrubte_troops_into_conquered_territory_after_attack
        8 = choose_which_arrangement_of_cards_to_trade_in
        9 = choose_initial_territory
        '''
        #always risk maximum troops during attack
        if action_code == 3:
            return options[-1]

        #never retreat        
        if action_code == 2:
            return True

        #typical random action
        return random.choice(options)
