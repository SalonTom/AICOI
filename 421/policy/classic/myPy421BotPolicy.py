# Local HackaGame:
import json
from statistics import mean
import sys
sys.path.insert( 1, __file__.split('421')[0] )

import hackagames.hackapy as hg
import random

f = open('player_policy.json')
possible_combinations = json.load(f)

input_output_file = open(r'input_output_421.txt', 'w+')

show_json = False

class AutonomousPlayer( hg.AbsPlayer ) :

    def __init__(self) -> None:
        self.current_game = []
        self.policy = {}

    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        test = 8
        # print( f'---\nWake-up player-{playerId} ({numberOfPlayers} players)')
        # print( gameConf )
    
    def perceive(self, gameState):
        self.horizon= gameState.child(1).flag(1)
        self.dices= gameState.child(2).flags()
        # print( f'H: {self.horizon} DICES: {self.dices}')

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
        self.current_game.append( str( self.horizon ) )
        self.current_game.append( str(action) )

        return action  
    
    def sleep(self, result):
        self.current_game.append( str(result) )

        input_output_file.write( ", ".join( self.current_game ) + '\n')

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

            if int(line[1]) <= 1 :
                # Init the state in the dict ex : { '421' : {} }
                if player.policy.get(line[0]) is None :
                    player.policy[line[0]] =  {}
                
                state = line[0]
                
                # Init the action for the state in the dict ex : { '421' : { 'keep-keep-keep' } }
                if player.policy[state].get(line[2]) is None:
                    player.policy[state][line[2]] = []
                
                action = line[2]

                action_score = line[3][:len(line[3]) - 1]
                player.policy[state][action].append(float(action_score))

        for state in player.policy.keys():
            if final_policy.get(state) is None :
                final_policy[state] = ''

            best_action = 'roll-roll-keep'
            best_state_average_score = 0

            for action in player.policy[state].keys():
                state_action_score = player.policy[state][action]

                average_action_score = mean(state_action_score)

                if (average_action_score > best_state_average_score):
                    best_action = action
                    best_state_average_score = average_action_score
            
            final_policy[state] = best_action

        # player.policy = {}
        # print('------',json.dumps(final_policy))
        data_file = open('player_policy.json', 'w+')
        json.dump(final_policy, data_file, sort_keys=True, indent=4)
        data_file.close()
        # print(player.policy)