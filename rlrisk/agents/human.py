'''
This is a subclass of agent.BaseAgent()
it is the object used when a human
wants to be a player in the game
'''

from rlrisk.agents import base_agent

class Human(base_agent.BaseAgent):
    '''Allows for human users to play Risk RL'''

    def __init__(self, player, gui=False):
        '''
        Needs to be initialized with what player you are
        and whether or not you are running the gui
        '''
        
        self.player = player
        self.gui = gui
        self.gui_promt = 0 #for communicating with the GUI

    def pick_initial_territories(self, valid, state):
        '''
        User picks a territory from list
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        if not self.gui:
            print("\nValid Territories are",valid)
            chosen = int(input("Choose a territory ID: "))

            while chosen not in valid:
                chosen = int(input("That was invalid. Choose again: "))
        else:
            chosen = self.gui_prompt

        territories[chosen]=[self.player,1]

        state = (steal_cards, turn_order, territories, cards, trade_ins)

        return (chosen, state)

    def choose_placement(self, valid, state, troops):
        '''
        User picks a territory to place troop
        '''

        print("\nYou have",troops,"troops")

        steal_cards, turn_order, territories, cards, trade_ins = state

        valid_dict = {}

        for x in valid:
            valid_dict[x] = territories[x]
        
        if not self.gui:
            print("Your territories plus troop values")
            [print(x,":",valid_dict[x]) for x in valid] 
            chosen = int(input("Choose a territory ID: "))

            while chosen not in valid:
                chosen = int(input("That was invalid. Choose again: "))
        else:
            chosen = self.gui_prompt

        return chosen

    def choose_trade_in(self, state, trade_vals, set_list, must_trade):
        '''
        User chooses what card set to trade in, if any
        '''

        if not self.gui:
            print("Valid card sets are:")
            for i,s in enumerate(set_list):
                print(i,"is set",s)
            chosen = int(input("Chose a set: "))

            while chosen>len(set_list-1):
                chosen = int(input("Invalid, chose again: "))
                
        else:
            chosen = self.gui_prompt

        return chosen

    
