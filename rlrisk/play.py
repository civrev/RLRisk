'''
This is the GUI for the Risk RL
by running this it will begin a game with a GUI
'''

import pygame
import risk_environment as risk
import config
        
def startup():
    '''begins the game'''

    pygame.init()

    #name game window
    pygame.display.set_caption("Risk Reinforcement Learning Project")

    #load image and make background
    background = pygame.image.load("board.bmp")
    size = background.get_size()
    screen = pygame.display.set_mode(size)
    backgroundRect = background.get_rect()
    screen.blit(background, backgroundRect)

    #get fonts working
    pygame.font.init()
    default_font = pygame.font.get_default_font()
    font_renderer = pygame.font.Font(default_font, 12)

    #get game clock
    clock = pygame.time.Clock()

    #get some colors
    colors = gen_colors()

    #get positions
    positions = gen_positions()

    #get colors per player id
    p2c = player_colors()

    #place holding white circles
    [pygame.draw.circle(screen,colors["white"],positions[i],14, 0) for i in range(42)]

    #game loop
    done = False
    while not done:
            
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                done=True

        #update display, and moderate frame rate to 1fps
        pygame.display.flip()
        clock.tick(1)

def gen_positions():
    #moved to risk.py
    pass

def gen_colors():
    #moved to risk.py
    pass

def player_colors():
    #moved to risk.py
    pass

#----------------------------------------------------------------------
# Main
#----------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    startup()
