'''
This file contains useful functions
for the configuration of the game in either
GUI or headless modes
'''

import random
from rlrisk.agents import base_agent
from rlrisk.agents import human

def console_players():
    '''
    used to gather user configuration settings for game
    NOTE: this is not needed for the GUI
    '''

    players = int(input("How many players? "))

    if input("Deal territories to players? y/n ")=='y':
        deal=True
    else:
        deal=False

    if input("Take cards upon player defeat? y/n ")=='y':
        steal_cards=True
    else:
        steal_cards=False

    return (players, deal, steal_cards)

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

def console_get_players(players):
    '''
    configure what kind of player each player is and return them in a list
    NOTE: not needed for the GUI
    '''

    agent_list = []

    for player in range(players):

        prompt = ("What kind of player is " + str(player+1) +
                  "\nA human = h\nA BaseAgent = b\nA RL agent = r\nh/b/r: ")
        ans = input(prompt)

        if ans == 'h':
            agent_list.append(human.Human(player))
        elif ans == 'b':
            agent_list.append(base_agent.BaseAgent(player))
        else:
            raise ValueError("No agent of that ID exist yet")

    return agent_list

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
        values = [0,4,6,8,10,15,20,25,30,35,40,45,50,55,60]
    elif choice == "1":
        values = list(range(4,1000))
    else:
        values = [int(x) for x in input("Type values seperated by space: ").split()]

    return values
