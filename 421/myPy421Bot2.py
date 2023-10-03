# Local HackaGame:
import json
import sys
sys.path.insert( 1, __file__.split('tutos')[0] )

import hackagames.hackapy as hg
import random
from itertools import groupby
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
    
    def proba(self, score):
        if score == 1:
            return float(56/216)
        if score == 2:
            return float(20/216)
        if score == 3:
            return float(25/216)
        if score == 4:
            return float(21/216)
        if score == 5:
            return float(26/216)
        if score == 6:
            return float(22/216)
        if score == 7:
            return float(6/216)
        if score == 8:
            return float(60/216)
    

    def decide(self):
        actions= ['keep-keep-keep', 'keep-keep-roll', 'keep-roll-keep', 'keep-roll-roll',
            'roll-keep-keep', 'roll-keep-roll', 'roll-roll-keep', 'roll-roll-roll' ]
        # action= random.choice( actions )
        # print( f'Action: {action}' )

        # print(possible_combinations)
        # print([
        #     {"score" : self.calculate_score([int(x) for x in list(comb['comb'])]),
        #      "comb" : comb['comb'],
        #      "proba" : self.proba(self.calculate_score([int(x) for x in list(comb['comb'])])),
        #     } for comb in possible_combinations['combinations']])

        action = random.choice(actions)

        if self.dices == [4,2,1] or self.dices == [1,1,1] :
            action = 'keep-keep-keep'
        else :
            currentScore = self.calculate_score(self.dices)

            def check_score(combination):
                return combination['score'] > currentScore
        
            higher_possible_combinations = filter(check_score, possible_combinations['combinations'])

            best_action = 'roll-roll-roll'
            # best_proba = findCombinationWithDices(self.dices)[0]['proba']
            best_proba = 0

            copy_dices = self.dices

            for action in actions:

                action_dice0 = action.split('-')[0]
                action_dice1 = action.split('-')[1]
                action_dice2 = action.split('-')[2]

                def findCombinationWithDices(dices) :
                    return [combination for combination in possible_combinations['combinations'] if all(dice in dices for dice in [int(x) for x in combination['comb']]) and combination['score']> currentScore]

                three_dices_roll = True

                new_dices = []

                if action_dice0 != 'roll' :
                    new_dices.append(self.dices[0])
                else :
                    three_dices_roll = False

                if action_dice1 == 'roll' :
                    new_dices.append(self.dices[0])
                else :
                    three_dices_roll = False

                if action_dice2 == 'roll' :
                    new_dices.append(self.dices[0])
                else :
                    three_dices_roll = False

                if three_dices_roll:
                    new_dices = copy_dices

                new_higher_combinations_possible = findCombinationWithDices(sorted(new_dices, reverse=True))

                # print(currentScore, new_higher_combinations_possible)
                def key_func(comb):
                    return comb['score']
                
                score_proba = sorted(new_higher_combinations_possible, key=key_func)
                proba_better_combination = 0
                for key, value in groupby(score_proba, lambda x: x['score']):
                    for comb in value:
                        proba_better_combination += float(comb['proba'])
                        # print(action, key, comb)
                    # for 
                    # if list(value)['proba']:
                    #     proba_better_combination += float((list(value)[0])['proba'])

                # print(action, proba_better_combination)
                

                if proba_better_combination > best_proba:
                    best_action = action
                    best_proba = proba_better_combination

            action = best_action

        print( f'Action: {action}' )

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