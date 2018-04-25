'''
This module holds the class for which the gui for the game is made
it can be used by setting the GUI flag when creating a Risk object
'''

import os
import pygame

class GUI(object):
    '''
    The GUI for the game, which is optional, and functions related to the GUI
    '''

    def __init__(self):
        """Loading the images and setting fonts and defaults"""
        self.colors = self.gen_colors()
        self.p2c = self.player_colors()

        #code to run at start
        pygame.init()

        #name game window
        pygame.display.set_caption("RLRisk - Reinforcement Learning Environment")

        #load image and make background
        path = os.path.dirname(__file__)
        self.background = pygame.image.load(os.path.join(path, 'board.bmp'))
        self.size = self.background.get_size()
        self.screen = pygame.display.set_mode(self.size)
        self.background = self.background.convert()
        self.positions = self.gen_positions()
        self.background_rect = self.background.get_rect()
        self.init_draw()


        #get fonts working
        pygame.font.init()
        self.d_font = pygame.font.get_default_font()
        self.id_font = pygame.font.Font(self.d_font, 20)
        self.font = pygame.font.Font(self.d_font, 12)


    def init_draw(self):
        """
        Displays the pregame-start screen

        Sets up the pygame display, draws the background,
        and empty positions (as white).

        Parameters
        -------------------
        None

        Returns
        -------
        None

        """
        self.size = self.background.get_size() #duplicate on purpose, for subclasses
        self.screen = pygame.display.set_mode(self.size)
        self.screen.blit(self.background, self.background_rect)
        for xpos, ypos in self.positions.values():
            pygame.draw.circle(self.screen, self.colors["white"], (xpos, ypos), 14, 0)
        pygame.display.flip()

    def recolor(self, state):
        """
        Updates the display for the current state

        Sets the color of each territory to the player color of the
        current owner and displays the number of troops present in each
        territory. Also shows the number of cards in each player's hand
        and the player color.

        Required Parameters
        -------------------
        State : 3 value tuple
            (2, 42) Numpy Array representing each territory owner and troop count
            (44,)   Numpy Array representing status of each card
            integer representing the number of card set trade-ins so far

        Returns
        -------
        None

        """

        #not interested in events
        pygame.event.clear()

        #reload original background
        self.screen.blit(self.background, self.background_rect)

        #get the territories dictionary
        territories = state[0]


        #now color and text cirlces
        for key in self.positions:
            #get owner and troop values
            territory = territories[key]

            #color all the circles their respective colors
            pygame.draw.circle(self.screen, self.colors[self.p2c[territory[0]]],
                               self.positions[key], 14, 0)

            #now add the troop count font
            label = self.font.render(str(territory[1]), 1, self.colors['black'])

            #and the province id
            label_id = self.id_font.render(str(key), 1, self.colors['white'])

            xpos, ypos = self.positions[key]
            self.screen.blit(label, (xpos - 12, ypos - 6))
            self.screen.blit(label_id, (xpos - 6, ypos - 30))

        self.draw_players(state)

        pygame.display.flip()

    def quit_game(self):
        """
        Quits the GUI

        Closes the Pygame display

        Parameters
        -------------------
        None

        Returns
        -------
        None

        """
        pygame.display.quit()

    def gen_positions(self):
        """
        Get X, Y coordinates on screen

        Maps Territory ID to the position to display data on screen
        for that territory

        Parameters
        -------------------
        None

        Returns
        -------
        Dictionary
            A dictionary with territory ID as the key and
            the X, Y position on screen for that territory

        """

        positions = [
            (80, 120), (220, 140), (440, 100), (180, 180), (240, 200),
            (340, 200), (200, 260), (280, 270), (235, 320), (355, 370),
            (430, 430), (355, 440), (370, 500), (520, 320), (620, 305),
            (640, 345), (610, 390), (610, 460), (690, 450), (930, 390),
            (1030, 405), (960, 470), (1050, 480), (490, 150), (515, 200),
            (570, 150), (650, 190), (570, 210), (610, 240), (515, 250),
            (680, 280), (750, 230), (800, 150), (860, 110), (980, 110),
            (1120, 130), (920, 180), (960, 230), (1030, 260), (920, 280),
            (800, 310), (885, 330)]

        xmod = lambda x: int(x * (self.size[0] / 1200))
        ymod = lambda y: int(y * (self.size[1] / 600))

        positions = [(xmod(p[0]), ymod(p[1])) for p in positions]

        return dict(zip(range(42), positions))

    @staticmethod
    def gen_colors():
        """
        Maps colors to RGB values

        Creates a dictionary that maps the name of colors to their RBG values

        Parameters
        -------------------
        None

        Returns
        -------
        Dictionary
            A dictionary with color name as the key and
            the RBG values of that color

        """

        colors = {
            "red":(255, 0, 0),
            "green":(0, 255, 0),
            "cyan":(0, 255, 255),
            "yellow":(255, 255, 0),
            "purple":(255, 0, 255),
            "orange":(255, 128, 0),
            "white":(255, 255, 255),
            "black":(0, 0, 0)
            }

        return colors

    @staticmethod
    def player_colors():
        """
        Records what player is what color

        Creates a dictionary that maps player index to a color

        Required Parameters
        -------------------
        State : 3 value tuple
            (2, 42) Numpy Array representing each territory owner and troop count
            (44,)   Numpy Array representing status of each card
            integer representing the number of card set trade-ins so far

        Returns
        -------
        Dictionary
            A dictionary with player number as the key (and -1 for unowned) and
            a color to display for them

        """

        p2c = {-1:'white',
               0:"red",
               1:'green',
               2:'cyan',
               3:'yellow',
               4:'purple',
               5:'orange'}

        return p2c

    def draw_players(self, state):
        """
        Draws the player colors and card counts to display

        Counts the number of cards each player has, and puts them in
        a circle with player color on screen. Also displays total number
        of card trade ins so far.

        Required Parameters
        -------------------
        State : 3 value tuple
            (2, 42) Numpy Array representing each territory owner and troop count
            (44,)   Numpy Array representing status of each card
            integer representing the number of card set trade-ins so far

        Returns
        -------
        None

        """
        cards = state[1]
        trade_ins = state[2]

        players_cards = {}
        for num in range(8):
            players_cards[num] = cards[cards == num].shape[0]

        #remove invalid players
        players_cards.pop(6, None)
        players_cards.pop(7, None)

        players = sorted(list(players_cards.keys()))
        ypos = 550
        orig_x = 600

        label = self.font.render("Trade ins: " + str(trade_ins), 1, self.colors['black'])
        self.screen.blit(label, (orig_x, ypos - 30))

        for i, player in enumerate(players):
            xpos = orig_x + 30 * i
            #color all the circles their respective colors
            pygame.draw.circle(self.screen, self.colors[self.p2c[player]],
                               (xpos, ypos), 14, 0)
            label = self.font.render(str(players_cards[player]), 1, self.colors['black'])
            self.screen.blit(label, (xpos - 12, ypos - 6))
