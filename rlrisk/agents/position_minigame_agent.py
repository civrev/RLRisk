"""
This is a learning agent for playing the minigame
Pick Start Positions
"""
import warnings
warnings.filterwarnings("ignore")

from rlrisk.agents import BaseAgent

from keras.layers import Dense
from keras.utils import to_categorical
from keras.models import Sequential
from keras.callbacks import EarlyStopping
import numpy as np
import random

class StartLearningAgent(BaseAgent):

    def __init__(self, nodes=100, learning_rate=1, v_flag=True, epsilon=0.1):
        super(StartLearningAgent, self).__init__()

        #Size of state array, for input layer of NN
        self.input = 42

        #42 territories to choose from
        self.output = 42

        #verbose output from NN
        self.v_flag = v_flag

        #for epsilon greedy
        self.epsilon = epsilon

        self.nodes = nodes
        self.alpha = learning_rate
        self.model = self.create_nn()
        self.state_history = []
        self.move_history = []

        self.prev_reward = 0
        self.reward = 0

        self.correct_count = 0

    def take_action(self, state, action_code, options):

        #if for some reason this agent is used
        #for anything other than the minigame,
        #skip learning
        if action_code == 9:
            
            state = np.array([state[0][:,0]])
            

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

            if random.random() < self.epsilon:
                max_action = random.choice(options)

            #record the state
            self.state_history.append(state)

            #record move after collecting reward
            self.reward = self.calculate_fitness(state) - self.prev_reward
            actions[0,max_action] = (actions[0,max_action]+self.reward)/2
            self.prev_reward = self.reward

            self.move_history.append(actions)
            
            return max_action

        else:
            super(StartLearningAgent, self).take_action(state, action_code, options)

    def reset(self):
        self.state_history = []
        self.move_history = []
        self.prev_reward = 0

    def update(self):
        #average the predicted values for the actions
        #with the reward*learning rate
        
        X = np.vstack(self.state_history)
        y = np.vstack(self.move_history)

        self.model.fit(X, y, epochs=6, verbose=self.v_flag)

    def correct(self, state, valid):
        '''
        Train NN on valid options for state
        '''
        layer = np.array([[0]*self.output])
        for pos in valid:
            layer[0, pos] = 1
        self.model.fit(state, layer, epochs=1, verbose=False)

        self.correct_count+=1

    def create_nn(self):
        '''
        Builds a neural network
        '''

        model = Sequential()
        model.add(Dense(int(self.nodes*1), activation='sigmoid', input_shape=(self.input,)))
        model.add(Dense(int(self.nodes*0.8), activation='sigmoid'))
        model.add(Dense(int(self.nodes*0.7), activation='sigmoid'))
        model.add(Dense(self.output, activation='sigmoid'))
        model.compile(optimizer='adam', loss='mean_absolute_percentage_error', metrics=['accuracy'])

        return model

    def calculate_fitness(self, state):
        '''
        Calculates fitness score
        '''

        fitness = 0

        for continent,provinces in self.continents.items():
            con_reward = self.continent_rewards[continent]
            continent_owners = state[0,provinces]
            owned_in_continent = continent_owners[continent_owners == self.player]
            fraction_owned = len(owned_in_continent)/len(provinces)
            fitness += con_reward * (fraction_owned**3)

        return fitness
