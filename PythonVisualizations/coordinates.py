# Utilities for working with coordinates
# The vector class is used to hold a tuple of coordinates and define many
# operations on them.  The operations return tuples not vectors, but can
# easily be converted by wrapping the result in vector() constructor, e.g.
# vector(*result)

from itertools import *
from operator import *
import math

class vector(object):
    # Constructor accepts multiple coordinate parameters: vector(3, 4, 5) or
    # a sequence containing coordinates: vector([3, 4, 5])
    def __init__(self, *coords):
        self.coords = tuple(coords[0]) if (
            len(coords) == 1 and isinstance(coords[0], (list, tuple, set))
        ) else coords

    def __len__(self):
        return len(self.coords)

    def __str__(self):
        return 'V({})'.format(', '.join(map(str, self.coords)))

    def __eq__(self, other):
        if isinstance(other, vector):
            return self.coords == other.coords
        elif isinstance(other, (list, tuple)):
            return self == vector(other)

    def __lt__(self, other):
        if isinstance(other, vector):
            return self.coords < other.coords
        elif isinstance(other, (list, tuple)):
            return self < vector(other)

    def __gt__(self, other):
        if isinstance(other, vector):
            return self.coords > other.coords
        elif isinstance(other, (list, tuple)):
            return self > vector(other)
         
    def __le__(self, other): return self < other or self == other
    def __ge__(self, other): return self > other or self == other

    def __getitem__(self, key): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.coords):
                return self.coords[key]
            raise IndexError
        elif isinstance(key, slice):
            return self.coords[key.start:key.stop:key.step]
        elif isinstance(key, str) and len(key) == 1 and key.lower() in 'xyz':
            return self.coords['xyz'.index(key.lower())]
        raise ValueError('Invalid vector type')

    def __add__(self, other):
        if isinstance(other, vector):
            return tuple(map(add, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self + vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c + other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __sub__(self, other):
        if isinstance(other, vector):
            return tuple(map(sub, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self - vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c - other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __mul__(self, other):
        if isinstance(other, vector):
            return tuple(map(mul, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self * vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c * other for c in self.coords)
        raise ValueError('Invalid vector type')

    def __truediv__(self, other):
        if isinstance(other, vector):
            return tuple(map(truediv, self.coords, other.coords))
        elif isinstance(other, (list, tuple)):
            return self / vector(other)
        elif isinstance(other, (int, float)):
            return tuple(c / other for c in self.coords)
        raise ValueError('Invalid vector type')

    def dot(self, other):
        return sum(self * other)
     
    def len2(self):
        return self.dot(self)

    def vlen(self):
        return math.sqrt(self.len2())

    def unit(self):
        return self / self.vlen()

    def rotate(self, angle, radians=False):
        a = angle if radians else math.radians(angle)
        s, c = math.sin(a), math.cos(a)
        return (self.dot(vector(c, -s)), self.dot(vector(s, c)))

def flat(*vectors): # Flatten a sequence of vectors into a tuple of coordinates
    return tuple(v[i] for v in vectors for i in range(len(v)))

def points(*coords, dimension=2): # Unflatten a list of coords into points of
    return [                      # a given dimension
        coords[j:j + dimension]
        for j in range(0, (len(coords) // dimension) * dimension, dimension)]

def vectors(*coords, dimension=2): # Unflatten a list of coords into vectors of
    return [                       # a given dimension
        vector(*coords[j:j + dimension])
        for j in range(0, (len(coords) // dimension) * dimension, dimension)]

def bbox(*points): # Return the bounding box of a sequence of points/vectors
    mindim = min(len(p) for p in points)
    return (
        tuple(min(*(p[i] for p in points)) for i in range(mindim)),
        tuple(max(*(p[i] for p in points)) for i in range(mindim)))

# Return the n vertices of regular polygon of nGon sides starting from
# a particular angle and going clockwise
def convexPolygon(center, radius, nGon, startAngle=90):
    V = vector
    return tuple(V(center) + V(radius, 0).rotate(startAngle + j * 360 / nGon)
                 for j in range(nGon))

# Return a n-pointed star's vertices with a given outer and inner radii
# starting at a particular angle and going clockwise.  (The result has
# 2 * nPoints vertices).
def regularStar(center, outerRadius, innerRadius, nPoints, startAngle=90):
    V = vector
    return tuple(
        V(center) + V(outerRadius if j % 2 == 0 else innerRadius, 0).rotate(
            startAngle + j * 180 / nPoints)
        for j in range(nPoints * 2))
     
if __name__ == '__main__':
    V = vector
    print('V is short for vector')
    A = V(3, 4, 5)
    print('A = V(3, 4, 5)')
    B = V(4, 3, 2)
    print('B = V(4, 3, 2)')

    expressions = [
        'A', 'B', 'str(A)', 'str(B)', 
        'A + B', 'A - B', 'A * B', 'B * A', 'A / B',
        'A * 2', 'A + 2', 'A - 2', 'A / 2',
        'A < B', 'A == B', 'A > B', 'A == A', 'A <= B', 'A <= A',
        'A[0]', 'A[:2]', 'A[::2]', 'str(V(*A[::2]))', 'str(V(A[::2]))',
        'V(A[::2]).rotate(90)', 'A.rotate(37)',
        'A.dot(B)', 'A.len2()', 'A.vlen()', 'A.unit()',
        'bbox(A, B)', 'bbox(B[1:], A)',
        'flat(*bbox(A, B))',
        'bbox(A[1:], B[1:])', 'flat(*bbox(A[1:], B[1:]))',
        '(A.coords, B.coords)', 'flat(A.coords, B.coords)',
        'points(*flat(A.coords, B.coords))',
        'points(*flat(A.coords, B.coords), dimension=3)', 
        'convexPolygon((0, 0), 10, 5)',
        'regularStar((10, 0), 10, 5, 6)'
    ]
    for exp in expressions:
        print('{} evaluates to '.format(exp), end='')
        print(repr(eval(exp, globals())))
