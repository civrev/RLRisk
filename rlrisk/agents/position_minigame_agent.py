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

class StartLearningAgent(BaseAgent):

    def __init__(self, nodes=144, learning_rate=1, v_flag=True):
        super(StartLearningAgent, self).__init__()

        #Size of state array, for input layer of NN
        self.input = 42+42+44+1

        #42 territories to choose from
        self.output = 42

        #verbose output from NN
        self.v_flag = v_flag

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
            
            state = np.array([np.append(state[0].flatten(), np.append(state[1],[state[2]]))])
            

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

    def update(self, state):
        #average the predicted values for the actions
        #with the reward*learning rate
        
        reward = self.calculate_fitness(state)

        self.move_history = [np.mean([y, reward], axis=0) for y in self.move_history]

        X = np.vstack(self.state_history)
        y = np.vstack(self.move_history)

        self.model.fit(X, y, epochs=6, verbose=self.v_flag)

        self.reset()

    def correct(self, state, valid):
        '''
        Train NN on valid options for state
        '''
        layer = np.array([[0]*self.output])
        for pos in valid:
            layer[0, pos] = 1
        self.model.fit(state, layer, verbose=False)
        

    def create_nn(self):
        '''
        Builds a neural network
        '''

        #build model
        model = Sequential()
        model.add(Dense(self.nodes, activation='sigmoid', input_shape=(self.input,)))
        model.add(Dense(int(self.nodes*0.75), activation='sigmoid'))
        model.add(Dense(int(self.nodes*0.5), activation='sigmoid'))
        model.add(Dense(self.output, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        return model

    def calculate_fitness(self, state):
        '''
        Calculates fitness score
        '''

        fitness = 0

        
        territories_owned = np.where(state[0][:, 0] == self.player)[0]

        

        for continent in self.continents:
            reward = self.continent_rewards[continent]
            size = len(self.continents[continent])
            t_in_c_count = 0
            for territory in self.continents[continent]:
                if territory in territories_owned:
                    t_in_c_count+=1
            fitness += reward * (t_in_c_count/size)**4

        return fitness
