"""
This is a learning agent for playing the minigame
Pick Start Positions
"""

from rlrisk.agents import BaseAgent

import keras
import numpy as np

class StartLearningAgent(BaseAgent):

    def __init__(self, nodes=144, learning_rate=1):
        super(StartLearningAgent, self).__init__()

        self.nodes = nodes
        self.alpha = learning_rate
        self.model = self.create_nn()
        self.state_history = []
        self.move_history = []

    def take_action(self, state, action_code, options):

        #if for some reason this agent is used
        #for anything other than the minigame,
        #skip learning
        if action_code == 9:

            #get the predictions on values of each potential state
            #for all actions
            actions = self.model.predict(state)

            #choose the one with the highest value
            max_action = np.argmax(actions)

            #if it chose an invalid option, train it until it learns
            #the rules
            while max_action not in options:
                #handles the training
                self.correct(state, options)

                #choose again
                actions = self.model.predict(state)
                max_action = np.argmax(actions)

            #record the state and move that was made
            self.state_history.append(state)
            self.move_history.append(actions)

            return max_action

        else:
            super(StartLearningAgent, self).take_action(state, action_code, options)

    def reset(self):
        self.state_history = []
        self.move_history = []

    def update(self, reward):
        #average the predicted values for the actions
        #with the reward*learning rate
        avg = lambda (y, r): np.mean([y, r], axis=0)
        self.move_history = [avg(y, reward) for y in self.move_history]
