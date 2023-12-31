#!env python3
"""
HackaGame player interface 
"""
import json
import math
import sys, os

from matplotlib import pyplot as plt
sys.path.insert( 1, __file__.split('moveIt')[0] )

import hackagames.hackapy.command as cmd
import hackagames.hackapy.player as pl
import hackagames.gameMoveIt.gameEngine as ge

import random

def log( aStr ):
    # print( aStr )
    pass

def main():
    player= AutonomousPlayer()
    results= player.takeASeat()
    print( f"Average: {sum(results)/len(results)}" )

    if player.use_q_values is False:
        data_file = open('q_values_moveIt.json', 'w+')
        json.dump(player.q_values, data_file, sort_keys=True, indent=4)
        data_file.close()

    # Graph showing the evolution of the average score per each chunk_size games depending on the total number of games
    scores= []
    size = len(results)
    chunk_size = 100
    for i in range(0, size, chunk_size) :
        s= min(i+chunk_size, size)
        scores.append( sum([ x for x in results[i:s] ]) / (s-i) )
    plt.plot( [ chunk_size*i for i in range(len(scores)) ], scores )
    plt.show()

class AutonomousPlayer( pl.AbsPlayer ):

    def __init__(self):
        super().__init__()
        self._board= ge.Hexaboard()
        self._mobiles= []
        self._id = 0

        self.alpha = 0.1
        self.exploRatio = 0.1

        self.former_state = ''
        self.last_dir = ''

        self.first_play = True

        self.previous_score = 0
    
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gamePod):
        # Initialize from gamePod:
        self._id= playerId
        assert( gamePod.family() == 'MoveIt')
        self._board.fromPod( gamePod )
        nbRobots, nbMobiles= gamePod.flag(3), gamePod.flag(4)
        self._mobiles= ge.defineMobiles( nbRobots, nbMobiles )
        self._board.setupMobiles( self._mobiles )

        # Initialize state variable:
        self._countTic= 0
        self._countCycle= 0
        self._score= 0

        self.use_q_values = False

        if self.use_q_values:
            data = open('q_values_moveIt.json', 'r')
            self.q_values = json.load(data)
            data.close()
        else :
            self.q_values = { "sleep" : { "sleep" : 0.0 } }

        # Reports:
        log( f'---\nwake-up player-{playerId} ({numberOfPlayers} players)')
        
    def perceive(self, statePod):

        # update the game state:
        self._countTic= statePod.flag(1)
        self._countCycle= statePod.flag(2)
        self._score= statePod.value(1)
        self._board.mobilesFromPod( statePod )

        # Definition nouvelles variables d'états
        
        self.objectif = {
            "dist": 0,
            "dir": 0
        }

        self.humains = [
            {
                "id": 2,
                "dist": 0,
                "dir_robot": 0,
                "dir_move": 0
            }, 
            {
                "id": 3,
                "dist": 0,
                "dir_robot": 0,
                "dir_move": 0
            }   
        ]

        self.obstacles = [True]*6

        # json de avec key : "distO dirO obs1 .... obs6 dirH1 distH1 moveH1 dirH2 distH2 moveH2"

    
    def decide(self):
        # print(self._board.shell())

        action= "move"
        dirs = ['0', '1', '2', '3', '4', '5', '6']

        robotx = 0
        roboty = 0

        path = []

        humain_index = 0

        for r in self._mobiles :
            if r.isRobot() :

                robotx = r.x()
                roboty = r.y()

                path= self._board.path( r.x(), r.y(), r.goalx(), r.goaly() )
                dir= path[0]
                
                self.objectif["dist"], self.objectif["dir"] = self.dist_and_dir(robotx, roboty, r.goalx(), r.goaly()) if len(path) < 3 else (0 , 0)

            if r.isHuman():
                human_dist, human_dir = self.dist_and_dir(robotx, roboty, r.x(), r.y())
                
                if human_dist > 2 :
                    human_dist = 0
                    human_dir = 0

                self.humains[humain_index]["dist"], self.humains[humain_index]["dir_robot"] = human_dist, human_dir
                self.humains[humain_index]["dir_move"] = r.direction()

                humain_index += 1

        self.state = '-'.join(str(i) for i in [self.objectif["dir"], self.objectif["dist"], self.get_obstacles_string(robotx, roboty), self.humains[0]["dist"], self.humains[0]["dir_robot"], self.humains[0]["dir_move"], self.humains[1]["dist"], self.humains[1]["dir_robot"], self.humains[1]["dir_move"]])

        if self.state not in self.q_values.keys():
            self.q_values[self.state] = {"0": 0.0, "1":0.0, "2":0.0, "3":0.0, "4":0.0, "5":0.0, "6":0.0}

        if random.uniform(0,1) < self.exploRatio:
            dir = random.choice(self.free_moves(robotx, roboty)) if len(self.free_moves(robotx, roboty)) > 0 else random.choice(dirs)
        else:
            dir = random.choice(self.free_moves(robotx, roboty)) if len(self.free_moves(robotx, roboty)) > 0 else random.choice(dirs)
            dir_q_value = self.q_values[self.state]
            max_q_value = -sys.maxsize - 1

            for key in dir_q_value.keys():
                if dir_q_value[key] > max_q_value:
                    dir = key
                    max_q_value = dir_q_value[key]

            reward = 0

            if self.first_play is False:
                reward = 1 if self._score >= self.previous_score else -10
                # print("q_values updated!")
                self.update_q_values(self.former_state, str(self.last_dir), reward, self.state, str(dir))

        action = ("move " + str(dir)) if dir != 'pass' else dir

        self.former_state = self.state
        self.last_dir = dir
        self.first_play = False
        self.previous_score = self._score

        return action
    
    def sleep(self, result):
        try:
            self.update_q_values(self.former_state, str(self.last_dir), result, 'sleep', 'sleep')
        except:
            print(f'ERROR UPDATING Q VALUES FOR FORMER STATE : {self.former_state}')
        self.first_play = True

        # log( f'---\ngame end on result: {result}' )

    def update_q_values(self, state_t1, action_t1, reward, state_t2, action_t2):
        # We take 90% of the known q_value and learning_rate% of the new_q_value
        new_q_value = self.alpha * ( reward + self.q_values[state_t2][action_t2] ) + ( 1 - self.alpha ) * self.q_values[state_t1][action_t1]
        self.q_values[state_t1][action_t1] = new_q_value
    
        
    def dist_and_dir(self, x1, y1, x2, y2):
        path = self._board.path(x1, y1, x2, y2)
        return len(path), path[0]
    

    def get_obstacles_string(self, x, y):
        dirs_available = self._board.movesFrom(x, y)
        obstacles = [1]*6

        for dir in dirs_available:
            if dir > 0:
                obstacles[dir - 1] = 0
                self.obstacles[dir - 1] = False

        return ''.join([str(i) for i in obstacles])

    def free_moves(self, x, y):
        possible_moves = self._board.movesFrom(x,y)
        # print(possible_moves)
        free_moves = []
        for move in possible_moves:
            new_x, new_y = self._board.at_dir(x, y, move)
            cell_at_dir = self._board.at(new_x, new_y)
            if bool(cell_at_dir._mobile) is False and self._board.isCoordinate(new_x, new_y):
                free_moves.append(move)
        
        # print(free_moves)
        
        return free_moves


# script
if __name__ == '__main__' :
    main()
