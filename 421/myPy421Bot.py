# Local HackaGame:
import json
import sys
sys.path.insert( 1, __file__.split('tutos')[0] )

import hackagames.hackapy as hg
import random
import itertools

f = open('data.json')
possible_combinations = json.load(f)

class AutonomousPlayer( hg.AbsPlayer ) :

    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        test = 8
        # print( f'---\nWake-up player-{playerId} ({numberOfPlayers} players)')
        # print( gameConf )
    
    def perceive(self, gameState):
        self.horizon= gameState.child(1).flag(1)
        self.dices= gameState.child(2).flags()
        print( f'H: {self.horizon} DICES: {self.dices}')

    def calculate_score(self, dice):
        # Define the scoring rules
        score = 0

        # Check for the highest possible combination (4, 2, 1)
        if dice == [4, 2, 1]:
            return 8
        
        if dice == [1, 1, 1]:
            return 7

        # Check for three of a kind
        for value in set(dice):
            if dice.count(value) >= 3:
                return value

        # Check for straights
        if sorted(dice) in [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6]]:
            return 2

        # Check for two aces (X, 1, 1) where X is 2 to 6
        if dice[1:] == [1, 1]:
            return dice[0]

        # All other rolls score 1 point
        return 1

    def best_action(self, dice):
        best_score = 0
        best_action = None

        # Generate all possible actions
        actions = list(itertools.product(['keep', 'roll'], repeat=3))

        for action in actions:
            current_dice = dice.copy()
            for i in range(3):
                if action[i] == 'roll':
                    current_dice[i] = random.randint(1, 6)
            current_score = self.calculate_score(current_dice)

            if current_score > best_score:
                best_score = current_score
                best_action = action

        return best_action, best_score

    def decide(self):
        actions= ['keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]
        # action= random.choice( actions )
        # print( f'Action: {action}' )

        # print(possible_combinations)
        # print([{"score" : self.calculate_score([int(x) for x in list(comb)]), "comb" : comb} for comb in possible_combinations['combinations']])

        action = random.choice(actions)

        if self.dices == [4,2,1] or self.dices == [1,1,1] :
            action = 'keep-keep-keep'
        else :
            if self.dices[2] != 1 :
                action = 'roll-roll-roll'
            elif self.dices[1] != 2:
                if self.dices[1] != 1:
                    action = 'roll-keep-keep'
                else :
                    action = 'keep-keep-keep'
            elif self.dices[1] != 4:
                action = 'roll-keep-keep'
            else :
                action = 'roll-keep-keep'

        print( f'Action: {action}' )
        # best_turn_action, turn_score = self.best_action(self.dices)


        return action  
    
    def sleep(self, result):
        test=8
        # print( f'--- Results: {str(result)}' )

# script :
if __name__ == '__main__' :
    player= AutonomousPlayer()
    results= player.takeASeat()
    # Analysis
    average= sum(results)/len(results)
    print( f"Average score: {average}")