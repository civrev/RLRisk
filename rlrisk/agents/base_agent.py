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
        pass

    def set_player(self, player):
        '''tell's the agent what player it is'''
        self.player = player

    #--------------------------------------------------
    # Agent specific Methods
    #--------------------------------------------------


    def choose_trade_in(self, state, trade_vals, set_list, must_trade):
        '''
        this is where the agent chooses what trade in combo to make, if any
        Override this method for subclasses
        '''

        return random.choice(set_list)

    def choose_attack(self, state, attacks):
        '''
        asks the agent to choose from a list of valid attacks
        Override for subclasses
        '''

        return random.choice(attacks)

    def continue_attack(self, state, current_attack):
        '''
        returns whether or not (True/False) to continue the attack
        given the current attack and state
        Override for subclasses
        '''

        #90% of the time just continue attack
        if random.random() > 0.9:
            return True
        
        return False

    def choose_attack_size(self, state, options):
        '''
        chooses how many troops to sent to attack
        Override for subclasses
        '''


        #a markov model showed that it's always best to Risk
        #a the maximum you can, so that base agent will
        #just do that
        return options[-1]

    def choose_placement(self, valid, state, troops):
        '''
        returns a single territory ID from a list of valid ids
        Override this method for subclass decisions on troop placement
        '''
        
        chosen = random.choice(valid)

        return chosen

    def choose_initial_territories(self, valid, state):
        '''
        for choosing territories at beginning of game
        when not randomly dealt
        arguments are passed from environment, a list of valid choices
        returns a single territory ID
        Override this method for subclasses
        '''

        chosen = random.choice(valid)

        return chosen

    def after_attack_troops(self, state, attack_from, attack_to, remaining):
        '''
        for moving troops after a successful attack
        Override for subclasses
        '''
        
        return random.choice((attack_from, attack_to))

    def choose_reinforce_from(self, state, options):
        '''
        During reinforcement phase choose where to reinforce from
        Override for subclasses
        '''
        return random.choice(options)

    def choose_reinforce_to(self, state, options):
        '''
        During reinforcement phase choose where to reinforce from
        Override for subclasses
        '''
        return random.choice(options)

    def reinforce(self, state, frm, to, remaining):
        '''
        choose where to distribute troops
        Override for subclasses
        '''
        return random.choice((frm, to))
