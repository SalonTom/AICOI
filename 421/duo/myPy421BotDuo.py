# Local HackaGame:
import json
import sys

from matplotlib import pyplot as plt
sys.path.insert( 1, __file__.split('421')[0] )

import hackagames.hackapy as hg
import random

class AutonomousPlayer( hg.AbsPlayer ) :

    def __init__(self, exploRatio = 0, discountFactor = 0.99, learningRate = 0.1):

        self.use_q_values = True

        if self.use_q_values:
            data = open('q_values_duo.json', 'r')
            self.q_values = json.load(data)
            data.close()
        else :
            self.q_values = {
                '1' : {
                    'sleep' : { 'sleep' : 0 }
                },
                '2' : {
                    'sleep' : { 'sleep' : 0 }
                } 
            }
        
        self.alpha = learningRate
        self.exploRatio = exploRatio
        self.former_state = ''
        self.last_action = ''

        self.round_counter = 0
        self.game_counter = 0

    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        self.player_id = playerId
        # print( f'---\nWake-up player-{playerId} ({numberOfPlayers} players)')
        # print( gameConf )
    
    def perceive(self, gameState):
        self.horizon= gameState.child(1).flag(1)
        self.dices= gameState.child(2).flags()
        self.op_dices= gameState.child(3).flags()

        self.state = ''.join([str(dice) for dice in self.dices])
        # print( f'H: {self.horizon} DICES: {self.dices} OPPONENTS {self.op_dices}' )

    def decide(self):
        self.player_id = str(self.player_id)
        actions= [ 'keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]

        if self.state not in self.q_values[self.player_id].keys():
            self.q_values[self.player_id][self.state] = { "keep-keep-keep":0.0, "roll-keep-keep":0.0, "keep-roll-keep":0.0, "roll-roll-keep":0.0, "keep-keep-roll":0.0, "roll-keep-roll":0.0, "keep-roll-roll":0.0, "roll-roll-roll":0.0}
        
        randomPercentage = random.uniform(0,1)

        if randomPercentage < self.exploRatio:
            action = random.choice( actions )
        else :
            actions_q_value = self.q_values[self.player_id][self.state]
            max_q_value = -sys.maxsize - 1
            action = random.choice(actions)

            for key in actions_q_value.keys():
                if actions_q_value[key] > max_q_value:
                    action = key
                    max_q_value = actions_q_value[key]

        if self.player_id == '1' and self.horizon == 1:

            middleReward = self.middleReward(self.former_state, self.state)
            self.updateQvalues(self.former_state, self.last_action, middleReward, self.state, action)

        elif self.player_id == '2':

            if self.score(self.dices) > self.score(self.op_dices):

                action = 'keep-keep-keep'

            elif self.round_counter > 0 :

                middleReward = self.middleReward(''.join([str(dice) for dice in self.op_dices]), self.state)
                self.updateQvalues(self.former_state, self.last_action, middleReward, self.state, action)

        self.former_state = self.state
        self.last_action = action

        # print( f'Action: {action}' )

        self.round_counter += 1
        return action
    
    def sleep(self, result):
        self.updateQvalues(self.former_state, self.last_action, result, 'sleep', 'sleep')
        # print( f'--- Results: {str(result)}' )

        self.round_counter = 0
        self.game_counter += 1

        if self.game_counter % 1000 == 0 and self.exploRatio >= 0.02:
            self.exploRatio = self.exploRatio - 0.02
            print(self.exploRatio)
        

    def updateQvalues(self, state_t1, action_t1, reward, state_t2, action_t2):
        # We take 90% of the known q_value and learning_rate% of the new_q_value
        new_q_value = self.alpha * ( reward + self.q_values[self.player_id][state_t2][action_t2] ) + ( 1 - self.alpha ) * self.q_values[self.player_id][state_t1][action_t1]
        self.q_values[self.player_id][state_t1][action_t1] = new_q_value

    # Return the given_reward if score state_1 < score state_2
    def middleReward(self, state_1, state_2, given_reward = 0.1):
        return -given_reward if self.score([int(dice) for dice in state_1]) > self.score([int(dice) for dice in state_2]) else given_reward 

    def score(self, state):
        if state[0] == 4 and state[1] == 2 and state[2] == 1 : 
            return 800

        if state[0] == 1 and state[1] == 1 and state[2] == 1 : 
            return 600

        if state[1] == 1 and state[2] == 1 : 
            return 400 +state[0]

        if state[1] == state[0] and state[2] == state[0] : 
            return 300 + state[0]

        if state[1] == state[0]-1 and state[2] == state[0]-2 : 
            return 200 + state[0]

        if state[0] == 2 and state[1] == 2 and state[2] == 1 : 
            return 0

        return 100 + state[0]

# script :
if __name__ == '__main__' :
    player= AutonomousPlayer()
    results= player.takeASeat()
    print( f"Average Results: {sum(results)/len(results)}" )

    data_file = open('q_values_duo.json', 'w+')
    json.dump(player.q_values, data_file, sort_keys=True, indent=4)
    data_file.close()

    # Graph showing the evolution of the average score per each chunk_size games depending on the total number of games
    scores= []
    size = len(results)
    chunk_size = 1000
    for i in range(0, size, chunk_size) :
        s= min(i+chunk_size, size)
        scores.append( sum([ x for x in results[i:s] ]) / (s-i) )
    plt.plot( [ chunk_size*i for i in range(len(scores)) ], scores )
    plt.show()