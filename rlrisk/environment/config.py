'''
This file contains useful functions
for the configuration of the game in either
GUI or headless modes
'''

import random

def turn_order(players, clockwise = "", debug=False):
    '''
    user chooses what method to generate turn order

    clockwise arg is for the GUI. The default is ""
    which signals that the user needs to input from console
    
    "c" = Clockwise: Actually is clockwise from random first player
    "r" = Highest Roll: Players are assigned turns randomly
    "i" = Input Order: User declares order manually
    '''
    p_list = list(range(players))
    op_list = list(p_list)
        
    order=[]

    #the GUI will handle setting selections
    #without console input
    if len(clockwise)==0:
        clockwise = input("Clockwise, highest roll, or input order? c/r/i ")
        
    if clockwise.lower()=="c":
            
        first = random.choice(p_list)
        order = [player if player<=players-1 else p_list[player-players] for player in range(first, players+first)]

        if debug:
            print("the first player should be",first)
            
    elif clockwise.lower()=="r":

        for player in range(players):
            chosen = random.choice(p_list)
            p_list.remove(chosen)
            order.append(chosen)
            
    else:

        order = [int(x)-1 for x in input("Enter the order by space seperated intergers example: \"1 2 3\" ").split()]

    if debug:
        print("the order decided was",order)

    if sum([True for p in order if p in op_list])==players:
        if debug:
            return True
    else:
        raise ValueError("Error generating player order " + str(order) +
            " did not match any order of " + str(list(range(players))))
        
    return order

def get_trade_vals(choice = ""):
    '''
    user chooses setting for card set trade in values
    NOTE: not needed for the GUI
    '''

    prompt = ("What do you want card trade in values to be?\n" +
        "Standard 4,6,8,10,15,...,60?\nBy one 4,5,6,etc?\nCustom values?\n" +
        "s/1/c: ")

    if len(choice)==0:
        choice = input(prompt)

    if choice == "s":
        def standard_trade_gen():
            for x in  [4,6,8,10,15]:
                yield x
            num = 15
            while True:
                num+=5
                yield num
        values = standard_trade_gen()
    elif choice == "1":
        values = range(4,10**20)
    else:
        values = [int(x) for x in input("Type values seperated by space: ").split()]

    return values
