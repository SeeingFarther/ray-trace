import numpy as np
from utilities import normalize


class InfinitePlane:
    def __init__(self, normal, offset, material_index):
        self.normal = normalize(normal)
        self.offset = -offset
        self.material_index = material_index

    # Get and set functions
    def getNormal(self):
        return self.normal

    def getOffset(self):
        return self.offset

    def getMaterial(self):
        return self.material_index

    def setNormal(self, normal):
        self.normal = normal

    def setOffset(self, offset):
        self.offset = -offset

    def setMaterial(self, material_index):
        self.material_index = material_index

    # Calculate intersection between the ray and the plane using algebraic method
    def findIntersection(self, P_0, vector):
        div = vector.dot(self.normal)
        prod = P_0.dot(self.normal) + self.offset
        with np.errstate(divide='ignore'):
            t = -(prod / div)
        return t

    # Get and set functions
    def getNormal(self, ray=None):
        return self.normal
