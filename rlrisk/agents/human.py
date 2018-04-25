'''
This module holds a subclass of BaseAgent()
it is the class used when a human
wants to be a player in the game
'''

from rlrisk.agents import BaseAgent

class Human(BaseAgent):
    '''Allows for human users to play Risk RL'''

    def __init__(self):
        """Adds a dictionary to use for prompting user by action code"""

        super(Human, self).__init__()
        self.acodes = {0:'Place 1 Troop during Recruitment\nOptions are territory IDs',
                       1:'Choose an attack to perform (From, To)\nFalse is for no attack',
                       2:'Continue Attack?',
                       3:'How many troops do you want to risk in battle?',
                       4:'Reinforce from what territory?\nFalse is do not fortify',
                       5:'Send reinforcements to what territory?',
                       6:'Where should 1 troop go during reinforcement?',
                       7:'Where should 1 troop move after the attack?',
                       8:'Which arrangement of cards would you like to trade in?',
                       9:'Choose Territories at game start',
                       10:'Place 1 Troop in initial placement',
                       11:'Choose which attack to follow up successful attack with\nFalse for no attack'}

    def take_action(self, state, action_code, options):
        """Enumerates options to user and validates input to choose an option"""

        print(self.acodes[action_code])
        for index, option in enumerate(options):
            print(index, 'is for option', option)
        user_input = input("Choose: ")
        while user_input not in [str(x) for x in range(len(options))]:
            user_input = input('Invalid, choose again: ')

        return options[int(user_input)]
