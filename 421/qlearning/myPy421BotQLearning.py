# Local HackaGame:
import json
import sys
sys.path.insert( 1, __file__.split('421')[0] )

import matplotlib.pyplot as plt

import hackagames.hackapy as hg
import random

class AutonomousPlayer( hg.AbsPlayer ) :

    def __init__(self, exploRatio = 0.1, discountFactor = 0.99, learningRate = 0.1):
        self.alpha = learningRate
        self.q_values = {'sleep' : {'sleep' : 0}}
        self.exploRatio = exploRatio
        self.former_state = ''
        self.last_action = ''

    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        test=8
        # print( f'---\nWake-up player-{playerId} ({numberOfPlayers} players)')
        # print( gameConf )
    
    def perceive(self, gameState):
        self.horizon= gameState.child(1).flag(1)
        self.dices= gameState.child(2).flags()

        # If the state is not a key in the qvalues dict, we initialize it.
        self.state = ''.join([str(dice) for dice in self.dices])
        if self.state not in self.q_values.keys():
            self.q_values[self.state]= { "keep-keep-keep":0.0, "roll-keep-keep":0.0, "keep-roll-keep":0.0, "roll-roll-keep":0.0, "keep-keep-roll":0.0, "roll-keep-roll":0.0, "keep-roll-roll":0.0, "roll-roll-roll":0.0}

        # print( f'H: {self.horizon} DICES: {self.dices}')

    def decide(self):
        actions= ['keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]

        randomPercentage = random.uniform(0,1)
        # If random < explorationRatio, pick a random action
        if randomPercentage < self.exploRatio:
            action = random.choice(actions)
            print(f"Random action : {action}")
        # Else we choose the best action in known q_values
        else :
            actions_q_value = self.q_values[self.state]
            max_q_value = -sys.maxsize - 1
            action = random.choice(actions)

            for key in actions_q_value.keys():
                if actions_q_value[key] > max_q_value:
                    action = key
                    max_q_value = actions_q_value[key]

        # No reward since no result yet
        # If first dice roll, former state is the current state and new state is set by default
        if self.horizon == 2:
            self.former_state = self.state
            self.last_action = random.choice(actions)
        elif self.horizon == 1:
            self.updateQvalues(self.former_state, self.last_action, 0, self.state, action)
        print( f'Action: {action}' )

        self.former_state = self.state
        self.last_action = action

        return action
    
    def sleep(self, result):
        print( f'--- Results: {str(result)}' )
        self.updateQvalues(self.former_state, self.last_action, result, 'sleep', 'sleep')

    
    def updateQvalues(self, state_t1, action_t1, reward, state_t2, action_t2):
        # We take 90% of the known q_value and learning_rate% of the new_q_value
        new_q_value = self.alpha * ( reward + self.q_values[state_t2][action_t2] ) + ( 1 - self.alpha ) * self.q_values[state_t1][action_t1]
        self.q_values[state_t1][action_t1] = new_q_value

# script :
if __name__ == '__main__' :
    player= AutonomousPlayer()
    results= player.takeASeat()
    # Analysis
    average= sum(results)/len(results)
    print( f"Average score: {average}")

    for state in player.q_values.keys():
        sorted_player_q_values = sorted(player.q_values[state].items(), key=lambda x:x[1], reverse=True)
        player.q_values[state] = dict(sorted_player_q_values)

    print(json.dumps(player.q_values))

    data_file = open('QValues.json', 'w+')
    json.dump(player.q_values, data_file, sort_keys=True, indent=4)
    data_file.close()

    # Graph showing the evolution of the average score per each chunk_size games depending on the total number of games
    scores= []
    size= len(results)
    chunk_size = 1000
    for i in range(0, size, chunk_size) :
        s= min(i+chunk_size, size)
        scores.append( sum([ x for x in results[i:s] ]) / (s-i) )
    plt.plot( [ chunk_size*i for i in range(len(scores)) ], scores )
    plt.show()