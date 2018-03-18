#risk.py
#Christian Watts

import sys #for testing the size of python objects in memory
import random

from rlrisk.environment import risk, config
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human


def node_test():
    '''test the nodes dictionaries'''

    env = risk.Risk([BaseAgent(x) for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    
    node2name,name2node = env.id_names()

    ids = list(node2name.keys())
    for i_d in ids:
        if i_d != name2node[node2name[i_d]] :
            print("ID",i_d,"is not",name2node[node2name[i_d]])
            return False

    gui = risk.GUI()

    for num in range(42):
        print("Name:",node2name[num],"\tID:",num,"Position",gui.positions[num])

    return True

def parse_test():
    '''
    test the ability to parse state representations
    it also test the amount of memory it takes to
    store the state representation
    '''
    
    test = "Hello World!"
    print(test,sys.getsizeof(test), "bytes")

    env = risk.Risk([BaseAgent(x) for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    steal_cards, turn_order, territories, cards, trade_ins = env.state

    #sets troops to a random number 1-2,000,000 for each territory
    for key in territories:
        territories[key][1]=random.randrange(1,2000000)

    state = (steal_cards, turn_order, territories, cards, trade_ins) #init state
    st_string = env.get_state(state) #turned into string
    state_2 = env.parse_state(st_string, debug=True)

    
    steal_cards2, turn_order2, territories2, cards2, trade_ins2 = state_2
    print(turn_order,turn_order2)
    for t in territories:
        print(territories[t],territories2[t])
    
    st_string_2 = env.get_state(state_2)

    print("State String Size:",sys.getsizeof(st_string),st_string)

    print("State String 2 Size:",sys.getsizeof(st_string_2),st_string_2)


    #this compares state->rep rep->state lossless conversion
    return st_string==st_string_2


def player_test():
    '''
    test player creation of BaseAgent
    '''

    #get some initial environment
    env = risk.Risk([BaseAgent(x) for x in range(6)],
                    [0,1,2,3,4,5],[4,6,8,10,15,20], True)
    steal_cards, turn_order, territories, cards, trade_ins = env.state

    #create agent as player 1
    agent_demo = BaseAgent(0)

    print(agent_demo)
    print("Class Vars (player)",agent_demo.player)

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
            temp_cards[c]=agent_demo.player
        env.state = steal_cards, turn_order, territories, temp_cards, trade_ins
        sets, c_owned  = agent_demo.get_sets(env.state, env.card_faces, debug=True)
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

def assign_territories_test(players=[BaseAgent(x) for x in range(6)], deal=True, order=[0,1,2,3,4,5], trade_vals=[4,6,8,10,15,20], steal_cards=True):
    '''
    testing the assigning of territories done at game start
    Optionally you can pass it the outcome of config_test()
    '''
    env = risk.Risk(players,order,trade_vals, steal_cards)
    env.deal_territories()
    print(env.state)
    

def standard_game_test():
    '''
    testing the standard_game() function in Risk
    that generates a default environment
    '''

    players = [BaseAgent(x) for x in range(6)]

    env = risk.standard_game(players)

    print(env)

def play_game():
    '''plays a standard game'''
    env = risk.standard_game([BaseAgent(x) for x in range(5)]+[Human(5)])

    env.play()



#****************************************************************
if input("Run node test? y/n ").lower() == "y":
    print("Node Test successful?", node_test(),"*"*50,"\n\n")

if input("Run parse test? y/n ").lower() == "y":
    print("Parse Test successful?", parse_test(),"*"*50,"\n\n")
    
if input("Run agent test? y/n ").lower() == "y":
    print("Agent Test successful?", player_test(),"*"*50,"\n\n")
    
config_out = ""
if input("Run game config test? y/n ").lower() == "y":
    config_out = config_test()
    print("Config Test returned", config_out,"*"*50,"\n\n")
    
if input("Run territory assignment test? y/n ").lower() == "y":
    if len(config_out)!=0:
        if input("Test with output of config test? y/n ").lower() == "y":
            assign_territories_test(config_out)
        else:
            assign_territories_test()
    else:
        assign_territories_test()

if input("Run standard game test? y/n ").lower() == "y":
    standard_game_test()

if input("Play standard game? y/n ").lower() == 'y':
    play_game()
