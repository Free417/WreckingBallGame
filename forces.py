import pygame
from pygame.math import Vector2
import itertools
import math

class SingleForce:
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):
        for obj in self.objects_list:
            force = self.force(obj)
            obj.add_force(force)

    def force(self, obj): # virtual function
        return Vector2(0, 0)


class PairForce:
    def __init__(self, pairs_list=[]):
        self.pairs_list = pairs_list

    def apply(self):
        # Loop over all pairs of objects and apply the calculated force
        # to each object, respecting Newton's 3rd Law.  
        # Use either two nested for loops (taking care to do each pair once)
        # or use the itertools library (specifically, the function combinations).
        for a, b in self.pairs_list:
            force = self.force(a,b)
            # Apply the force to each member of the pair respecting Newton's 3rd Law.
            a.add_force(force)
            b.add_force(-force)

    def force(self, a, b): # virtual function
        return Vector2(0,0)


class BondForce:
    def __init__(self, pairs_list=[]):
        # pairs_list has the format [[obj1, obj2], [obj3, obj4], ... ]
        self.pairs_list = pairs_list

    def apply(self):
        # Loop over all pairs from the pairs list.
        for a, b in self.pairs_list:
            force = self.force(a,b)
            # Apply the force to each member of the pair respecting Newton's 3rd Law.
            a.add_force(force)
            b.add_force(-force)

    def force(self, a, b): # virtual function
        return Vector2(0, 0)

# Add Gravity, SpringForce, SpringRepulsion, AirDrag
class Gravity(SingleForce):
    def __init__(self, acc=(0,0), **kwargs):
        self.acc = Vector2(acc)
        super().__init__(**kwargs)

    def force(self, obj):
        G = 6.67 * 10**-11
        self.acc = Vector2(self.acc.x, self.acc.y - G)

        if obj.mass != math.inf:
            return obj.mass*self.acc
        else:
            return Vector2(0,0)

class SpringForce(PairForce):
    def force(self, a, b): # virtual function
        k = 80
        len = 50
        f_spring = Vector2(0,0)
        r = a.pos - b.pos
        v = a.vel - b.vel
        damp_const = 30
        if r != Vector2(0,0):
            f_damping = damp_const * v * r.normalize()
            f_spring = ((-k * r.magnitude() - len) - f_damping) * r.normalize()
        return f_spring


class AirDrag(SingleForce):
    def __init__(self, wind=(0,0), **kwargs):
        self.wind = Vector2(0,0)
        super().__init__(**kwargs)

    def force(self, obj):
        cd = 0.44
        A = math.pi * obj.radius**2
        p = 0.00129
        if obj.mass != math.inf:
            obj.vel = obj.vel - self.wind
        if obj.vel != Vector2(0,0): 
            drag = -(1/2) * cd * p * A * obj.vel.magnitude() * obj.vel
        else:
            drag = (0,0)

        if obj.mass != math.inf:
            return drag
        else:
            return Vector2(0,0)

class FrictionForce(SingleForce):
    def __init__(self, u=0, g=0, **kwargs):
        self.u = 0.3
        self.g = 6.67 * 30
        super().__init__(**kwargs)

    def force(self, obj):
        if obj.vel == 0:
            self.u = 0

        if obj.vel != Vector2(0,0):
            friction=-self.u*obj.mass*self.g*obj.vel.normalize()
        else:
            friction = Vector2(0,0)

        if obj.mass != math.inf:
            return friction
        else:
            return Vector2(0,0)

class SpringRepulsion(BondForce):
    def force(self, a, b): # virtual function
        r = a.pos - b.pos
        k = 80
        if (a.radius + b.radius - r.magnitude()) > 0 and a.mass != math.inf and r != Vector2(0,0):
            return k * (a.radius + b.radius - r.magnitude())*r.normalize()
        else:
            return Vector2(0, 0)