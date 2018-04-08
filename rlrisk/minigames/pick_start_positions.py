import rlrisk as rlr

class PickStartGame(object):
    '''A mini game for picking starting territories'''
    
    def __init__(self, agents):
        '''sets up the minigame'''
        self.players = agents
        self.gui = rlr.environment.gui.GUI()
        self.board, self.continents, cf = rlr.environment.risk.Risk.gen_board()
        self.state = rlr.environment.risk.Risk.gen_init_state(False, [0])

    def play(self):
        '''Begins the minigame'''
        
        steal_cards, turn_order, territories, cards, trade_ins = self.state

        turn_count = 0
        
        valid = list(range(42))
        for index in range(42):

            turn = turn_order[turn_count%len(self.players)]
            
            current_player = self.players[turn]
            chosen = current_player.choose_initial_territories(valid, self.state)

            territories[chosen]=[turn,1]

            valid.remove(chosen)

            turn_count+=1

            self.gui.recolor(self.state)

            #repack state
            self.state = (steal_cards, turn_order, territories, cards, trade_ins)

        #at this point all provinces have been chosen
        print('All positions have been chosen')
        
