#risk.py
#Christian Watts

import sys #for testing the size of python objects in memory
import random
import os
import pygame

from rlrisk.environment import  config, gui
from rlrisk.environment.risk import Risk
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human


def node_test():
    '''test the nodes dictionaries'''

    env = Risk([BaseAgent() for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    
    node2name,name2node = env.id_names()

    ids = list(node2name.keys())
    for i_d in ids:
        if i_d != name2node[node2name[i_d]] :
            print("ID",i_d,"is not",name2node[node2name[i_d]])
            return False

    graphics = gui.GUI()

    for num in range(42):
        print("Name:",node2name[num],"\tID:",num,"Position",graphics.positions[num])

    graphics.quit_game()

    return True

def event_test():
    '''
    test the gui response to events
    '''
    graphics = gui.GUI(os.getcwd()+"/rlrisk/environment/")

    input("Use KEYDOWN then press enter")
    event = graphics.loop_event(pygame.KEYDOWN)
    if event!=None and pygame.KEYDOWN == event.type:
        print("Event search was a success!")
    else:
        print("Event search was a failure")

    input("Click EXIT, the press enter")

    event = graphics.loop_event(pygame.KEYDOWN)

    if event:
        print("Exit was a success! Event Log cleanup was a success!")
    else:
        print("Exit or Event Log cleanup was a failure!")

def gui_test():
    '''testing gui painting territories by player and troop count'''

    players = [BaseAgent() for x in range(6)]

    env = Risk.standard_game(players)

    graphics = gui.GUI(os.getcwd()+"/rlrisk/environment/")

    graphics.recolor(env.state)
    
    input("Click EXIT, the press enter")
    event = graphics.loop_event(pygame.KEYDOWN)

def attack_phase_test():
    '''test the parts of the attack phase for the base agent'''

    #generate environment
    players = [BaseAgent() for x in range(6)]

    env = Risk.standard_game(players)

    #unpack initial state
    steal_cards, turn_order, territories, cards, trade_ins = env.state

    #change troops to random values
    for key in territories:
        territories[key][1]=random.randrange(1,50)

    #repack changed state
    env.state = (steal_cards, turn_order, territories, cards, trade_ins)

    #get a player
    p = players[0]

    #compare valid targets for validity
    print("Owned---------------------------------------")
    [print(x,territories[x]) for x in env.get_owned_territories(0)]
    print("Board --------------------------------------")
    [print(t,v) for t,v in env.board.items()]
    print("Valid Attacks ------------------------------")
    [print(x) for x in env.get_targets(0)]

    

def parse_test():
    '''
    test the ability to parse state representations
    it also test the amount of memory it takes to
    store the state representation
    '''
    
    test = "Hello World!"
    print(test,sys.getsizeof(test), "bytes")

    env = Risk([BaseAgent() for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    steal_cards, turn_order, territories, cards, trade_ins = env.state

    #sets troops to a random number 1-2,000,000 for each territory
    for key in territories:
        territories[key][1]=random.randrange(1,2000000)

    state = (steal_cards, turn_order, territories, cards, trade_ins) #init state
    st_string = Risk.get_state(state) #turned into string
    state_2 = Risk.parse_state(st_string, debug=True)

    
    steal_cards2, turn_order2, territories2, cards2, trade_ins2 = state_2
    print(turn_order,turn_order2)
    for t in territories:
        print(territories[t],territories2[t])
    
    st_string_2 = Risk.get_state(state_2)

    print("State String  1 Size:",sys.getsizeof(st_string),st_string)

    print("State String 2 Size:",sys.getsizeof(st_string_2),st_string_2)

    print("Test passed?",st_string==st_string_2)


    #this compares state->rep rep->state lossless conversion
    return st_string==st_string_2


def player_test():
    '''
    test player creation of BaseAgent
    '''

    #get some initial environment
    env = Risk([BaseAgent() for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    steal_cards, turn_order, territories, cards, trade_ins = env.state

    #create agent as player 1
    agent_demo = BaseAgent()

    print(agent_demo)

    #test sets
    #([cards owned],[correct sets])
    #2 (1,5,10)s
    test_sets = [
        ([0,1,2,3,4,5],[[0,2,1],[3,4,5]]),
        ([0,1,2,3,4,43], [[0, 2, 1], [0, 3, 43], [2, 4, 43], [0, 2, 43], [0, 1, 43], [1, 2, 43]]),
        ([0,1,3,4,6],[[0,3,6],[0,4,1]])]

    test_success = True
    for s in test_sets:
        data,ans = s
        print("data:",data)
        temp_cards = dict(cards)
        for c in data:
            temp_cards[c]=0 #let's say our agent is player 0
        env.state = steal_cards, turn_order, territories, temp_cards, trade_ins
        sets, c_owned  = env.get_sets(0, debug=True)
        env.state = steal_cards, turn_order, territories, cards, trade_ins

        print("Sets detected:",sets)
        print("Sets supposed:",ans)
        
        for i,s in enumerate(sets):
            ts = ans[i]
            #print(s)
            #print(ts)
            for i2,e in enumerate(s):
                if e!=ts[i2]:
                    test_success=False
    return test_success

def config_test():
    '''testing the game config'''

    players, deal, steal_cards = config.console_players()
    order = config.turn_order(players, debug=True)
    trade_vals = config.get_trade_vals()


    return players, deal, order, trade_vals, steal_cards

def assign_territories_test(players=[BaseAgent() for x in range(6)], deal=True, order=[0,1,2,3,4,5], trade_vals=[4,6,8,10,15,20], steal_cards=True):
    '''
    testing the assigning of territories done at game start
    Optionally you can pass it the outcome of config_test()
    '''
    env = Risk(players,order,trade_vals, steal_cards)
    env.deal_territories()
    print(env.state)
    

def standard_game_test():
    '''
    testing the standard_game() function in Risk
    that generates a default environment
    '''

    players = [BaseAgent() for x in range(6)]

    env = Risk.standard_game(players)

    print(env)

def play_game():
    '''plays a standard game'''
    env = Risk.standard_game([BaseAgent() for x in range(5)]+[Human()])

    env.play()

def play_game_with_gui():
    '''plays a standard game'''
    env = Risk.standard_game([BaseAgent() for x in range(5)]+[Human()], True)

    env.play()

def cpu_play_game():
    '''Base Agents only play standard game'''
    Risk.standard_game([BaseAgent() for x in range(6)]).play()

def cpu_play_game_with_gui():
    '''Base Agents only play standard game'''
    Risk.standard_game([BaseAgent() for x in range(6)], True).play()



#****************************************************************
menu = {
    "01) node test":node_test,
    "02) parse test":parse_test,
    "03) agent test":player_test,
    "04) game config test":config_test,
    "05) territory assignment test":assign_territories_test,
    "06) standard game test":standard_game_test,
    "07) play standard game":play_game,
    "08) event test":event_test,
    "09) gui test":gui_test,
    "10) attack phase test": attack_phase_test,
    "11) Computer plays standard game":cpu_play_game,
    "12) Computer play, with GUI":cpu_play_game_with_gui,
    "13) User play, with GUI":play_game_with_gui}

stop = False
while not stop:
    [print(x) for x in sorted(list(menu.keys()))]
    user=0
    try:
        user=int(input("Make a selection: "))
    except:
        print("you MUST input a number")
    if user in range(1,len(menu)+1):
        menu[sorted(list(menu.keys()))[user-1]]()
    elif user==0:
        continue
    else:
        stop=True
