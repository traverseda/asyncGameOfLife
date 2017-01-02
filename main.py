import ZODB, ZODB.FileStorage, BTrees.OOBTree
import collections, datetime
from utils import sphereGenerator, cubeGenerator, SpaceVector

class colorBlock():
    """
    Just a block with a color
    """
    def __init__(self, r,g,b):
        self.color = (r,g,b)
    def light(self):
        s = sum(self.color)
        if s > 385:
            return True
        else:
            return False

storage = ZODB.FileStorage.FileStorage('db/pycraftData.ZODB')
db = ZODB.DB(storage)
connection = db.open()
root = connection.root

root.world=BTrees.OOBTree.BTree()

from ptpython.repl import embed
import asyncio
loop = asyncio.get_event_loop()

#Game of life
counter={'gameOfLife':0,'frames':0}

whiteBlock=colorBlock(255,255,255)
blackBlock=colorBlock(0,0,0)


import random
def backgroundGen():
    return blackBlock
#    return random.choice([whiteBlock,blackBlock,blackBlock])

core = {}
for coord in cubeGenerator([-20,-20,0],[40,40,1]):
    core[coord] = random.choice([whiteBlock,blackBlock,blackBlock])

background = collections.defaultdict(backgroundGen)

blinker={
SpaceVector(0,1,0):whiteBlock,
SpaceVector(0,2,0):whiteBlock,
SpaceVector(0,3,0):whiteBlock,
}

world = collections.ChainMap(root.world, blinker, core, background)
#world=root.world
#world = background

def madd(a1,a2): #matrix add
    zipped = zip(a1, a2)
    return [x+y for x,y in zipped]

import transaction, copy
async def gameoflife():
    area = [i for i in cubeGenerator([-20,-20,0],[40,40,1])]
    while True:
        counter['gameOfLife'] += 1
        worldCache = { key: world[key] for key in cubeGenerator([-21,-21,0],[42,42,1]) }
        for coord in area:
            neighbors=0
            currentBlock = world[coord]
            #Calc neighbor count. The biggest argument for using numpy with its matrix math.
            if worldCache[SpaceVector(coord[0]-1, coord[1], coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0], coord[1]-1, coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0]+1, coord[1], coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0], coord[1]+1, coord[2])].light():
                neighbors=neighbors+1

            if worldCache[SpaceVector(coord[0]-1, coord[1]-1, coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0]+1, coord[1]-1, coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0]+1, coord[1]+1, coord[2])].light():
                neighbors=neighbors+1
            if worldCache[SpaceVector(coord[0]-1, coord[1]+1, coord[2])].light():
                neighbors=neighbors+1

            #Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
            if currentBlock.light() and neighbors < 2:
                world[coord]=blackBlock 
            
            #Any live cell with two or three live neighbours lives on to the next generation.

            #Any live cell with more than three live neighbours dies, as if by overpopulation.
            if currentBlock.light() and neighbors > 3:
                world[coord]=blackBlock 

            #Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
            if not currentBlock.light() and neighbors==3:
                 world[coord]=whiteBlock

        del worldCache
        transaction.commit()
        await asyncio.sleep(1) 

##The interactive shell
@asyncio.coroutine
def interactive_shell():
    """
    Coroutine that starts a Python REPL from which we can access the global
    counter variable.
    """
    yield from embed(globals=globals(), return_asyncio_coroutine=True, patch_stdout=True)
    # Stop the loop when quitting the repl. (Ctrl-D press.)
    loop.stop()

windowarea=sorted(cubeGenerator([-21,-21,0],[42,42,1]))

from colorama import init, Fore, Back, Style
init()


import time
start_time = time.time()

async def asciiWindow():
    while True:
        counter['frames'] += 1
        print(Style.RESET_ALL+str(counter))
        print("clocktime: "+ str((time.time() - start_time)))
        for coord in windowarea:
            if world[SpaceVector(coord[0], coord[1], coord[2])].light():
                print(Back.WHITE+" ", end="")
            else:
                print(Back.BLACK+" ", end="")
            if coord[1]==20:
                print(Style.RESET_ALL+str(coord))
        await asyncio.sleep(0.5)

def main():
#    asyncio.async(interactive_shell())
    asyncio.async(asciiWindow())
    asyncio.async(gameoflife())
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()

