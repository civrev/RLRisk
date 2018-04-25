"""
This module holds the base agent class
for playing the World Domination version of Risk
all other agents used to play the game
should be sub-classes of this one.
"""

import random

class BaseAgent(object):
    """A base agent for Risk"""

    def __init__(self):
        """Overview of instance variables"""
        self.player = None
        self.trade_vals = None
        self.turn_order = None
        self.steal_cards = None
        self.board = None
        self.defeated = None
        self.continents = None
        self.continent_rewards = None

    def pregame_setup(self, setup_values):
        """
        Provides unchanging state information to the agent

        Called at the beginning of every game, this method
        is used to provide the agent with static information
        regarding the game environment (such as the board,
        troop rewards for card trade ins, turn order for players, etc).

        Also used to reset instance variables used during the
        course of the game.

        Required Parameters
        -------------------
        setup_values : 7 value tuple
            int : The symbol in the game state representing this agent
                ie 0 means this agent is player 1 for the particular game

            generator : The sequence from which rewards for card set trade ins
                are pulled

            list : Order in which players take turns

            boolean : Whether or not cards are stolen upon defeating a player

            dictionary : Adjacentcy lists for territories with ID as key

            dictionary : Continents as keys with a list of possessed territories
                as values

            dictionary : Maps continents to the defined troop rewards per continent

        Returns
        -------
        None

        """
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
        """
        Choose from a set of valid actions given the game state

        Every time this player needs to make a decision (always
        on their turn) this method is called and provided with
        the current state of the game, along with an action code
        and a set of options which are valid. This method must
        return a valid action.

        Required Parameters
        -------------------
        state : 3 value tuple
            (42, 2) Numpy Array : Indexed by territory ID, the first colum
                is player owner, and the second one is the number of troops
                in that territory

            (44,) Numpy Array : The status of all cards in the deck, either
                the player number for ownership by that player or 6 representing
                unowned

            integer : The number or card sets traded in so far

        action_code : integer
            Action Codes represent what part of the game is requesting an action
                0 = placing troops during recruitment
                1 = choosing an attack
                2 = pressing the attack during combat
                3 = choose size of troops to risk during attack
                4 = reinforce from province
                5 = reinforce to province
                6 = distrubte troops during reinforcement
                7 = distrubte troops into conquered territory after attack
                8 = choose which arrangement of cards to trade in
                9 = choose initial territory
                10 = place initial troops
                11 = after attack choose another attack

        options : list
            A list of all valid moves for a given player, for a given action,
            for a given state. Most of the time it is a list of territory IDs,
            but could well be tuples (attack from, attack to), or booleans.

        Returns
        -------
        ? : One of the elements inside the options parameter
        """

        #random action is performed for base agent
        return random.choice(options)
