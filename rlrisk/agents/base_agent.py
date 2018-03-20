"""
this is the base agent for playing the
World Domination version of Risk
you can't really play the game with this
see it's sub-classes for actual functionality
"""

import random
import abc

class BaseAgent(object):
    """A base agent for Risk"""

    __metaclass__  = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def choose_trade_in(self, state, trade_vals, set_list, must_trade):
        '''
        this is where the agent chooses what trade in combo to make, if any
        Override this method for subclasses
        '''

        return random.choice(set_list)

    @abc.abstractmethod
    def choose_attack(self, attacks):
        '''
        asks the agent to choose from a list of valid attacks
        Override for subclasses
        '''

        return random.choice(attacks)

    @abc.abstractmethod
    def choose_placement(self, valid, state, troops):
        '''
        returns a single territory ID from a list of valid ids
        Override this method for subclass decisions on troop placement
        '''
        
        chosen = random.choice(valid)

        return chosen

    @abc.abstractmethod
    def choose_initial_territories(self, valid, state):
        '''
        for choosing territories at beginning of game
        when not randomly dealt
        arguments are passed from environment, a list of valid choices
        returns a single territory ID
        override this method for subclasses
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        chosen = random.choice(valid)

        territories[chosen]=[self.player,1]

        state = (steal_cards, turn_order, territories, cards, trade_ins)

        return (chosen, state)
