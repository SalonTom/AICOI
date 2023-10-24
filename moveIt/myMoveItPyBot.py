#!env python3
"""
HackaGame player interface 
"""
import sys, os
sys.path.insert( 1, __file__.split('moveIt')[0] )

import hackagames.hackapy.command as cmd
import hackagames.hackapy.player as pl
import hackagames.gameMoveIt.gameEngine as ge

import random

def log( aStr ):
    print( aStr )
    pass

def main():
    player= AutonomousPlayer()
    result= player.takeASeat()
    print( f"Average: {sum(result)/len(result)}" )

class AutonomousPlayer( pl.AbsPlayer ):

    def __init__(self):
        super().__init__()
        self._board= ge.Hexaboard()
        self._mobiles= []
        self._id= 0
    
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


        self.q_values = {
            "sleep" : 0
        }

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

        robotx = 0
        roboty = 0

        humain_index = 0

        for r in self._mobiles :
            if r.isRobot() :

                robotx = r.x()
                roboty = r.y()

                path= self._board.path( r.x(), r.y(), r.goalx(), r.goaly() )
                dir= path[0]
                
                self.objectif["dist"], self.objectif["dir"] = self.dist_and_dir(robotx, roboty, r.goalx(), r.goaly())

                print(self.get_obstacles_string(r.x(), r.y()))

                print('Initial move : ' + str(dir))

                new_x, new_y = self._board.at_dir(r.x(), r.y(), dir)

                if self._board.at(new_x, new_y).mobile():
                    print("Humain sur la next case, redirect ...")
                    possible_dirs = self._board.movesFrom(r.x(), r.y())

                    for pdir in possible_dirs:
                        new_x, new_y = self._board.at_dir(r.x(), r.y(), pdir)
                        if self._board.at(new_x, new_y).isAvailable() is True:
                            dir = pdir
                            break
        
                action+= " " + str(dir)

            if r.isHuman():
                self.humains[humain_index]["dist"], self.humains[humain_index]["dir_robot"]  = self.dist_and_dir(robotx, roboty, r.x(), r.y())
                self.humains[humain_index]["dir_move"] = r.direction()

                humain_index += 1

        self.state = ''.join(str(i) for i in [self.objectif["dir"], self.objectif["dist"], self.get_obstacles_string(robotx, roboty), self.humains[0]["dist"], self.humains[0]["dir_robot"], self.humains[0]["dir_move"], self.humains[1]["dist"], self.humains[1]["dir_robot"], self.humains[1]["dir_move"]])
        print(self.state)

        if self.state not in self.q_values.keys():
            self.q_values[self.state] = { "1":0.0, "2":0.0, "3":0.0, "4":0.0, "5":0.0, "6":0.0}

        return action
    
    def sleep(self, result):
        
        log( f'---\ngame end on result: {result}' )

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

# script
if __name__ == '__main__' :
    main()