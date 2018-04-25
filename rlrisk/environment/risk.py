'''
This module holds the Risk Class which is the
framework from which game environment objects can
be created
'''

import random
import itertools
import math
import numpy as np
from rlrisk.environment import config, GUI

class Risk(object):
    """Game Environment for Risk World Domination Ruleset"""

    def __init__(self, agents, turn_order="c", trade_vals="s",
                 steal_cards=False, deal=True, fortify_adjacent=True,
                 has_gui=False, verbose_gui=False, turn_cap=math.inf):
        """
        Risk Constructor

        Sets up the game environment with chosen ruleset. Players will be given
        the rules as static information, and will also instantiate the gui
        if set to do so. All optional parameters are by default the standard
        ruleset for World Domination.

        Required Parameters
        -------------------
        agents : List, 2 <= len(agents) <= 6
            List of agents that will be the players in the game. Agents must
            be BaseAgent or subclass of BaseAgent, or at least follow the general
            structure of that class

        Optional Parameters
        -------------------
        turn_order : String "c"/"r" or List
            Options for the turn order in the game.
            "c" = Clockwise (as in increasing) order from random player
            "r" = Random turn order. Turn order will not be increasing, but will
                  remain constant throughout game
            List = List of custom turn order for index of agents
                   Example [0, 2, 3, 1] Player 1 will go first, followed by player 3
                   then player 4 and then player 2

            "c" by default

        trade_vals : String "s"/"1" (letter one) or Generator
            Options for the sequence that generate card set trade in rewards
            "s" = Standard Risk trade in rewards
            "1" = Increasing by 1
            Generator = Generator representing a unique sequence of integers to reward

            A copy of the generator used to get trade values is in
            instance variable gen_backup

            "s" by default

        steal_cards : boolean
            Whether or not defeated player's card go to the player that defeated them

            True by default

        deal : boolean
            Whether or not players are randomly alloted territories or they pick them
            one by one

            True by default

        fortify_adjacent : boolean
            Whether players may only fortify during fortify phase from adjacent
            territories. Setting False will allow contiguous fortifying

            True by default

        has_gui : boolean
            Whether or not to use the Pygame gui to observe actions during game

            False by default

        verbose_gui : boolean
            Whether or not to update Pygame gui in between individual troop allocations
            useful when playing as Human agent. Considerably slows down the game.

            False by default

        turn_cap : integer
            Stops the game if it exceeds a given number of turns

            Infinity by default

        Returns
        -------
        None

        """

        if len(agents) < 2 or len(agents) > 6:
            raise ValueError("Invalid size for agents. Must be 2<=len(agents)<=6")

        self.players = agents

        if isinstance(turn_order, str):
            self.turn_order = config.get_turn_order(len(agents), turn_order)
        else:
            self.turn_order = turn_order

        if isinstance(trade_vals, str):
            self.orig_trade_vals = config.get_trade_vals(trade_vals)
        else:
            self.orig_trade_vals = trade_vals

        #A backup of the trade vals generator
        self.trade_vals, self.gen_backup = itertools.tee(self.orig_trade_vals)

        self.steal_cards = steal_cards
        self.fortify_adjacent = fortify_adjacent
        self.has_gui = has_gui
        self.verbose_gui = verbose_gui
        self.deal = deal
        self.turn_cap = turn_cap

        self.turn_count = 0
        self.game_over = False
        self.board, self.continents, self.card_faces, self.con_rewards = self.gen_board()
        self.state = self.gen_init_state()
        self.node2name, self.name2node = self.id_names()
        self.record = {0:[], 1:[], 2:[], 3:[]}

        if has_gui:
            self.gui = GUI()

        for plr_num, player in enumerate(agents):
            setup_values = [plr_num, itertools.tee(self.orig_trade_vals, 1),
                            turn_order, steal_cards, self.board,
                            self.continents, self.con_rewards]
            player.pregame_setup(setup_values)

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
        6 value tuple
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

        #place starting troops
        self.place_starting_troops()
        self.gui_update()

        #Main game loop
        while not self.game_over:
            #record state
            self.record_state()

            #get the index of player whose turn it is
            turn = self.turn_order[self.turn_count%num_players]

            #check if player is defeated, if so skip turn
            while self.players[turn].defeated:
                self.turn_count += 1
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
            self.fortify_phase(turn)
            self.gui_update()

            #increase turn count
            self.turn_count += 1

            if self.turn_count > self.turn_cap:
                self.game_over = True
                break

        #exit message
        if self.turn_count > self.turn_cap:
            print("The game is over! Turn Cap was reached.")
        else:
            winner = self.turn_order[self.turn_count%num_players] + 1
            print("The game is over! Player", winner, "won the game!")

        #quit gui
        self.gui_update()

        return (np.array(self.record[0]),
                np.array(self.record[1]),
                np.array(self.record[2]),
                np.array(self.record[3]),
                self.turn_order,
                self.steal_cards)

    def recruitment_phase(self, player):
        """
        Executes recruitment phase

        Collects the number of troops a player should recieve at turn start,
        then asks the player to distribute them. Afterwards if the player has
        cards to trade in they may choose to (or must) do so at this time.

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        None

        """

        recruited = self.calculate_recruits(player)

        self.place_troops(player, recruited)

        #gets card sets, if they have card sets ask the player if they want to trade
        set_list, card_count = self.get_sets(player)
        if len(set_list) != 0:
            recruited = self.trade_in(player, set_list, card_count)
            #zero is they chose not to trade in a set
            if recruited != 0:
                self.place_troops(player, recruited)

    def attack_phase(self, player):
        """
        Executes attack phase

        Collects the IDs of valid territories to attack from, and where they
        can attack to. Prompts the user for a choice of attack, or not. If
        they choose an attack, attack (conduct combat).

        If the outcome is victory, reassign territories, prompt player to move
        troops from attacking territory to defeated territory, and then if there are
        enough troops in the new territory, ask if they want to make another
        attack from that territory.

        If the outcome is defeat, no further action will be taken.

        If the outcome is not yet decided, prompt the player for an oppertunity
        to cancel the attack

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        None

        """

        territories = self.state[0]

        targets = self.get_targets(player)
        choice = self.players[player].take_action(self.state, 1, targets)

        card_eligible = True

        while choice != False:

            defending_player = territories[choice[1], 0]

            #-1 is defeat, 1 is victory, 0 is undecided
            result = self.combat(choice)

            if result == -1:
                break
            elif result == 0:
                #agent asked if they want to continue attacking after undecided
                press_attack = self.players[player].take_action(self.state, 2, (True, False))
                if not press_attack:
                    break
            else:
                #victory
                if card_eligible:
                    self.reward_card(player)
                    card_eligible = False

                self.after_attack_reinforce(player, choice)

                #check if this defeated the other player
                self.defeated(defending_player, player)

                territories = self.state[0]

                if territories[choice[1], 1] > 1:
                    targets = self.get_targets(player, frm=choice[1])
                    choice = self.players[player].take_action(self.state, 11, targets)
                else:
                    break

            self.gui_update(True)

    def fortify_phase(self, player):
        """
        Executes fortify phase

        Generates all territories elegible to gather troops
        from, and prompts the player to choose where to fortify from.
        Then gathers elegible provinces to place troops from the chosen
        territory. Such provinces are elegible if they are part of
        contiguously owned territory with chosen province, only if rules
        allow for this. Otherwise only adjacent owned territories are elegible.
        Player is then prompted to choose the destination for the troops.
        Once the source and destination are decided the player is prompted
        for where to distribute the troops from the source
        (either in the same territory or in the destination territory)
        one by one. Players may also choose not to fortify their territories

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        None

        """

        territories = self.state[0]
        owned = self.get_owned_territories(player)
        valid_source = owned[np.where(territories[owned, 1] > 1)[0]].tolist()
        source = False
        if len(valid_source) > 0:
            source = self.players[player].take_action(self.state, 4, valid_source+[False])

        if source != False:
            if self.fortify_adjacent:
                valid_destinations = np.intersect1d(owned, self.board[source])
            else:
                valid_destinations = self.map_connected_territories(source, owned)

            #Could have chosen a dead-end province
            if len(valid_destinations) > 0:

                destination = self.players[player].take_action(self.state, 5, valid_destinations)

                self.fortify(player, source, destination)

    def record_state(self):
        """
        Records the state of the game

        Creates a list of the game state at the beginning of each turn.
        At the end of the game, these are changed to numpy arrays and
        returned.

        The game state is the 3 value tuple, but the recording of the game
        state breaks the 1st value (the territories with owner and troop count)
        into 2 seperate arrays, the owner and troop count

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        self.record[0].append(np.copy(self.state[0][:, 0]))
        self.record[1].append(np.copy(self.state[0][:, 1]))
        self.record[2].append(np.copy(self.state[1]))
        self.record[3].append(self.state[2])

    def place_starting_troops(self):
        """
        Handles placing troops at game start

        Gathers the number of starting troops alloted for the number of players,
        subtracts the number of territories each player recieved, and then asks
        the players to place troops one by one totating by turn order

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        troops_to_place = {}
        s_troops = self.starting_troops(len(self.players))
        for player_index in self.turn_order:
            troops_per = s_troops - self.get_owned_territories(player_index).shape[0]
            troops_to_place[player_index] = troops_per

        for player_index in itertools.cycle(self.turn_order):
            if player_index in troops_to_place:
                self.place_troops(player_index, 1, 10)
                troops_to_place[player_index] -= 1
                if troops_to_place[player_index] == 0:
                    troops_to_place.pop(player_index)
                    if len(troops_to_place) == 0:
                        break

    def fortify(self, player, source, destination):
        """
        Handles transfer of troops during fortification

        Calculates all troops from source province elegible to transfer
        to destination province, and then prompts agent to place them
        one by one

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        source : integer
            Territory ID of source of troop transfer

        destination : integer
            Territory ID of where troops are transfering to

        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state

        distribute = territories[source, 1] - 1
        territories[source, 1] = 1

        for troop in range(distribute):
            #repack state
            self.state = (territories, cards, trade_ins)

            choice = self.players[player].take_action(self.state, 6, (source, destination))

            if choice == destination:
                territories[destination][1] += 1
            else:
                territories[source][1] += 1

            self.gui_update(True)

    def map_connected_territories(self, source, owned):
        """
        Generates all territories connected to a given territory owned by a player

        Performs breadth first search on the board to construct the breadth
        first traversal of the spanner tree rooted at the source province.
        Only counts territory owned by the same player.

        Required Parameters
        -------------------
        source : integer
            Territory ID to get territories connected to with same owner

        owned : List
            List of territory IDs owned by same player as source

        Returns
        -------
        List :
            List of Territories ID that are part of contiguous owned territory

        """

        contiguous = [source]

        index = 0
        while True:
            for terr in self.board[contiguous[index]]:
                if terr in owned and terr not in contiguous:
                    contiguous.append(terr)
            index += 1
            if index >= len(contiguous):
                break

        return contiguous

    def get_targets(self, player, frm=-1):
        """
        Generates all valid attack options for a player

        Gets provinces owned by enemies that are adjacent to provinces the
        player owns that have at least 2 troops in them

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Optional Parameters
        -------------------
        frm : integer
            The territory ID of finding valid targets of attacks launched
            from a single territory

        Returns
        -------
        List of 2 value tuples :
            A list of all valid attacks. A valid attack is a tuple
            of (attacking_from, attacking_to) territory IDs.
            Also last value is always False, as player always has the
            choice not to attack

        """

        territories = self.state[0]

        owned = self.get_owned_territories(player)

        if frm == -1:
            valid_from = owned[np.where(territories[owned, 1] > 1)[0]]
        else:
            valid_from = [frm]

        attacks = []
        for vf_terr in valid_from:
            links = set(self.board[vf_terr])
            valid_to = links - set(owned)
            for vt_terr in valid_to:
                attacks.append((vf_terr, vt_terr))

        attacks.append(False)

        return attacks

    def combat(self, attack):
        """
        Performs combat for a given attack

        Calculates the maximum number of troops each player has to invested in the
        attack, defenders always use the max available (up to 2 troops) while the
        attacker may choose how many troops to risk in the attack (up to 3).
        The attacking player is prompted for this choice. Once the number of troops
        that will do battle are known, a 6 sided die will be emulated for each
        troop on each side of combat. The highest pairs of die from each side
        will be compared and the greater of these will be considered the victor
        and will keep that troop while the looser will loose 1 troop. In the event
        of a tie the defender always wins. The remaining troops will be updated
        to the territories at the end of a single round of combat, and if the
        attack is successful then the territory will be trasfered to them and
        the number of troops they risked that remain will move into them.

        Required Parameters
        -------------------
        attack : 2 integer tuple
            The territory IDs of (attacking_from, attacking_to)

        Returns
        -------
        integer :
            -1 if the attack ended in failure
             0 if attack is still undecided
             1 if attack resulted in victory

        """

        territories, cards, trade_ins = self.state

        attacking_from, attacking_to = attack

        max_attack_troops = territories[attacking_from, 1]
        max_defend_troops = territories[attacking_to, 1]

        #calculate defending troops, and options for attacking troops
        defending_troops = min((2, max_defend_troops))
        options = [x + 1 for x in range(3) if max_attack_troops > x + 1]

        #prompt attacker for how many troops to risk
        attacking_player_index = territories[attacking_from, 0]
        attacking_player = self.players[attacking_player_index]
        attacking_troops = attacking_player.take_action(self.state, 3, options)

        #emulate 6 sided dice
        a_rolls = []
        for roll in range(attacking_troops):
            a_rolls.append(random.randrange(1, 7))

        d_rolls = []
        for roll in range(defending_troops):
            d_rolls.append(random.randrange(1, 7))

        #compare highest pairs
        for roll in range(min((len(d_rolls), len(a_rolls)))):
            highest_a = max(a_rolls)
            highest_d = max(d_rolls)
            a_rolls.remove(highest_a)
            d_rolls.remove(highest_d)

            if highest_a > highest_d:
                max_defend_troops -= 1
            else:
                attacking_troops -= 1
                max_attack_troops -= 1

        if max_defend_troops == 0:
            territories[attacking_from, 1] = max_attack_troops-attacking_troops
            territories[attacking_to, 1] = attacking_troops
            territories[attacking_to, 0] = attacking_player_index
            result = 1
        elif max_attack_troops == 1:
            territories[attacking_from, 1] = max_attack_troops
            result = -1
        else:
            territories[attacking_from, 1] = max_attack_troops
            territories[attacking_to, 1] = max_defend_troops
            result = 0

        #repack state
        self.state = territories, cards, trade_ins

        return result

    def reward_card(self, player):
        """
        Deals a random card to a player

        Assigns an unowned card to a given player

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players to recieve a card

        Returns
        -------
        None

        """
        territories, cards, trade_ins = self.state

        unowned = np.where(cards[cards == 6])[0]
        cards[np.random.choice(unowned)] = player

        #repack state
        self.state = (territories, cards, trade_ins)

    def after_attack_reinforce(self, player, attack):
        """
        Handles moving troops into newly acquired territory

        Asks the agent to place troops from the attacking territory
        to the new territory (or not) one by one

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players to recieve a card

        attack : 2 integer tuple
            The territory IDs of (attacking_from, attacking_to)

        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state

        att_frm, att_to = attack

        divy_up = territories[att_frm, 1]-1
        territories[att_frm, 1] = 1

        for troop in range(divy_up):
            #repack state
            self.state = (territories, cards, trade_ins)
            choice = self.players[player].take_action(self.state, 7, attack)
            if choice == att_to:
                territories[att_to, 1] += 1
            else:
                territories[att_frm, 1] += 1
            self.gui_update(True)

    def defeated(self, victim, conquerer):
        """
        Checks if a player is defeated

        Checks defeated player for any territories in their posession.
        If the player doesn't own any territories, mark them as defeated
        and then change all their cards to either go back into the deck
        or get passed on to the player that defeated them based on rules
        at game start. If players do recieve defeated player's cards then
        if they possess 6 or more cards after stealing them, require that
        they trade them in down to 4 or less cards. If player has fewer
        than 6 cards they must wait until their next turn to trade in.

        Required Parameters
        -------------------
        victim : integer
            The index of the agent checking if defeated in self.players

        conquerer : integer
            The index of the agent that defeated them in self.players

        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state

        if victim not in territories[:, 0]:
            #they own no territories, so they are defeated
            self.players[victim].defeated = True

            if not self.steal_cards:
                cards[cards == victim] = 6
            cards[cards == victim] = conquerer

            #repack state
            self.state = (territories, cards, trade_ins)

            set_list, cards_owned = self.get_sets(conquerer)
            first_trade = True
            while (first_trade and cards_owned > 5) or (not first_trade and cards_owned > 4):
                troops_awarded = self.trade_in(conquerer, set_list, cards_owned)
                self.place_troops(conquerer, troops_awarded)
                set_list, cards_owned = self.get_sets(conquerer)
                first_trade = False

    def winner(self):
        """
        Checks if the game is over

        Checks to see if all territories are owned by the same player,
        if so the game is over

        Required Parameters
        -------------------
        None

        Returns
        -------
        boolean :
            Whether or not the game has a winner

        """

        territories = self.state[0]
        return np.array_equal(territories[:, 0], np.repeat(territories[0, 0], len(self.board)))

    def get_owned_territories(self, player):
        """
        Finds all territories owned by the player

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        (?,) Numpy Array:
            The IDs of territories owned by the player

        """

        territories = self.state[0]
        return np.where(territories[:, 0] == player)[0]

    def calculate_recruits(self, player):
        """
        Calculates the number of troops recruited at turn start

        Sums troop bonuses based on territories own and continent bonuses

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        integer :
            The number of troops to be recruited

        """

        territories_owned = self.get_owned_territories(player)

        #Risk rules say # of owned territories then floor division by 3
        recruitment = len(territories_owned) // 3

        #you always get at least 3
        if recruitment < 3:
            recruitment = 3

        #Calculate for continents
        for continent in self.continents:
            c_owned = True
            for territory in self.continents[continent]:
                if territory not in territories_owned:
                    c_owned = False

            if c_owned:
                recruitment += self.con_rewards[continent]

        return recruitment

    def place_troops(self, player, troops, action_code=0):
        """
        Place troops into owned territory

        Prompts the player for a territory to place troops one at a time

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        troops :
            Number of troop the player must place

        Optional Parameters
        -------------------
        action_code : integer
            Number representing what kind of action the agent is being asked
            to perform.

            0 by default

        Returns
        -------
        None

        """

        territories, cards, trade_ins = self.state
        current_player = self.players[player]

        for troop in range(troops):
            valid = self.get_owned_territories(player)
            chosen = current_player.take_action(self.state, action_code, valid)
            territories[chosen][1] += 1
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
        -------------------
        player : integer
            The index of the agent in self.players

        Returns
        -------
        List of Lists:
            All the unique arrangements of card that can be traded in

        integer :
            The number of cards a player owns

        """

        cards = self.state[1]

        cards_owned = np.where(cards == player)[0]

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
        if len(one) >= 3:
            set_list.append(one[:3])
        if len(five) >= 3:
            set_list.append(five[:3])
        if len(ten) >= 3:
            set_list.append(ten[:3])

        #one of each kind
        if len(one) >= 1 and len(five) >= 1 and len(ten) >= 1:
            set_list.append([one[0], five[0], ten[0]])

        #wild card sets
        for card in wild:
            if len(one) >= 2:
                #two of ones
                set_list.append([one[0], one[1], card])
            if len(five) >= 2:
                #two of fives
                set_list.append([five[0], five[1], card])
            if len(ten) >= 2:
                #two of tens
                set_list.append([ten[0], ten[1], card])
            if len(one) != 0 and len(five) != 0:
                #one 1 and one 5
                set_list.append([one[0], five[0], card])
            if len(one) != 0 and len(ten) != 0:
                #one 1 and one 10
                set_list.append([one[0], ten[0], card])
            if len(ten) != 0 and len(five) != 0:
                #one 5 and one 10
                set_list.append([ten[0], five[0], card])

        return (set_list, len(cards_owned))

    def trade_in(self, player, options, card_count):
        """
        Handles players trading in card sets

        Prompts the player for what arrangement of cards they want to
        trade in, and if they have less than 5 cards, they may choose
        not to trade in a card set.

        Required Parameters
        -------------------
        player : integer
            The index of the agent in self.players

        options : List
            A list of valid card sets for the player to trade in

        card_count : integer
            The number of cards owned by the player

        Returns
        -------
        integer :
            The number of troops awarded for trading in card sets

        """

        territories, cards, trade_ins = self.state

        #if they can choose not to trade, add False as an option representing this
        if card_count < 5:
            options.append(False)

        chosen = self.players[player].take_action(self.state, 8, options)

        troops_awarded = 0

        if chosen != False:
            trade_ins += 1
            #place cards traded in back in deck
            cards[chosen] = 6

            #award troops
            troops_awarded = next(self.trade_vals)

            #update state
            territories, cards, trade_ins = self.state
            trade_ins += 1
            self.state = (territories, cards, trade_ins)

        return troops_awarded

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

        remaining = list(self.board.keys())

        for index in range(len(self.board.keys())):

            turn = self.turn_order[index % len(self.turn_order)]

            if self.deal:
                chosen = random.choice(remaining)
            else:
                chosen = self.players[turn].take_action(self.state, 9, remaining)

            remaining.remove(chosen)

            territories[chosen, 0] = turn
            territories[chosen, 1] = 1

            self.state = (territories, cards, trade_ins)


    def gui_update(self, verbose=False):
        """
        Updates the GUI based on initial preferences

        Normal GUI updates occur after every phase of a player's turn
        while verbose GUI updates occur thoughout each phase
        which is very helpful when testing as a Human agent

        Optional Parameters
        -------------------
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
            0:[1, 3, 35], 1:[0, 2, 3, 4], 2:[5, 1, 4, 23], 3:[0, 4, 1, 6], 4:[1, 2, 3, 5, 6, 7],
            5:[2, 4, 7], 6:[3, 4, 7, 8], 7:[5, 4, 6, 8], 8:[6, 7, 9], 9:[8, 10, 11],
            10:[9, 12, 11, 13], 11:[10, 12, 9], 12:[10, 11], 13:[10, 14, 16, 28, 29, 15],
            14:[13, 15, 28, 30], 15:[13, 16, 17, 14, 30, 18], 16:[13, 15, 17], 17:[16, 15, 18],
            18:[17, 15], 19:[41, 20, 21], 20:[22, 21, 19], 21:[22, 19, 20], 22:[20, 21],
            23:[2, 24, 25], 24:[23, 25, 27, 29], 25:[23, 27, 26, 24], 26:[25, 27, 28, 30, 31, 32],
            27:[26, 28, 29, 25, 24], 28:[29, 27, 26, 30, 13, 14], 29:[13, 28, 27, 24],
            30:[31, 40, 14, 15, 26, 28], 31:[32, 30, 26, 40, 39], 32:[31, 26, 33, 39],
            33:[32, 39, 37, 34, 36], 34:[33, 36, 35], 35:[38, 34, 36, 0], 36:[35, 34, 33, 37],
            37:[36, 38, 39, 33, 35], 38:[35, 37], 39:[31, 37, 33, 41, 40, 32], 40:[39, 41, 31, 30],
            41:[39, 40, 19]
            }

        continents = {
            "Europe":[23, 24, 25, 26, 27, 28, 29],
            "N_America":[0, 1, 2, 3, 4, 5, 6, 7, 8],
            "Africa":[14, 18, 13, 15, 16, 17],
            "Australia":[19, 20, 21, 22],
            "Asia":[30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41],
            "S_America":[9, 12, 10, 11]
            }


        #the army size presented on the front of the Risk card
        #99 is wild card
        card_faces = {0:1, 1:10, 2:5, 3:1, 4:5, 5:10, 6:1, 7:10, 8:5, 9:10, 10:10,
                      11:5, 12:1, 13:1, 14:1, 15:10, 16:5, 17:10, 18:1, 19:5, 20:5,
                      21:10, 22:1, 23:1, 24:5, 25:10, 26:10, 27:5, 28:5, 29:1, 30:10,
                      31:1, 32:5, 33:10, 34:5, 35:5, 36:1, 37:10, 38:1, 39:5, 40:1,
                      41:10, 42:99, 43:99}

        continent_rewards = {"Europe":5, "N_America":5, "Africa":3,
                             "Australia":2, "Asia":7, "S_America":2}

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
            "Alaska", "NW_Territory", "Greenland", "Alberta",
            "Ontario", "Quebec", "W_US", "E_US", "C_America",
            #South America
            "Venezuela", "Brazil", "Peru", "Argentina",
            #Africa
            "N_Africa", "Egypt", "E_Africa", "Congo", "S_Africa", "Madagascar",
            #Australia
            "Indonesia", "New_Guinea", "W_Australia", "E_Australia",
            #Europe
            "Iceland", "Great_Britain", "Scandanavia",
            "Ukraine", "N_Europe", "S_Europe", "W_Europe",
            #Asia
            "Mid_East", "Afghanistan", "Ural", "Siberia",
            "Yakutsk", "Kamchatka", "Irkutsk", "Mongolia",
            "Japan", "China", "India", "Siam"]

        node2name = {}
        for num, name in enumerate(names):
            node2name[num] = name

        name2node = {}
        for num, name in enumerate(names):
            name2node[name] = num

        return (node2name, name2node)

    @staticmethod
    def starting_troops(players):
        """
        Get the number of starting troops for each player

        2 player variation from rules is that they get 40 troops
        in place of 'neutral 3rd player'

        Required Parameters
        -------------------
        players : integer
            The number of players in the game

        Returns
        -------
        integer
            The number a troops each player should start with

        """
        return {2:40, 3:35, 4:30, 5:25, 6:20}[players]

    @staticmethod
    def gen_init_state(board_size=42):
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
        territories = np.array([territory]*board_size)
        cards = np.repeat(6, 44)
        return (territories, cards, 0)

