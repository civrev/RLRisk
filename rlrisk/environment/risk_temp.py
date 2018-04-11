import numpy as np
import random
from rlrisk.environment import config, gui

from rlrisk.agents.base_agent import BaseAgent
from rlrisk.agents.human import Human

class Risk(object):
    """Game Environment for Risk World Domination Ruleset"""

    def __init__(self, agents, turn_order="c", trade_vals="s", steal_cards=False,
                 deal=True, has_gui=False, verbose_gui=False, debug=False):
        """
        Risk Constructor

        Sets up the game environment with chosen ruleset.

        Required Parameters
        ----------
        agents : List/Tuple of BaseAgent class or subclasses
            List of agents that will be the players in the game. Players must
            be BaseAgent or subclass of BaseAgent, or at least follow the general
            structure of that class

        Optional Parameters
        ----------
        turn_order : String "c"/"r" or List
            Options for the turn order in the game.
            "c" = Clockwise (as in increasing) order from random player
            "r" = Random turn order. Turn order will not be increasing, but will
                  remain constant throughout game
            List = List of custom turn order for index of agents
                   Example [0, 2, 3, 1] Player 1 will go first, followed by player 3
                   then player 4 and then player 2

            "c" by default

        trade_vals : String "s"/"1" or Generator
            Options for the sequence that generate card set trade in rewards
            "s" = Standard Risk trade in rewards
            "1" = Increasing by 1
            Generator = Generator representing a unique sequence of integers to reward

            "s" by default

        steal_cards : boolean
            Whether or not defeated player's card go to the player that defeated them

            True by default

        deal : boolean
            Whether or not players are randomly alloted territories or they pick them
            one by one

            True by default

        has_gui : boolean
            Whether or not to use the Pygame gui to observe actions during game

            False by default

        verbose_gui : boolean
            Whether or not to update Pygame gui in between individual troop allocations
            useful when playing as Human agent. Considerable slows down the game.

            False by default        

        Returns
        -------
        None

        """

        self.players = agents
        
        if isinstance(turn_order, str):
            self.turn_order = config.turn_order(len(agents), turn_order)
        else:
            self.turn_order = turn_order

        if isinstance(trade_vals, str):
            self.trade_vals = config.get_trade_vals(trade_vals)
        else:
            self.trade_vals = trade_vals

        self.steal_cards = steal_cards
        self.has_gui = has_gui
        self.verbose_gui = verbose_gui
        self.deal = deal

        self.turn_count = 0
        self.game_over = False
        self.board, self.continents, self.card_faces, self.con_rewards = self.gen_board()
        self.state = self.gen_init_state()
        self.node2name, self.name2node = self.id_names()
        self.troop_count_record = []
        self.territory_owner_record = []
        self.card_ownership_record = []
        self.trade_in_record = []

        if has_gui:
            self.gui = gui.GUI()
        
    def play(self):
        """
        Play the game

        Begins the game with the rules and variations set forth during
        instantiation. Games start with territory allotment, and then
        proceed to the main portion of the game, turn taking. 

        Parameters
        ----------
        None
        
        Returns
        -------
        5 value tuple
            (TurnCount,42) Numpy Array: Record of territory ownership
            (TurnCount,42) Numpy Array: Record of troops per territory
            (TurnCount,44) Numpy Array: Record of card ownership
            (TurnCount,)   Numpy Array: Record of number of card set trade ins
            List: In order numbering of each players turn order 0->n players
            boolean: Whether or not defeated player's card go to the player that
                     defeated them

        """

        num_players = len(self.players)

        #divy up territories at game start
        self.allocate_territories()
        self.gui_update()

        #Main game loop
        while not self.game_over:
            #record state
            self.territory_owner_record.append(self.state[0][:,0])
            self.troop_count_record.append(self.state[0][:,1])
            self.card_ownership_record.append(self.state[1])
            self.trade_in_record.append(self.state[2])

            #get the index of player whose turn it is
            turn = self.turn_order[self.turn_count%num_players]

            #check if player is defeated, if so skip turn
            if self.players[turn].defeated:
                self.turn_count+=1
                turn = self.turn_order[self.turn_count%num_players]

            #perform recruitment phase
            self.recruitment_phase(turn)
            self.gui_update()

            #perform attack phase
            self.attack_phase(turn)
            self.gui_update()

            #Don't allow reinforcement phase if player has won the game
            if self.winner():
                self.game_over = True
                break

            #perform recruitment phase
            self.reinforce_phase(turn)
            self.gui_update()

            #increase turn count
            self.turn_count+=1

        #exit message
        winner = self.turn_order[(self.turn_count-1)%num_players]+1
        print("The game is over! Player",winner,"won the game!")

        return (np.array(self.owner_record),
                np.array(self.troop_record),
                np.array(self.card_record),
                np.array(self.trade_in_record),
                self.turn_order,
                self.steal_cards)

    def recruitment_phase(self, player):
        """
        Executes recruitment phase

        Collects the number of troops a player should recieve at turn start,
        then asks the player to distribute them. Afterwards if the player has
        cards to trade in they may choose to (or must) do so at this time.

        Required Parameters
        ----------
        player :
            The index of the agent in self.players
        
        Returns
        -------
        None

        """

        recruited = self.calculate_recruits(player)
        self.place_troops(player,recruited)

        #gets card sets, if they have card sets ask the player if they want to trade
        set_list,card_count = self.get_sets(player)
        if len(set_list)!=0:
            recruited = self.trade_in(player, set_list, card_count)
            #zero is they chose not to trade in a set
            if recruited!=0:
                self.place_troops(player, recruited)

    def get_owned_territories(self, player):
        """
        Finds all territories owned by the player

        Required Parameters
        ----------
        player :
            The index of the agent in self.players
        
        Returns
        -------
        (?,) Numpy Array:
            The IDs of territories owned by the player

        """

        territories, cards, trade_ins = self.state
        return np.where(territories[:,0]==player)[0]

    def calculate_recruits(self, player):
        """
        Calculates the number of troops recruited at turn start

        Sums troop bonuses based on territories own and continent bonuses

        Required Parameters
        ----------
        player :
            The index of the agent in self.players
        
        Returns
        -------
        integer :
            The number of troops to be recruited

        """
        territories, cards, trade_ins = self.state

        territories_owned = self.get_owned_territories(player)

        #Risk rules say # of owned territories then floor division by 3
        recruitment = len(territories_owned)//3

        #you always get at least 3
        if recruitment < 3:
            recruitment = 3

        #Calculate for continents
        for continent in self.continents:
            c_owned=True
            for territory in self.continents[continent]:
                if territory not in territories_owned:
                    c_owned=False

        if c_owned:
                recruitment += self.con_rewards[continent]

        return recruitment

    def place_troops(self, player, troops):
        """
        Place troops into owned territory

        Prompts the player for a territory to place troops one at a time

        Required Parameters
        ----------
        player :
            The index of the agent in self.players

        troops :
            Number of troop the player must place
        
        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state
        current_player = self.players[player]

        for troop in range(troops):
            valid = self.get_owned_territories(player)
            chosen = current_player.take_action(self.state, 0, valid)
            territories[chosen][1]+=1
            self.state = (territories, cards, trade_ins)
            self.gui_update(True)

    def get_sets(self, player):
        """
        Calculates the number of unique tradable card sets

        Generates all unique combination of cards the player owns
        that may be traded in. Valid sets are:
            - any 3 of same kind
            - set of 1,5,10
            - any 2 and a wild card

        Required Parameters
        ----------
        player :
            The index of the agent in self.players
        
        Returns
        -------
        List of Lists:
            All the unique arrangements of card that can be traded in

        integer :
            The number of cards a player owns

        """

        territories, cards, trade_ins = self.state

        cards_owned = np.where(cards==player)[0]

        one = []
        five = []
        ten = []
        wild = []
        set_list = []

        for card in cards_owned:
            if self.card_faces[card] == 1:
                one.append(card)
            elif self.card_faces[card] == 5:
                five.append(card)
            elif self.card_faces[card] == 10:
                ten.append(card)
            else:
                wild.append(card)

        #three of a kind
        if len(one)>=3:
            set_list.append(one[:3])
        if len(five)>=3:
            set_list.append(five[:3])
        if len(ten)>=3:
            set_list.append(ten[:3])

        #one of each kind
        if len(one)>=1 and len(five)>=1 and len(ten)>=1:
            set_list.append([one[0],five[0],ten[0]])

        #wild card sets
        for wc in wild:
            if len(one)>=2:
                #two of ones
                set_list.append([one[0], one[1], wc])
            if len(five)>=2:
                #two of fives
                set_list.append([five[0], five[1], wc])
            if len(ten)>=2:
                #two of tens
                set_list.append([ten[0], ten[1], wc])
            if len(one)!=0 and len(five)!=0:
                #one 1 and one 5
                set_list.append([one[0], five[0], wc])
            if len(one)!=0 and len(ten)!=0:
                #one 1 and one 10
                set_list.append([one[0], ten[0], wc])
            if len(ten)!=0 and len(five)!=0:
                #one 5 and one 10
                set_list.append([ten[0], five[0], wc])

        return (set_list, len(cards_owned))

    def allocate_territories(self):
        """
        Allocates territories to players at game start

        If rules are to randomly deal, assigns 1 troop to each player randomly
        in a territory going by turn order. Otherwise allows players to
        choose territories one by one

        Parameters
        ----------
        None
        
        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state

        remaining = list(range(42))

        for index in range(42):

            player_id = self.turn_order[index%len(self.turn_order)]

            if self.deal:
                chosen = random.choice(remaining)
            else:
                chosen = self.players[turn].take_action(self.state, 9, valid)

            remaining.remove(chosen)

            territories[chosen][0]=player_id
            territories[chosen][1]=1

        self.state = (territories, cards, trade_ins)


    def gui_update(self, verbose=False):
        """
        Updates the GUI based on initial preferences

        Normal GUI updates occur after every phase of a player's turn
        while verbose GUI updates occur thoughout each phase
        which is very helpful when testing as a Human agent

        Optional Parameters
        ----------
        verbose : boolean
            Whether or not this is a verbose gui update
        
        Returns
        -------
        None

        """
        if self.has_gui:
            if not verbose:
                self.gui.recolor(self.state)
            elif verbose and self.verbose_gui:
                self.gui.recolor(self.state)
            if self.game_over:
                self.gui.quit_game()


    #Game Setup Methods
    @staticmethod
    def gen_board():
        """
        Generates Risk board mappings

        Dictionaries for static game information

        Parameters
        ----------
        None
        
        Returns
        -------
        4 value tuple
            Dictionary: Territory IDs as keys for territory adjacentcy values
            Dictionary: Continent names as keys for containing territory IDs values
            Dictionary: Card IDs as keys for card face values
            Dictionary: Continent names as keys for ownership reward values

        """

        board = {
            0:[1,3,35],1:[0,2,3,4],2:[5,1,4,23],3:[0,4,1,6],4:[1,2,3,5,6,7],
            5:[2,4,7],6:[3,4,7,8],7:[5,4,6,8],8:[6,7,9],9:[8,10,11],
            10:[9,12,11,13],11:[10,12,9],12:[10,11],13:[10,14,16,28,29,15],
            14:[13,16,28,29],15:[13,16,17,14,30,18],16:[13,15,17],17:[16,15,18],
            18:[17,15],19:[41,20,21],20:[22,21,19],21:[22,19,20],22:[20,21],
            23:[2,24,25],24:[23,25,27,29],25:[23,27,26,24],26:[25,27,28,30,31,32],
            27:[26,28,29,25,24],28:[29,27,26,30,13,14],29:[13,28,27,24],
            30:[31,40,14,15,26,28],31:[32,30,26,40,39],32:[31,26,33,39],
            33:[32,39,37,34,36],34:[33,36,35],35:[38,34,36,0],36:[35,34,33,37],
            37:[36,38,39,33,35],38:[35,37],39:[31,37,33,41,40,32],40:[39,41,31,30],
            41:[39,40,19]
            }

        continents = {
            "Europe":[23,24,25,26,27,28,29],
            "N_America":[5,0,1,2,3,4,5,6,7,8],
            "Africa":[14,18,13,15,16,17],
            "Australia":[19,20,21,22],
            "Asia":[30,31,32,33,34,35,36,37,38,39,40,41],
            "S_America":[9,12,10,11]
            }


        #the army size presented on the front of the Risk card
        #99 is wild card
        card_faces = {0:1,1:10,2:5,3:1,4:5,5:10,6:1,7:10,8:5,9:10,10:10,
                      11:5,12:1,13:1,14:1,15:10,16:5,17:10,18:1,19:5,20:5,
                      21:10,22:1,23:1,24:5,25:10,26:10,27:5,28:5,29:1,30:10,
                      31:1,32:5,33:10,34:5,35:5,36:1,37:10,38:1,39:5,40:1,
                      41:10,42:99,43:99}

        continent_rewards = {"Europe":5,"N_America":5,"Africa":3,
                             "Australia":2,"Asia":7,"S_America":2}

        return (board, continents, card_faces, continent_rewards)
    
    @staticmethod
    def id_names():
        """
        Identify Names of Provinces and IDs of Provinces

        Helpful 2-way dictionaries for territories

        Parameters
        ----------
        None
        
        Returns
        -------
        2 value tuple
            Dictionary: Territory IDs as keys for territory name values
            Dictionary: Territory names as keys for territory IDs values

        """
        names = [
            #North America
            "Alaska","NW_Territory","Greenland","Alberta",
            "Ontario","Quebec","W_US","E_US","C_America",
            #South America
            "Venezuela","Brazil","Peru","Argentina",
            #Africa
            "N_Africa","Egypt","E_Africa","Congo","S_Africa","Madagascar",
            #Australia
            "Indonesia","New_Guinea","W_Australia","E_Australia",
            #Europe
            "Iceland","Great_Britain","Scandanavia",
            "Ukraine","N_Europe","S_Europe","W_Europe",
            #Asia
            "Mid_East","Afghanistan","Ural","Siberia",
            "Yakutsk","Kamchatka","Irkutsk","Mongolia",
            "Japan","China","India","Siam"]

        node2name = {}
        for num, name in enumerate(names):
            node2name[num]=name

        name2node = {}
        for num, name in enumerate(names):
            name2node[name]=num

        return (node2name,name2node)

    @staticmethod
    def starting_troops(players):
        """
        Get the number of starting troops for each player

        2 player variation from rules is that they get 40 troops
        in place of 'neutral 3rd player'

        Required Parameters
        ----------
        players : integer
            The number of players in the game
        
        Returns
        -------
        integer
            The number a troops each player should start with

        """
        return {2:40,3:35,4:30,5:25,6:20}[players]

    @staticmethod
    def gen_init_state():
        """
        Generate the pregame state of the environment

        Not normally a valid state, this is just a place holder for
        the game until territories are allocated

        Parameters
        ----------
        None
        
        Returns
        -------
        3 value tuple
            (42, 2) Numpy Array: Territories with owner and troop count
            (44,)   Numpy Array: Cards by owner/status
            0: The number of times card sets have been traded in so far

        """
        territory = np.array([-1, 0])
        territories = np.array([territory for x in range(42)])
        cards = np.repeat(6, 44)
        return (territories, cards, 0)

#Get rid of this for full version ----------------------------------------------
if __name__ == "__main__":
    
    print(Risk([BaseAgent() for x in range(6)]).play())
    
