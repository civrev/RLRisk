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

    @staticmethod
    def get_state(state):
        '''
        gets the state representation from the state
        state = (steal_cards, turn_order, territories, cards, trade_ins)
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        #steal_cards is first
        if steal_cards:
            state_string = "1" #for yes steal cards
        else:
            state_string = "2" #for no do not steal cards

        #the state string starts with turn order after steal_cards setting
        state_string += "".join([str(x) for x in turn_order])+"6"
        
        for key in range(44):
            if key in territories:
                t_owner,troops = territories[key]
                c_owner = cards[key]
                state_string = state_string + str(key)+str(c_owner)+str(t_owner)+str(troops)+"0"
            else:
                #must be wildcard (key 42/43)
                owner = cards[key]
                state_string = state_string + str(key)+str(owner)

        state_string = state_string + str(trade_ins)

        state_string = int(state_string)

        return state_string

    @staticmethod
    def parse_state(state_string, debug=False):
        '''
        gets the state from the state representation string
        set debug=True for debugging 
        '''

        territories = {}
        cards = {}
        trade_ins = 0

        state_string = str(state_string)

        #the first character is the steal_cards setting
        steal_cards = state_string[0]
        if steal_cards == "1":
            steal_cards = True
        elif steal_cards == "2":
            steal_cards = False
        else:
            raise ValueError("Steal cards was " + steal_cards + " instead of \'1\' or \'2\'")

        state_string = state_string[1:]

        #there is a "6" that seperates turn order from the rest of the state
        six_loc = state_string.find("6")
        turn_order = [int(x) for x in state_string[:six_loc] if len(x)!=0]

        if debug:
            print("Turn Order:",turn_order)
        
        state_string = state_string[six_loc+2:]
        
        #deconstruct the state_string (territories and cards)
        for id_num in range(44):
            
            if debug:
                print("DEBUG ID:", id_num, state_string[:10])
                
            if id_num!=0:
                #remove the next id #, the leading 0 is implied
                state_string = state_string[len(str(id_num)):]
                
            if id_num<42:
                #parses the card owner, then territory owner, then troop count
                
                c_owner = state_string[0]
                t_owner = state_string[1]
                
                state_string = state_string[2:] #don't need them anymore

                #there is a slightly complicated way in which troop numbers need to be parsed
                #to avoid errors
                #for example if there were 102 troops in territory 2 then the beginning of the state string
                #may look like 1020200310234 is valid and it may
                #generate errors relying solely on my trailing 0 delimiter
                #NOTE: this does NOT eliminated the problems when parsing the state_string
                #merely reduces the chance of one from occuring

                troops=""

                unsolved = True

                while(unsolved):
                    nid=str(id_num+1)
                    nid_loc=state_string.find("0"+nid)
                    temp_c_owner = int(state_string[nid_loc+1+len(nid)])
                    temp_t_owner = int(state_string[nid_loc+2+len(nid)])
                    temp_non_zero = int(state_string[nid_loc+3+len(nid)])
                
                    if temp_c_owner<8 and temp_t_owner<6 and temp_non_zero!=0 and nid!="42":
                        #if this is true, then it is much more unlikely to have a bad parse
                        troops = troops + state_string[:nid_loc]
                        state_string = state_string[nid_loc+1:]
                        unsolved = False
                        
                    elif nid=="42":
                        #on id_num 41 nid = 42 which is a wild card and must be handed differently
                        if debug:
                            print("Debug ID:",id_num,"C_O:",temp_c_owner,"T_O:",temp_t_owner,"non0:",state_string[:10])
                        if temp_c_owner<8 and temp_t_owner==4 and temp_non_zero==3:
                            troops = troops + state_string[:nid_loc]
                            state_string = state_string[nid_loc+1:]
                            unsolved = False
                    else:
                        #this is the error handling part
                        #when a difficult parsing situation occurs, it's handled here
                        #it will go to the trouble location (what is throwing a false parse)
                        #and go ahead and add that to troops, then tries to parse again
                        if debug:
                            print("Debug ID:",id_num,"C_O:",temp_c_owner,"T_O:",temp_t_owner,"non0:",state_string[:10])
                        troops = troops + state_string[:nid_loc+1]
                        state_string = state_string[nid_loc+1:]

                territories[id_num] = [int(t_owner),int(troops)]
                cards[id_num] = int(c_owner)

            else:
                #must be a wild card (42/43)
                c_owner = int(state_string[0])
                state_string = state_string[1:]
                cards[id_num] = c_owner

        trade_ins=int(state_string) #if it parses correctly, this should be all that remains

        if trade_ins > 1000:
            #trade ins go up to 15 possibilities, generally
            #This is a debugging help feature
            #you'd have to change this is you had a set of trade in vals
            #greater than length 1,000
            print(territories)
            print("*"*50)
            print(cards)
            print("*"*50)
            print(trade_ins)
            raise ValueError('Parsed incorrectly or impossible trade in value for this game')

        return (steal_cards, turn_order, territories, cards, trade_ins) #this is what a state consist of

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
        override this method for subclasses
        '''

        chosen = random.choice(valid)

        return chosen

    def after_attack_troops(self, state, attack_from, attack_to, remaining):
        '''
        for moving troops after a successful attack
        Override for subclasses
        '''
        
        return random.choice((attack_from, attack_to))
