'''
This is a subclass of agent.BaseAgent()
it is the object used when a human
wants to be a player in the game
'''

from rlrisk.agents.base_agent import BaseAgent

class Human(BaseAgent):
    '''Allows for human users to play Risk RL'''

    def __init__(self):
        prompts=['Place 1 Troop during Recruitment\nOptions are territory IDs',
                 'Choose an attack to perform (From, To)\nFalse is for no attack',
                 'Continue Attack?',
                 'How many troops do you want to risk in battle?',
                 'Reinforce from what territory?',
                 'Send reinforcements to what territory?',
                 'Where should 1 troop go during reinforcement?',
                 'Where should 1 troop move after the attack?',
                 'Which arrangement of cards would you like to trade in?']
        self.acodes=dict(zip(range(9), prompts))

    def take_action(self, state, action_code, options):
        '''The environment provides the state, and requests an action from the agent'''

        print(self.acodes[action_code])
        for index,option in enumerate(options):
            print(index,'is for option',option)
        user_input = input("Choose: ")
        while user_input not in [str(x) for x in range(len(options))]:
            user_input = input('Invalid, choose again: ')

        return options[int(user_input)]

    

    
