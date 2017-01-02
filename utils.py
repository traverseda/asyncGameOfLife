import math, collections

SpaceVectorBase = collections.namedtuple('SpaceVector', 'x y z')
#SpaceTimeVectorBase = collections.namedtuple('SpaceTimeVector', 'x y z t')#Time is relative, so use a SpaceTimeVector to do an operation as if it was a particular, known, point in time.

class VectorMethods():
    def __int__(self):
        combined = "".join([str(i) for i in self])
        return int(combined)

class SpaceVector(SpaceVectorBase,VectorMethods):
    pass


def distance(point1, point2):
    diff1 = point1[0]-point2[0]
    diff1 = diff1**2
    diff2 = point1[1]-point2[1]
    diff2 = diff2**2
    return math.sqrt(diff1+diff2)

#Probably more clever then it's worth.
def cubeGenerator(center, size, partial=list()):
    depth = len(partial)
    if depth < 3:
        for i in range(center[depth],center[depth]+size[depth]):
            newPartial = partial+[i,]
            yield from cubeGenerator(center,size,newPartial)
    else:
        partial = SpaceVector(*partial)
        yield partial

def cylinderGenerator(center, rad, height, partial=list()):
    pass

def sphereGenerator(center, diam):
    rad=diam/2
    boundingCube = cubeGenerator([int(i-rad) for i in center], (diam,diam,diam))
    return set((i for i in boundingCube if distance(center, i) < rad ))
