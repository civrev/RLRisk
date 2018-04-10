import rlrisk as rlr
import numpy as np
import time 

class PickStartGame(object):
    '''A mini game for picking starting territories'''
    
    def __init__(self, agents, has_gui=True, verbose_gui=True):
        '''sets up the minigame'''
        self.players = agents
        self.verbose_gui = verbose_gui
        self.has_gui=has_gui
        if has_gui:
            self.gui = rlr.environment.gui.GUI()
        self.board, self.continents, cf = rlr.environment.risk.Risk.gen_board()
        #random turn order
        self.turn_order = rlr.environment.config.turn_order(len(agents), clockwise = "r")
        self.state = rlr.environment.risk.Risk.gen_init_state()

    def play(self):
        '''Begins the minigame'''
        
        territories, cards, trade_ins = self.state

        turn_count = 0
        record = np.empty([42,42], dtype='int32')
        
        
        valid = list(range(42))
        for index in range(42):

            turn = self.turn_order[turn_count%len(self.players)]
            
            current_player = self.players[turn]
            chosen = current_player.take_action(self.state, 9, valid)

            territories[chosen]=[turn,1]

            valid.remove(chosen)

            turn_count+=1

            owners = np.empty([42,], dtype='int32')
            for num in range(42):
                owners[num]=territories[num][0]
            record[index]=owners

            #repack state
            self.state = (territories, cards, trade_ins)

            if self.has_gui:
                self.gui.recolor(self.state)

            if self.has_gui and self.verbose_gui:
                time.sleep(0.5)

        #at this point all provinces have been chosen
        print('All positions have been chosen')
        return record
        
