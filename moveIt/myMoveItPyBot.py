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

        self.obstacles = [False]*6

        # json de avec key : "distO dirO obs1 .... obs6 dirH1 distH1 moveH1 dirH2 distH2 moveH2"

    
    def decide(self):
        # print(self._board.shell())
        action= "move"
        for r in self._mobiles :
            if r.isRobot() :
                path= self._board.path( r.x(), r.y(), r.goalx(), r.goaly() )
                dir= path[0]

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
        print(action)
        return action
    
    def sleep(self, result):
        
        log( f'---\ngame end on result: {result}' )

# script
if __name__ == '__main__' :
    main()