'''
This class represents the game environment (the board)
of Risk using standard World Domination ruleset
See instructions https://www.hasbro.com/common/instruct/risk.pdf
'''

import random
from rlrisk.environment import config
from rlrisk.environment import gui

class Risk:
    '''Game Environment for Risk World Domination'''

    def __init__(self, players, turn_order, trade_vals, steal_cards=False, has_gui=False):
        '''
        setting up for the game
        the arguments here are the rule settings for the game
        turn_order: order that players take turns (in a list)
        trade_vals: sequencial values of traded in card sets (also a list)
        random_deal: whether players pick their territories at game start or are assigned
        '''

        #house keeping for players
        for num,p in enumerate(players):
            p.set_player(num)

        self.has_gui = has_gui #whether or not the gui should be displayed

        if has_gui:
            self.gui = gui.GUI()
            
        self.players = players #the agents that play the game
        self.turn_count = 0 #initialize turn count at 0
        self.node2name, self.name2node = self.id_names() #dictionaries to get territory name from ID
        self.board, self.continents, self.card_faces = self.gen_board() #gets board set up
        self.state = self.gen_init_state(steal_cards, turn_order) #gets an initial state
        self.turn_order = turn_order #order in which players take turns, includes # of players
        self.trade_vals = trade_vals #values for card set trade ins
        self.steal_cards = steal_cards #whether or not cards are taken after player defeat

    def play(self, debug=False):
        '''this is the main game loop'''

        num_players = len(self.players)

        troops = self.starting_troops()

        if self.has_gui:
            self.gui.recolor(self.state)

        for turn in self.turn_order:
            owned = self.get_owned_territories(turn)
            self.place_troops(turn, troops-len(owned))
            if self.has_gui:
                self.gui.recolor(self.state)

            
            

        #begin main game loop
        while not self.winner(debug):

            #whose turn is it?
            turn = self.turn_order[self.turn_count%num_players]

            #is this player defeated? If so skip turn
            while self.defeated(turn, debug):
                self.turn_count+=1
                turn = self.turn_order[self.turn_count%num_players]

            #perform recruitment
            self.recruitment_phase(turn)

            #perform attack
            self.attack_phase(turn)

            #if attacking won you the game stop
            if not self.winner(debug):
                #if game is not over perform reinforcement
                self.reinforce_phase(turn)

            #turn is over, increase turn count
            self.turn_count+=1

            
        #end game loop
        #exit message

        print("DEBUG end state",self.state)
        print("The game is over! Player",
                           self.turn_order[(self.turn_count-1)%num_players],
                           "won the game!")

    def recruitment_phase(self, player):
        '''perform recruitment phase'''
        
        #recruit troops for turn
        recruited = self.recruit_troops(player)

        #place recruited troops, update the game state to reflect placement
        self.place_troops(player,recruited)

        #does agent have a valid card trade in set?
        set_list,card_count = self.get_sets(player)

        #if agent does, prompt them for whether or not they want to trade in a set
        while len(set_list)!=0:
            recruited = self.trade_in(player, set_list, card_count)
            if recruited!=0:
                #increase number of trade ins
                self.state[-1]+=1

                #place newly recruited troops
                self.state = current_player.place_troops(recruited)
            else:
                set_list=[]

        #recruitment phase is over

    def attack_phase(self, player):
        '''perform attack phase'''

        current_player = self.players[player]
        targets = self.get_targets(player)
        choice = current_player.choose_attack(self.state, targets)

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        while choice!=False:

            #performs a single iteration of combat
            result = self.combat(choice)

            #result 1 if attacker wins, -1 if defender wins
            #0 if no result yet
            if result!=0:
                
                if result==1:
                    self.reward_card(player) #give player a card
                    attack_from,attack_to = choice
                    territories[attack_from][1]-=1
                    territories[attack_to][1]=1
                    territories[attack_to][0]=player

                    self.after_attack_reinforce(player,choice)

                    
                    
                    
                break

            else:
                current_player.continue_attack(self.state, choice)
        
        

    def reinforce_phase(self, player):
        '''perform reinforcement phase (Risk turn phase not RL)'''

        pass

        
    def id_names(self):
        """returns helpful 2-way dictionaries for territories"""
        
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

    def gen_board(self):
        """
        Generates the environment of the board
        """
        
        board = {
            0:[1,3,35],1:[2,3,4],2:[5,1,4,23],3:[0,4,1,6],4:[1,2,3,5,6,7],
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

        #Continent name as key, with a list containing
        #continent value as 1st element, and then nodes
        continents = {
            "Europe":[5,23,24,25,26,27,28,29],
            "N_America":[5,0,1,2,3,4,5,6,7,8],
            "Africa":[3,14,18,13,15,16,17],
            "Australia":[2,19,20,21,22],
            "Asia":[7,30,31,32,33,34,35,36,37,38,39,40,41],
            "S_America":[2,9,12,10,11]
            }


        #the army size presented on the front of the Risk card
        #99 is wild card
        card_faces = {0:1,1:10,2:5,3:1,4:5,5:10,6:1,7:10,8:5,9:10,10:10,
                      11:5,12:1,13:1,14:1,15:10,16:5,17:10,18:1,19:5,20:5,
                      21:10,22:1,23:1,24:5,25:10,26:10,27:5,28:5,29:1,30:10,
                      31:1,32:5,33:10,34:5,35:5,36:1,37:10,38:1,39:5,40:1,
                      41:10,42:99,43:99}

        return (board, continents, card_faces)

    def starting_troops(self):
        '''
        returns the amount of troops each player gets at start
        NOTE: rule variations here are that 2 players are
        getting 40. In reality this package is not supporting
        the 2 person game according to the rules

        All too many/too few player errors will throw a key error here
        '''
        return {2:40,3:35,4:30,5:25,6:20}[len(self.players)]

    def gen_init_state(self, steal_cards, turn_order, debug=False):
        '''
        generates the initial state of the game
        steal_cards: whether or not players aquire the cards of their opponents upon defeat
        turn_order: turn order of players, note: this is just passing through
        so that a full "state" can be represented in one tuple
        '''

        #debugging will force player number and order to be 0-5
        #so that this can be tested easier
        if debug:
            order = list(range(6))

        
        #initializes the initial state of the game
        #the game state is all the nodes, node owner, and army size per node
        territories = {
            0:[0,0],1:[0,0],2:[0,0],3:[0,0],4:[0,0],5:[0,0],6:[0,0],7:[0,0],8:[0,0],
            9:[0,0],10:[0,0],11:[0,0],12:[0,0],13:[0,0],14:[0,0],15:[0,0],16:[0,0],
            17:[0,0],18:[0,0],19:[0,0],20:[0,0],21:[0,0],22:[0,0],23:[0,0],24:[0,0],
            25:[0,0],26:[0,0],27:[0,0],28:[0,0],29:[0,0],30:[0,0],31:[0,0],32:[0,0],
            33:[0,0],34:[0,0],35:[0,0],36:[0,0],37:[0,0],38:[0,0],39:[0,0],40:[0,0],
            41:[0,0]
            }

        #initializes the cards pre-start of game with their owner
        #6=unused card, 7=used card (max of 6 player per game)
        cards = {
            0:6,1:6,2:6,3:6,4:6,5:6,6:6,7:6,8:6,9:6,
            10:6,11:6,12:6,13:6,14:6,15:6,16:6,17:6,18:6,19:6,
            20:6,21:6,22:6,23:6,24:6,25:6,26:6,27:6,28:6,29:6,
            30:6,31:6,32:6,33:6,34:6,35:6,36:6,37:6,38:6,39:6,
            40:6,41:6,42:6,43:6
            }

        # 0 for number of card sets turned in
        #this just packs the info into a state tuple that is used to begin the game
        return (steal_cards, turn_order, territories, cards, 0)

    def deal_territories(self):
        '''deals territories randomly, returns nothing'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        remaining = list(range(42)) #unallocated territories

        for index in range(42):
            
            player_id = turn_order[index%len(turn_order)]

            chosen = random.choice(remaining)

            remaining.remove(chosen)

            territories[chosen][0]=player_id
            territories[chosen][1]=1

        self.state = (steal_cards, turn_order, territories, cards, trade_ins)

    def winner(self, debug=False):
        '''checks the game state to see if the game is over'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        winner = True
        
        for t in territories:
            if territories[t][0]!=territories[0][0]:
                #there isn't a winner yet
                winner=False
                break

        if debug:
            print("Was a winner found?",winner)

        return winner

    def defeated(self, player, debug=False):
        '''checks if a player has any territories'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        defeated = True
        
        for t in territories:
            if territories[t][0]==player:
                #player has at least one territory
                defeated=False
                break

        if debug:
            print("Was player",player,"defeated?",defeated)

        return defeated

    def place_troops(self, player, troops):
        '''
        Place troops into owned territory
        takes in arguments the environment state and how many troops to place
        for each troop it will call choose_placement() with a valid list of
        territories to place troops
        returns the altered state
        '''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        current_player = self.players[player]

        for troop in range(troops):
            
            valid = []
            for t in territories:
                
                if territories[t][0]==player:
                    valid.append(t)

            chosen = current_player.choose_placement(valid, self.state, troops-troop)
            territories[chosen][1]+=1

        self.state = (steal_cards, turn_order, territories, cards, trade_ins)

    def get_owned_territories(self, player):
        '''returns a list of territories owned by the player'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        return [t for t in territories if territories[t][0]==player]

    def get_targets(self, player):
        '''
        returns a list of tuples with the first value being
        a valid territory to attack from and the second a
        potential target

        also adds False to the end (position -1) which represents
        choosing not to attack

        NOTE: the board is also a required argument, as it needs
        to know the connections to calculate valid attacks
        '''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        #get all owned territories
        owned = self.get_owned_territories(player)

        #get all owned territories with more than 1 troop
        valid = [t for t in owned if territories[t][1]>1]

        #generate a list of tuples representing all valid attack options
        attacks = []

        for t in valid:
            for link in self.board[t]:
                if link not in owned:
                    attacks.append((t,link))

        attacks.append(False)

        return attacks

    def combat(self, attack):
        '''does the standard dice roll combat for Risk for a given attack'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        attacker, defender = attack

        max_attack_troops = territories[attacker][1]
        max_defend_troops = territories[defender][1]

        defending = min((2, max_defend_troops))

        options = [x+1 for x in range(3) if max_attack_troops>x+1]

        attacker_player = self.players[territories[attacker][0]]

        attacking = attacker_player.choose_attack_size(self.state, options)

        a_rolls = []
        for x in range(attacking):
            a_rolls.append(random.randrange(1,7))

        d_rolls = []
        for x in range(defending):
            d_rolls.append(random.randrange(1,7))

        for roll in range(min((len(d_rolls),len(a_rolls)))):
            a = max(a_rolls)
            d = max(d_rolls)
            a_rolls.remove(a)
            d_rolls.remove(d)

            if a>d:
                max_defend_troops-=1
            else:
                max_attack_troops-=1

        territories[attacker][1] = max_attack_troops
        territories[defender][1] = max_defend_troops

        if max_defend_troops == 0:
            return 1
        
        if max_attack_troops == 1:
            return -1

        return 0

    def recruit_troops(self, player):
        '''
        this calculates and returns the number of troops the player
        recieves at the beginning of their turn not including card sets
        '''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        recruit = 0

        #get the territories this player controls
        t_owned = self.get_owned_territories(player)

        #count them
        t_count = len(t_owned)

        #Risk rules then floor divide by 3
        t_count = t_count//3

        #and you always get at least 3 troops from this
        if t_count<3:
            t_count=3

        #now add to amount recruited
        recruit+=t_count

        #calculate for continents
        for continent in self.continents:
            c_owned=True
            for territory in self.continents[continent][1:]:
                if territory not in t_owned:
                    c_owned=False

            #if you own the continent, then get the troops
            #allocated for that continent (stored in position 0)
            if c_owned:
                recruit += self.continents[continent][0]

        return recruit

    def get_sets(self, player, debug=False):
        '''
        now you have the total troops recruited from these areas
        but there is still the trade ins to consider
        what this will return is any combination of cards
        the player owns that may be traded in
        valid sets are
        any 3 of same kind
        1 for 1,5,10
        any 2 and a wild
        '''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        c_owned = [c for c in cards if cards[c]==player]

        if debug:
            print("DEBUG C_O:", c_owned)

        set_list = []

        one = []
        five = []
        ten = []
        wild = []
        for card in c_owned:
            if self.card_faces[card] == 1:
                one.append(card)
            elif self.card_faces[card] == 5:
                five.append(card)
            elif self.card_faces[card] == 10:
                ten.append(card)
            else:
                wild.append(card)

        if debug:
            print("DEBUG 1s:", one)
            print("DEBUG 5s:", five)
            print("DEBUG 10s:", ten)
            print("DEBUG Wilds:", wild)

        #this calculates 3 of same kind
        if len(one)>=3:
            #in cases such as these there is no need to consider 3+
            #since any 1 is as good as another 1
            #append the first 3, if there are more than 3
            #deal with it else where
            set_list.append(one[:3])
        if len(five)>=3:
            set_list.append(five[:3])
        if len(ten)>=3:
            set_list.append(ten[:3])

        #calculates one of each kind
        if len(one)>=2 and len(five)>=2 and len(ten)>=2:
            #either you have two
            set_list.append([one[0],five[0],ten[0]])
            set_list.append([one[1],five[1],ten[1]])
        elif len(one)>=1 and len(five)>=1 and len(ten)>=1:
            #or you have just one
            set_list.append([one[0],five[0],ten[0]])

        #calculates wildcard sets
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

        return (set_list, len(c_owned))

    def trade_in(self, player, set_list, card_count):
        '''
        trade in which arrangement of cards the agent wants to trade in
        NOTE: according to the rules if you have more than 5 cards you must
        trade in at least one set
        returns the amount of troops recruited
        '''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        if card_count>=5:
            must_trade=True
        else:
            must_trade=False

        current_player = self.players[player]

        chosen = current_player.choose_trade_in(self.state, self.trade_vals, set_list, must_trade)

        if chosen!=0:

            #set all traded in cards to 7, the 'unowned'
            for c in chosen:
                cards[c]=6

            #award the player troops equivalent to trade in val
            #if number of trade ins exceeds length of values
            #just award the last one
            if len(self.trade_vals)<trade_ins:
                trade_ins+=1
                return self.trade_vals[-1]
            else:
                trade_ins+=1
                return self.trade_vals[trade_ins-1]
            
        #if agent decides not to trade in a set, then no troops will be awarded
        return 0

    def reward_card(self, player):
        '''set's an unowned card to the player at random'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        #get all cards that aren't owned
        c_unowned = [c for c in cards if cards[c]==6]

        #choose one at random
        chosen = random.choice(c_unowned)

        #set that card to now owned by player
        cards[chosen] = player

    def players_choose_territories(self):
        '''for when territories are not dealt at random'''
        #players are prompted by turn order for a territory selection

        steal_cards, turn_order, territories, cards, trade_ins = self.state
        
        valid = list(range(42))
        for index in range(42):

            turn = self.turn_order[self.turn_count%len(self.players)]
            
            current_player = self.players[turn]
            chosen = current_player.pick_initial_territories(valid)

            territories[chosen]=[turn,1]

            valid.remove(chosen)

    def after_attack_reinforce(self, player, attack):
        '''this method handles reinforcement after attacking'''

        steal_cards, turn_order, territories, cards, trade_ins = self.state

        frm,to = attack
        
        divy_up = territories[frm][1]-1

        for t in range(divy_up):
            choice = self.players[player].after_attack_troops(self.state, frm, to, divy_up-t)
            territories[choice][1]+=1

    @staticmethod
    def standard_game(players, has_gui=False):
        '''
        generates a stadard game of Risk using a provided
        list of agent objects up to a max of 6 and a minimum of 2

        the gui is optional
            

        the rules it will use are as follows
        - random turn order
        - random territory assignment
        - traditional trade in values for Risk cards

        '''

        if len(players)>6 or len(players)<2:
            raise ValueError("Players must be between 2 and 6")

        turn_order = config.turn_order(len(players), 'r') #random turns
        trade_vals = config.get_trade_vals('s') #standard trade in vals
            
        env = Risk(players, turn_order, trade_vals, False, has_gui)

        env.deal_territories() #territories are assigned at random

        return env #the pre-game environment is now set up

    @staticmethod
    def custom_game(debug=False):
        '''the user chooses settings from console'''

        #settings
        players, deal, steal_cards = config.console_players()
        turn_order = config.turn_order(players)
        trade_values = config.console_trade_vals()
        player_list = config.console_get_players(players)

        if debug:
            print("Turn order is:",turn_order)

        #generate the environment with settings
        env = Risk(player_list, turn_order,trade_values,steal_cards)

        #set up pre-game territory allocation
        if deal:
            env.deal_territories()
        else:
            env.players_choose_territories()
            

        if debug:
            [print(x) for x in env.state]

        return env #the environment is now ready to begin playing

    
    
