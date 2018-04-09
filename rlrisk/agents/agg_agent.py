'''
Same randomness as BaseAgent, but always
choosing more aggressive choices
'''

import random
from rlrisk.agents.base_agent import BaseAgent

class AggAgent(BaseAgent):
    def choose_attack(self, state, attacks):
        '''Always chooses attack'''
        if len(attacks)>1:
            return random.choice(attacks[:-1])
        else:
            return attacks[0]
    def continue_attack(self, state, current_attack):
        '''Always continue attack'''
        return True
    def after_attack_troops(self, state, attack_from, attack_to, remaining):
        '''Always move into newly occupied province'''
        return attack_to
