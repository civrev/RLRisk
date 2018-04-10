'''
This class represents the game environment (the board)
of Risk using standard World Domination ruleset
See instructions https://www.hasbro.com/common/instruct/risk.pdf
'''

import random
import numpy as np
from rlrisk.environment import config
from rlrisk.environment import gui

class Risk:
    '''Game Environment for Risk World Domination'''

    def __init__(self, players, turn_order, trade_vals, steal_cards=False, has_gui=False, verbose_gui=False):
        '''
        setting up for the game
        the arguments here are the rule settings for the game
        turn_order: order that players take turns (in a list)
        trade_vals: sequencial values of traded in card sets (also a list)
        random_deal: whether players pick their territories at game start or are assigned
        '''

        #house keeping for players
        for num,p in enumerate(players):
            p.pregame_setup(num, trade_vals, turn_order, steal_cards)

        self.has_gui = has_gui #whether or not the gui should be displayed
        self.verbose_gui = verbose_gui #how often the gui updates
            
        self.players = players #the agents that play the game
        self.turn_count = 0 #initialize turn count at 0
        self.node2name, self.name2node = self.id_names() #dictionaries to get territory name from ID
        self.board, self.continents, self.card_faces = self.gen_board() #gets board set up
        self.state = self.gen_init_state() #gets an initial state
        self.turn_order = turn_order #order in which players take turns, includes # of players
        self.trade_vals = trade_vals #values for card set trade ins
        self.steal_cards = steal_cards #whether or not cards are taken after player defeat
        self.con_rewards = self.continent_rewards() #rewards for owning continents
        self.troop_record = []
        self.owner_record = []
        self.card_record = []
        self.trade_in_record = []

        if has_gui:
            self.gui = gui.GUI()
            #self.gui.add_players(len(players))

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

            #record states
            owr,trr,cdr, trade = self.get_numpy_state(self.state)
            self.owner_record.append(owr)
            self.troop_record.append(trr)
            self.card_record.append(cdr)
            self.trade_in_record.append(trade)
 
            #whose turn is it?
            turn = self.turn_order[self.turn_count%num_players]

            #is this player defeated? If so skip turn
            while self.defeated(turn, debug):
                self.turn_count+=1
                turn = self.turn_order[self.turn_count%num_players]

            #perform recruitment
            self.recruitment_phase(turn)

            #update GUI
            if self.has_gui:
                self.gui.recolor(self.state)

            #perform attack
            self.attack_phase(turn)

            #update GUI
            if self.has_gui:
                self.gui.recolor(self.state)

            #if attacking won you the game stop
            if not self.winner(debug):
                #if game is not over perform reinforcement
                self.reinforce_phase(turn)

            #update GUI
            if self.has_gui:
                self.gui.recolor(self.state)

            #turn is over, increase turn count
            self.turn_count+=1

            
        #end game loop
        #exit message

        print("The game is over! Player",
                           self.turn_order[(self.turn_count-1)%num_players]+1,
                           "won the game!")

        if self.has_gui:
            #close gui
            self.gui.quit_game()

        #returns a log of game states at each turn start
        #along with the settings of the game
        return (np.array(self.owner_record),
                np.array(self.troop_record),
                np.array(self.card_record),
                np.array(self.trade_in_record),
                self.turn_order,
                self.steal_cards)

    def recruitment_phase(self, player):
        '''perform recruitment phase'''
        
        #recruit troops for turn
        recruited = self.recruit_troops(player)

        #place recruited troops, update the game state to reflect placement
        self.place_troops(player,recruited)

        #does agent have a valid card trade in set?
        set_list,card_count = self.get_sets(player)

        #if agent does, prompt them for whether or not they want to trade in a set
        if len(set_list)!=0:
            recruited = self.trade_in(player, set_list, card_count)
            if recruited!=0:
                #place newly recruited troops
                self.place_troops(player, recruited)
            else:
                set_list=[]

        #recruitment phase is over

    def attack_phase(self, player):
        '''perform attack phase'''

        current_player = self.players[player]
        targets = self.get_targets(player)
        choice = current_player.take_action(self.state, 1, targets)

        territories, cards, trade_ins = self.state

        #Notes whether or not they should recieve a card if they win
        first=True

        
        while choice!=False:

            #performs a single iteration of combat
            result = self.combat(choice)


            #result 1 if attacker wins, -1 if defender wins
            #0 if no result yet
            if result==-1:
                break
            elif result==1:

                #give player a card if first conquest this turn
                if first:
                    self.reward_card(player)

                #move troops into territory
                attack_from,attack_to = choice
                territories[attack_from][1]-=1
                territories[attack_to][1]=1
                loosing_player = territories[attack_to][0]
                territories[attack_to][0]=player

                if self.has_gui and self.verbose_gui:
                    self.gui.recolor(self.state)

                #repack
                self.state = (territories, cards, trade_ins)

                self.after_attack_reinforce(player,choice)
                #if player has enough troops, offer to extend the attack
                territories = self.state[0]
                if territories[attack_to][1]>1:
                    targets = self.get_targets(player,frm=attack_to)
                    choice = current_player.take_action(self.state, 1, targets)
                    first=False
                else:
                    choice=False

                if self.steal_cards:
                    #determines if the defender lost their last territory
                    if self.defeated(loosing_player):
                        #transfer all defender's cards to attacker
                        self.transfer_cards(loosing_player, player)

            else:
                temp = current_player.take_action(self.state, 2, (True, False))
                if not temp:
                    choice=temp

        
        

    def reinforce_phase(self, player):
        '''perform reinforcement phase (Risk turn phase not RL)'''

        current_player = self.players[player]
        owned = self.get_owned_territories(player)
        valid = [t for t in owned if self.state[0][t][1]>1]
        frm = current_player.take_action(self.state, 4, valid+[False])
        
        if frm != -1:
            options = self.map_connected_territories(frm, owned)
            #prevents getting empty sequence
            if len(options)==0:
                to = frm
            else:
                to = current_player.take_action(self.state, 5, options)
            self.during_reinforce(player,frm,to)

    @staticmethod
    def id_names():
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

    @staticmethod
    def continent_rewards():
        '''Returns the troop rewards for owning continents'''
        return {"Europe":5,"N_America":5,"Africa":3,"Australia":2,"Asia":7,"S_America":2}

    @staticmethod
    def gen_board():
        """
        Generates the environment of the board
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

        #Continent name as key, with a list containing
        #continent value as 1st element, and then nodes
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

    @staticmethod
    def gen_init_state(debug=False):
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
        x = [-1,0]
        territories = {
            0:list(x),1:list(x),2:list(x),3:list(x),4:list(x),5:list(x),6:list(x),7:list(x),8:list(x),
            9:list(x),10:list(x),11:list(x),12:list(x),13:list(x),14:list(x),15:list(x),16:list(x),
            17:list(x),18:list(x),19:list(x),20:list(x),21:list(x),22:list(x),23:list(x),24:list(x),
            25:list(x),26:list(x),27:list(x),28:list(x),29:list(x),30:list(x),31:list(x),32:list(x),
            33:list(x),34:list(x),35:list(x),36:list(x),37:list(x),38:list(x),39:list(x),40:list(x),
            41:list(x)
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
        return (territories, cards, 0)

    def deal_territories(self):
        '''deals territories randomly, returns nothing'''

        territories, cards, trade_ins = self.state

        remaining = list(range(42)) #unallocated territories

        for index in range(42):
            
            player_id = self.turn_order[index%len(self.turn_order)]

            chosen = random.choice(remaining)

            remaining.remove(chosen)

            territories[chosen][0]=player_id
            territories[chosen][1]=1

        self.state = (territories, cards, trade_ins)

    def winner(self, debug=False):
        '''checks the game state to see if the game is over'''

        territories, cards, trade_ins = self.state

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

        territories, cards, trade_ins = self.state

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

        territories, cards, trade_ins = self.state

        current_player = self.players[player]

        for troop in range(troops):
            
            valid = []
            for t in territories:
                
                if territories[t][0]==player:
                    valid.append(t)

            #troops-troop #how many troops they get, now removed
            #0 is place_troops_during_recruitment
            chosen = current_player.take_action(self.state, 0, valid)
            territories[chosen][1]+=1

            if self.has_gui and self.verbose_gui:
                self.gui.recolor(self.state)

        self.state = (territories, cards, trade_ins)

    def get_owned_territories(self, player):
        '''returns a list of territories owned by the player'''

        territories, cards, trade_ins = self.state

        return [t for t in territories if territories[t][0]==player]

    def get_targets(self, player, frm=-1):
        '''
        returns a list of tuples with the first value being
        a valid territory to attack from and the second a
        potential target

        also adds False to the end (position -1) which represents
        choosing not to attack

        NOTE: the board is also a required argument, as it needs
        to know the connections to calculate valid attacks
        '''

        territories, cards, trade_ins = self.state

        #get all owned territories
        owned = self.get_owned_territories(player)

        #get all owned territories with more than 1 troop
        if frm==-1:
            valid = [t for t in owned if territories[t][1]>1]
        else:
            #continuing attack onto other provinces
            valid = [frm]

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

        territories, cards, trade_ins = self.state

        attacker, defender = attack

        max_attack_troops = territories[attacker][1]
        max_defend_troops = territories[defender][1]

        defending = min((2, max_defend_troops))

        options = [x+1 for x in range(3) if max_attack_troops>x+1]

        attacker_player = self.players[territories[attacker][0]]
        attacker_player_number = territories[attacker][0]

        attacking = attacker_player.take_action(self.state, 3, options)

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
                attacking-=1
                max_attack_troops-=1

        #debugging check
        if max_attack_troops < 0 or max_defend_troops < 0:
            print(self.state)
            raise ValueError("Combat below zero")

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

        territories, cards, trade_ins = self.state

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
            for territory in self.continents[continent]:
                if territory not in t_owned:
                    c_owned=False

            #if you own the continent, then get the troops
            #allocated for that continent (stored in position 0)
            if c_owned:
                recruit += self.con_rewards[continent]

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

        territories, cards, trade_ins = self.state

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

    def trade_in(self, player, options, card_count):
        '''
        trade in which arrangement of cards the agent wants to trade in
        NOTE: according to the rules if you have more than 5 cards you must
        trade in at least one set
        returns the amount of troops recruited
        '''

        territories, cards, trade_ins = self.state

        if card_count>=5:
            must_trade=True
        else:
            must_trade=False
            options.append(0)

        current_player = self.players[player]
        
        chosen = current_player.take_action(self.state, 8, options)

        if chosen!=0:

            trade_ins+=1

            #repack state
            self.state = (territories, cards, trade_ins)

            #set all traded in cards to 7, the 'unowned'
            for c in chosen:
                cards[c]=6

            #award the player troops equivalent to trade in val
            #if number of trade ins exceeds length of values
            #just award the last one
            if len(self.trade_vals)<trade_ins:
                return self.trade_vals[-1]
            else:
                return self.trade_vals[trade_ins-1]
            
        #if agent decides not to trade in a set, then no troops will be awarded
        return 0

    def reward_card(self, player):
        '''set's an unowned card to the player at random'''

        territories, cards, trade_ins = self.state

        #get all cards that aren't owned
        c_unowned = [c for c in cards if cards[c]==6]

        #choose one at random
        chosen = random.choice(c_unowned)

        #set that card to now owned by player
        cards[chosen] = player

    def transfer_cards(self, from_player, to_player):
        '''Set's ownership of all cards from one player to another player'''

        territories, cards, trade_ins = self.state

        c_owned_from = [c for c in cards if cards[c]==from_player]
        c_owned_to = [c for c in cards if cards[c]==to_player]

        #transfer
        for c in c_owned_from:
            cards[c]=to_player

        #if cards now owned greater than or equal to 6, force player to trade in
        if len(c_owned_from)+len(c_owned_to)>=6:
            set_list, card_count = self.get_sets(to_player)
            while card_count>=6:
                #force them to trade in and distribute troops until
                #they are below 6
                troop_reward = self.trade_in(to_player, set_list, card_count)
                self.place_troops(to_player, troop_reward)
                card_count-=3

    def players_choose_territories(self):
        '''for when territories are not dealt at random'''
        #players are prompted by turn order for a territory selection

        territories, cards, trade_ins = self.state

        turn_count=0
        
        valid = list(range(42))
        for index in range(42):

            turn = turn_order[turn_count%len(self.players)]
            
            current_player = self.players[turn]
            chosen = current_player.choose_initial_territories(valid, self.state)

            territories[chosen]=[turn,1]

            valid.remove(chosen)
            turn_count+=1

            #repack state
            self.state = (territories, cards, trade_ins)

    def after_attack_reinforce(self, player, attack):
        '''this method handles reinforcement after attacking'''

        territories, cards, trade_ins = self.state

        frm,to = attack
        
        divy_up = territories[frm][1]-1
        territories[frm][1] = 1

        for t in range(divy_up):
            #divy_up-t #troops to distribute after an attack
            #repack state
            self.state = (territories, cards, trade_ins)
            choice = self.players[player].take_action(self.state, 7, (frm, to))
            if choice==to:
                territories[to][1]+=1
            else:
                territories[frm][1]+=1

            if self.has_gui and self.verbose_gui:
                self.gui.recolor(self.state)

    def during_reinforce(self, player, frm, to):
        '''this method handles reinforcement'''

        territories, cards, trade_ins = self.state
        divy_up = territories[frm][1]-1
        territories[frm][1] = 1

        for t in range(divy_up):
            #repack state
            self.state = (territories, cards, trade_ins)
            #divy_up-t #troops left to distribute
            choice = self.players[player].take_action(self.state, 6, (frm, to))
            if choice==to:
                territories[to][1]+= 1
            else:
                territories[frm][1]+= 1

            if self.has_gui and self.verbose_gui:
                self.gui.recolor(self.state)

    def map_connected_territories(self, frm, owned):
        '''
        Returns a list of territories that are connected to a
        specific territory contigously via same ownership
        '''

        owned = set(owned)
        connections = list(owned.intersection(set(self.board[frm])))
        for x in range(42):
            if x < len(connections):
                c_connections = owned.intersection(set(self.board[connections[x]]))
                #weed out visited ones and concatenate them to connections
                connections += list(c_connections - set(connections))

        return connections
        

    @staticmethod
    def standard_game(players, has_gui=False, verbose_gui=False):
        '''
        generates a stadard game of Risk using a provided
        list of agent objects up to a max of 6 and a minimum of 2

        the gui is optional
            

        the rules it will use are as follows
        - random turn order
        - random territory assignment
        - traditional trade in values for Risk cards
        - steal cards upon player defeat

        '''

        if len(players)>6 or len(players)<2:
            raise ValueError("Players must be between 2 and 6")

        steal_cards=True
        turn_order = config.turn_order(len(players), 'r') #random turns
        trade_vals = config.get_trade_vals('s') #standard trade in vals
        env = Risk(players, turn_order, trade_vals, steal_cards, has_gui, verbose_gui)

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

    @staticmethod
    def get_numpy_state(state):
        '''
        Returns the state as a 4 tuple numpy arrays + trade ins
        Notable missing Steal Cards, and Turn Order normally included in this
        '''
        territories, cards, trade_ins = state

        owners = np.empty([42,], dtype='int32')
        troops = np.empty([42,], dtype='int32')
        card_owners = np.empty([44,], dtype='int32')
        for num in range(42):
            owners[num]=territories[num][0]
            troops[num]=territories[num][1]
            card_owners[num]=cards[num]
        card_owners[42]=cards[42]
        card_owners[43]=cards[43]

        return (owners, troops, card_owners, trade_ins)

    @staticmethod
    def parse_numpy_array(array_tuple):
        '''
        Returns the game state (minus steal cards and turn order)
        from a numpy array tuple
        '''
        owners, troops, card_owners, trade_ins = array_tuple

        territories = {}
        cards = {}

        for num in range(42):
            territories[num]=[owners[num]]
            territories[num].append(troops[num])
            cards[num]=card_owners[num]
        cards[42]=card_owners[42]
        cards[43]=card_owners[43]

        return (territories, cards, trade_ins)
    
