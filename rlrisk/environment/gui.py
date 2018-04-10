'''
This class is the gui for the game
it can be used by setting the GUI flag when
creating a Risk object
'''

import pygame, os

class GUI(object):
    '''
    The GUI for the game, which is optional, and functions
    related to the GUI
    '''
    
    def __init__(self):
        self.colors = self.gen_colors()
        self.p2c = self.player_colors()

        #code to run at start
        pygame.init()

        #name game window
        pygame.display.set_caption("RLRisk - Reinforcement Learning Environment")

        #load image and make background
        self.background = pygame.image.load(os.path.join(os.getcwd(),'rlrisk/environment/board.bmp'))
        self.size = self.background.get_size()
        self.screen = pygame.display.set_mode(self.size)
        self.background = self.background.convert()
        self.positions = self.gen_positions()
        self.backgroundRect = self.background.get_rect()
        self.init_draw()


        #get fonts working
        pygame.font.init()
        self.d_font = pygame.font.get_default_font()
        self.id_font = pygame.font.Font(self.d_font, 20)
        self.font = pygame.font.Font(self.d_font, 12)


    def init_draw(self):
        '''Draws the initial screen'''
        self.size = self.background.get_size() #duplicate on purpose, for subclasses
        self.screen = pygame.display.set_mode(self.size)
        self.screen.blit(self.background, self.backgroundRect)
        [pygame.draw.circle(self.screen,self.colors["white"],(x,y),14, 0) for x,y in self.positions.values()]
        pygame.display.flip()
        
    def loop_event(self, target_event_type):
        '''
        Loops through all the pygame events,
        looks for a specific event, and garages the rest

        so instead of running a continuous loop (like normal for pygame)
        this loop is run on command as the game is static
        '''

        for event in pygame.event.get():

            e = event
            del event #clear the event log

            if e.type == target_event_type:
                return e

            #exit on click
            if e.type == pygame.QUIT:
                self.quit_game()
                return True

    def recolor(self, state):
        '''
        colors a circle representing a territory from a environment state
        '''

        #not interested in events
        pygame.event.clear()

        #reload original background
        self.screen.blit(self.background, self.backgroundRect)

        #get the territories dictionary
        territories = state[0]

        #now color and text cirlces
        for key in self.positions:
            #get owner and troop values
            t_owner,troops = territories[key]

            #color all the circles their respective colors
            pygame.draw.circle(self.screen, self.colors[self.p2c[t_owner]],
                               self.positions[key], 14, 0)

            #now add the troop count font
            label = self.font.render(str(troops),1,self.colors['black'])

            #and the province id
            label_id = self.id_font.render(str(key),1,self.colors['white'])
            
            x,y = self.positions[key]
            self.screen.blit(label,(x-12,y-6))
            self.screen.blit(label_id,(x-6,y-30))

        self.draw_players(state)

        pygame.display.flip()

            

    def quit_game(self):
        '''closes the pygame window'''
        pygame.display.quit()
        pygame.quit()

    def gen_positions(self):
        '''returns a dictionary that matches ID to node positions in pygame'''

        positions = [
            (80,120), (220,140), (440,100), (180,180), (240,200),
            (340,200), (200,260), (280,270), (235,320), (355,370),
            (430,430), (355,440), (370,500), (520,320), (620,305),
            (640,345), (610,390), (610,460), (690,450), (930,390),
            (1030,405), (960,470),(1050,480), (490,150), (515,200),
            (570,150), (650,190), (570,210), (610,240), (515,250),
            (680,280), (750,230), (800,150), (860,110), (980,110),
            (1120,130), (920,180),(960,230), (1030,260), (920,280),
            (800,310), (885,330)]

        x,y = self.size
        xmod = x/1200
        ymod = y/600

        positions = [(int(p[0]*xmod),int(p[1]*ymod)) for p in positions]

        return dict(zip(range(42),positions))

    @staticmethod
    def gen_colors():
        '''returns a dictionary of RGB colors to be used in pygame'''

        colors = {
            "red":(255,0,0),
            "green":(0,255,0),
            "cyan":(0,255,255),
            "yellow":(255,255,0),
            "purple":(255,0,255),
            "orange":(255,128,0),
            "white":(255,255,255),
            "black":(0,0,0)
            }

        return colors

    @staticmethod
    def player_colors():
        '''assigned players colors in pygame'''

        p2c = {-1:'white',0:"red",1:'green',2:'cyan',3:'yellow',4:'purple',5:'orange'}

        return p2c


    def draw_players(self, state):
        '''draws the players and # cards in their hands'''
        cards = state[1]

        players_cards={}
        for num in range(8):
            players_cards[num]=0
        for key in cards:
            players_cards[cards[key]]+=1

        #remove invalid players
        players_cards.pop(6,None)
        players_cards.pop(7,None)

        players = sorted(list(players_cards.keys()))
        y = 550
        for i,p in enumerate(players):
            x = 600 + 30*i
            #color all the circles their respective colors
            pygame.draw.circle(self.screen, self.colors[self.p2c[p]],
                               (x,y), 14, 0)
            label = self.font.render(str(players_cards[p]),1,self.colors['black'])
            self.screen.blit(label,(x-12,y-6))

        
