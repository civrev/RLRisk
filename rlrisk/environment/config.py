'''
This moduel contains useful functions
for the configuration of the game in either
GUI or headless modes
'''

import random

def get_turn_order(players, order_setting="c"):
    '''
    Generate what order players take their turns

    Produces a list of player order based on a given setting
    and number of players

    Optional Parameters
    -------------------
    order_setting : "c","r", or "i"
        "c" = Clockwise: Actually is clockwise from random first player
        "r" = Highest Roll: Players are assigned turns randomly
        "i" = Input Order: User declares order manually

        "c" by default as per Risk World Domination stadard ruleset

    Returns
    -------
    list : player indices placed sequencially representing the order in which
        they take their turns
    '''
    p_list = list(range(players))
    op_list = list(p_list)

    order = []

    if order_setting.lower() == "c":

        first = random.choice(p_list)
        order = [player if player <= players - 1 else p_list[player-players]
                 for player in range(first, players + first)]

    elif order_setting.lower() == "r":

        for player in range(players):
            chosen = random.choice(p_list)
            p_list.remove(chosen)
            order.append(chosen)

    else:
        prompt = "Enter the order by space seperated intergers example: \"1 2 3\" "
        order = [int(x) - 1 for x in input(prompt).split()]


    if sum([True for p in order if p in op_list]) != players:
        raise ValueError("Error generating player order " + str(order) +
                         " did not match any order of " +
                         str(list(range(players))))

    return order

def standard_trade_gen():
    """Generator for standard ruleset trade in rewards"""
    for num in  [4, 6, 8, 10, 15]:
        yield num
    num = 15
    while True:
        num += 5
        yield num

def by_one_gen():
    """Generator for trade in rewards starting at 3 and increasing by 1"""
    num = 2
    while True:
        num += 1
        yield num

def get_trade_vals(setting="s"):
    '''
    Generate what trade in values are to be used during a game

    Produces a list of player order based on a given setting
    and number of players

    Optional Parameters
    -------------------
    setting : "s", or "1" (letter one)
        "s" = standard ruleset trade in rewards
        "1" = trade in rewards starting at 3 and increasing by 1

        "s" by default as per Risk World Domination stadard ruleset

    Returns
    -------
    generator : Sequence from which to yeild player rewards
    '''

    if setting == "s":
        values = standard_trade_gen()
    elif setting == "1":
        values = by_one_gen()

    return values
