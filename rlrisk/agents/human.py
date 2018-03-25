'''
This is a subclass of agent.BaseAgent()
it is the object used when a human
wants to be a player in the game
'''

from rlrisk.agents import base_agent

class Human(base_agent.BaseAgent):
    '''Allows for human users to play Risk RL'''

    def __init__(self):
        '''
        Nothing for now
        '''
        
        pass

    def choose_initial_territories(self, valid, state):
        '''
        User picks a territory from list
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        print("\nValid Territories are",valid)
        chosen = int(input("Choose a territory ID: "))

        while chosen not in valid:
            chosen = int(input("That was invalid. Choose again: "))


        return valid[chosen]

    def choose_placement(self, valid, state, troops):
        '''
        User picks a territory to place troop
        '''

        #show the cards in your hand to user
        self.show_cards(state)

        print("\nYou have",troops,"troops")

        steal_cards, turn_order, territories, cards, trade_ins = state

        valid_dict = {}

        for x in valid:
            valid_dict[x] = territories[x]
        
        print("Your territories plus troop values")
        [print(i,': (id, troops)',x,',',valid_dict[x][1]) for i,x in enumerate(valid)]
        chosen = int(input("Choose a territory to place 1 troop: "))

        while chosen not in list(range(len(valid))):
            chosen = int(input("That was invalid. Choose again: "))

        return valid[chosen]

    def choose_trade_in(self, state, trade_vals, set_list, must_trade):
        '''
        User chooses what card set to trade in, if any
        '''

        print("Valid card sets are:")
        for i,s in enumerate(set_list):
            print(i,"is set",s)
        chosen = int(input("Chose a set: "))

        while chosen>len(set_list)-1:
            chosen = int(input("Invalid, chose again: "))

        return set_list[chosen]

    def choose_attack(self, state, attacks):
        '''
        User chooses a province to attack from a list of valid attacks
        '''

        print("Valid attacks are:")
        for i,s in enumerate(attacks):
            if s!=False:
                print(i,"is from",s[0],"attack",s[1])
            else:
                print(i,'for choosing not to attack')
        chosen = int(input("Chose an attack: "))

        while chosen>len(attacks)-1:
            chosen = int(input("Invalid, chose again: "))

        return attacks[chosen]

    def continue_attack(self, state, current_attack):
        '''
        Asks is the user wants to continue an attack
        '''

        steal_cards, turn_order, territories, cards, trade_ins = state

        a = territories[current_attack[0]]
        d = territories[current_attack[1]]

        print("Attack overview:\nYour", a[1], "against their",d[1])
        
        user_input = ""
        
        while not (user_input=="y" or user_input=="n"):

            user_input = input("Continue your attack? y/n: ")

        return {'y':True, 'n':False}[user_input]
            

    def choose_attack_size(self, state, options):
        '''
        Asks the user how many troops they want to risk in the attack
        '''

        print("How many troops do you want to risk?:")
        for i,s in enumerate(options):
            print(i,"is risking",s,'troops')
        chosen = int(input("Chose an amount: "))

        while chosen>len(options)-1:
            chosen = int(input("Invalid, chose again: "))

        return options[chosen]

    def after_attack_troops(self, state, attack_from, attack_to, remaining):
        '''
        Ask the user where to move troops after an attack
        '''

        print('You have',remaining,'troops to distribute\n')
        print('0: for province',attack_from)
        print('1: for province',attack_to)

        user_input=''

        while not (user_input=="0" or user_input=="1"):

            user_input = input("Choose where 1 troop goes: ")
        
        return {'0':attack_from,'1':attack_to}[user_input]

    def show_cards(self, state):
        '''displays all cards owned by player'''
        
        steal_cards, turn_order, territories, cards, trade_ins = state

        #player variable get's assigned via set_player() during environment
        #init()
        c_owned = [c for c in cards if cards[c]==self.player]

        print()
        [print('you own card', cards[c]) for c in c_owned]

        if len(c_owned)==0:
            print('you don\'t have any cards')

    

    
