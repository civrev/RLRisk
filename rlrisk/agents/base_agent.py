"""
this is the base agent for playing the
World Domination version of Risk
you can't really play the game with this
see it's sub-classes for actual functionality
"""

import random

class BaseAgent(object):
    """A base agent for Risk"""

    def __init__(self, player):
        '''must include what player they are in the constructor'''

        self.player=player

    def pick_initial_territories(self, valid, state):
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

    def place_troops(self, state, troops):
        '''
        Place troops into owned territory
        takes in arguments the environment state and how many troops to place
        for each troop it will call choose_placement() with a valid list of
        territories to place troops
        returns the altered state
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        for troop in range(troops):
            
            valid = []
            for t in territories:
                
                if territories[t][0]==self.player:
                    valid.append(t)

            chosen = self.choose_placement(valid, state, troops-troop)
            territories[chosen][1]+=1

        return (steal_cards, turn_order, territories, cards, trade_ins)

    def choose_placement(self, valid, state, troops):
        '''
        returns a single territory ID from a list of valid ids
        Override this method for subclass decisions on troop placement
        '''
        
        chosen = random.choice(valid)

        return chosen

    def recruit_troops(self, state, continents):
        '''
        this calculates and returns the number of troops the player
        recieves at the beginning of their turn not including card sets
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        recruit = 0

        #get the territories this player controls
        t_owned = [t for t in territories if territories[t][0]==self.player]

        #count them
        t_count = len(t_owned)

        #Risk rules then floor divide by 3
        t_count = t_count//3

        #and you always get at least 3 troops from this
        if t_count<3:
            t_count=3

        #now add to amount recruited
        recruit+=t_count

        #calculate for continents
        for continent in continents:
            c_owned=True
            for territory in continents[continent][1:]:
                if territory not in t_owned:
                    c_owned=False

            #if you own the continent, then get the troops
            #allocated for that continent (stored in position 0)
            if c_owned:
                recruit += continents[continent][0]

        return recruit

    def get_sets(self, state, card_faces, debug=False):
        '''
        now you have the total troops recruited from these areas
        but there is still the trade ins to consider
        what this will return is any combination of cards
        the player owns that may be traded in
        valid sets are
        any 3 of same kind
        1 for 1,5,10
        any 2 and a wild
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        c_owned = [c for c in cards if cards[c]==self.player]

        if debug:
            print("DEBUG C_O:", c_owned)

        set_list = []

        one = []
        five = []
        ten = []
        wild = []
        for card in c_owned:
            if card_faces[card] == 1:
                one.append(card)
            elif card_faces[card] == 5:
                five.append(card)
            elif card_faces[card] == 10:
                ten.append(card)
            else:
                wild.append(card)

        if debug:
            print("DEBUG 1s:", one)
            print("DEBUG 5s:", five)
            print("DEBUG 10s:", ten)
            print("DEBUG Wilds:", wild)

        #this calculates 3 of same kind
        if len(one)>=3:
            #in cases such as these there is no need to consider 3+
            #since any 1 is as good as another 1
            #append the first 3, if there are more than 3
            #deal with it else where
            set_list.append(one[:3])
        if len(five)>=3:
            set_list.append(five[:3])
        if len(ten)>=3:
            set_list.append(ten[:3])

        #calculates one of each kind
        if len(one)>=2 and len(five)>=2 and len(ten)>=2:
            #either you have two
            set_list.append([one[0],five[0],ten[0]])
            set_list.append([one[1],five[1],ten[1]])
        elif len(one)>=1 and len(five)>=1 and len(ten)>=1:
            #or you have just one
            set_list.append([one[0],five[0],ten[0]])

        #calculates wildcard sets
        for wc in wild:
            if len(one)>=2:
                #two of ones
                set_list.append([one[0], one[1], wc])
            if len(five)>=2:
                #two of fives
                set_list.append([five[0], five[1], wc])
            if len(ten)>=2:
                #two of tens
                set_list.append([ten[0], ten[1], wc])
            if len(one)!=0 and len(five)!=0:
                #one 1 and one 5
                set_list.append([one[0], five[0], wc])
            if len(one)!=0 and len(ten)!=0:
                #one 1 and one 10
                set_list.append([one[0], ten[0], wc])
            if len(ten)!=0 and len(five)!=0:
                #one 5 and one 10
                set_list.append([ten[0], five[0], wc])

        return (set_list, len(c_owned))

    def trade_in(self, state, trade_vals, set_list, count):
        '''
        trade in which arrangement of cards the agent wants to trade in
        NOTE: according to the rules if you have more than 5 cards you must
        trade in at least one set
        returns the amount of troops recruited
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        if count>=5:
            must_trade=True
        else:
            must_trade=False

        chosen = self.choose_trade_in(state, trade_vals, set_list, must_trade)

        if chosen!=0:

            #set all traded in cards to 7, the 'used' symbol
            for c in chosen:
                cards[c]=7

            #award the player troops equivalent to trade in val
            #if number of trade ins exceeds length of values
            #just award the last one
            if len(trade_vals)<trade_ins:
                return trade_vals[-1]
            else:
                return trade_vals[trade_ins]
            
        #if agent decides not to trade in a set, then no troops will be awarded
        return 0

    def choose_trade_in(self, state, trade_vals, set_list, must_trade):
        '''
        this is where the agent chooses what trade in combo to make, if any
        Override this method for subclasses
        '''

        return random.choice(set_list)
