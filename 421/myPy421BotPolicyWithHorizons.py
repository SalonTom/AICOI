# Local HackaGame:
import json
from statistics import mean
import sys
sys.path.insert( 1, __file__.split('tutos')[0] )

import hackagames.hackapy as hg
import random

f = open('player_policy.json')
possible_combinations = json.load(f)

input_output_file = open(r'input_output_421_2.txt', 'w+')

show_json = False

class AutonomousPlayer( hg.AbsPlayer ) :

    def __init__(self) -> None:
        self.current_game = []
        self.policy = {}
        self.game_dices = []

    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        test = 8
        # print( f'---\nWake-up player-{playerId} ({numberOfPlayers} players)')
        # print( gameConf )
    
    def perceive(self, gameState):
        self.horizon= gameState.child(1).flag(1)
        self.dices= gameState.child(2).flags()
        print( f'H: {self.horizon} DICES: {self.dices}')

    def decide(self):
        self.current_game = []
        actions= ['keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]
        # action= random.choice( actions )
        # print( f'Action: {action}' )

        # print(possible_combinations)
        # print([{"score" : self.calculate_score([int(x) for x in list(comb)]), "comb" : comb} for comb in possible_combinations['combinations']])


        if show_json : 
            action= random.choice( actions )
        else :
            action = possible_combinations[''.join([str(dice) for dice in self.dices])]

        # print( f'Action: {action}' )
        # best_turn_action, turn_score = self.best_action(self.dices)
        self.current_game.append(''.join([str(dice) for dice in self.dices]))
        print(f'{self.horizon} : {self.dices}')
        # self.current_game.append( str(self.horizon) )
        if self.horizon == 2:
            self.current_game.append( '2' )
        elif self.horizon == 1:
            self.current_game.append( '1' )
            
        self.current_game.append( str(action) )
        input_output_file.write( ", ".join( self.current_game ) )
        # print(self.current_game)

        return action  
    
    def sleep(self, result):
        # self.current_game.append( str(result) )
        input_output_file.write( f", {result}\n" )
        self.game_dices = []


        # print( f'--- Results: {str(result)}' )

# script :
if __name__ == '__main__' :
    player= AutonomousPlayer()
    results= player.takeASeat()
    # Analysis
    average= sum(results)/len(results)
    print( f"Average score: {average}")

    final_policy = {}

    input_output_file.close()

    if show_json :
        input_output_file = open(r'input_output_421.txt', 'r+')

        data_file = input_output_file.readlines()
        for line in data_file:
            line = line.split(', ')
            # print(line)

            if player.policy.get(line[0]) is None :
                player.policy[line[0]] =  {}
            
            if player.policy[line[0]].get(line[2]) is None:
                player.policy[line[0]][line[2]] = []

            player.policy[line[0]][line[2]].append(float(line[3][:len(line[3]) - 1]))
        

        for dice_combination in player.policy.keys():
            if final_policy.get(dice_combination) is None :
                final_policy[dice_combination] = ''
            
            actions_and_scores = player.policy[dice_combination]

            current_action = 'keep-keep-keep'
            max_score = 0

            for action in actions_and_scores.keys():
                # print(f'dices : {dice_combination} - occurences {actions_and_scores["keep-keep-keep"]}')
                scores = actions_and_scores[action]
                max_scores = max(scores)

                if max_scores > max_score:
                    max_score = max_scores
                    current_action = action
            
            final_policy[dice_combination] = current_action

        # player.policy = {}
        print('------',json.dumps(final_policy))
        # print(player.policy)