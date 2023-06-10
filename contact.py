import enum
from sys import displayhook
from pygame.math import Vector2
import math

# Returns a new contact object of the correct subtype
# This function has been done for you.
def generate(a, b, **kwargs):
    # Check if a's type comes later than b's alphabetically.
    # We will label our collision types in alphabetical order, 
    # so the lower one needs to go first.
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"{a.contact_type}_{b.contact_type}"](a, b, **kwargs)
    
# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a, b, resolve=False, flipNormals = False, **kwargs):
        self.a = a
        self.b = b
        self.flipNormals = flipNormals
        self.kwargs = kwargs
        self.update()
        if resolve:
            self.resolve(update=False)
 
    def update(self):  # virtual function
        self.overlap = 0
        self.normal = Vector2(0, 0)

    def point(self):
        return Vector2(0,0)

    def resolve(self, restitution=None, friction=None, jump_vel = None, update=True):
        a = self.a
        b = self.b
        if update:
            self.update()

        if restitution is None:
            if "restitution" in self.kwargs.keys():
                restitution = self.kwargs["restitution"]
            else:
                restitution = 0

        if friction is None:
            if "friction" in self.kwargs.keys():
                friction = self.kwargs["friction"]
            else:
                friction = 0

        if jump_vel is None:
            if "jump_vel" in self.kwargs.keys():
                jump_vel = self.kwargs["jump_vel"]
            else:
                jump_vel = 0

        # if(self.flipNormals):
        #     print("A.avel is " + str(a.avel))
        #     print("B.avel is " + str(b.avel))
            
        #     #b.avel = 0.0
        #     print("A.mass is " + str(a.mass))
        #     print("B.mass is " + str(b.mass))
        #     print("B.vel is " + str(b.vel))
        #     if(a.mass * b.mass < 0):
        #         a.mass *= -1
        
            #b.vel *= -1
        # resolve overlap
        if self.overlap > 0:
            a = self.a
            b = self.b
            if(a.mass == -b.mass):
                print("Same mass collision")
                print("A.mass is " + str(a.mass))
                print("B.mass is " + str(b.mass))
                if(a.mass < 0):
                    a.mass *= -1
                else:
                    b.mass *= -1
            m = 1/(1/a.mass+1/b.mass)
            a.delta_pos(m/a.mass*self.overlap*self.normal)
            b.delta_pos(-m/b.mass*self.overlap*self.normal)
            point = self.point()
            sap = (point - a.pos).rotate(90)
            va = a.vel + a.avel*sap
            sbp = (point - b.pos).rotate(90)
            vb = b.vel + b.avel*sbp
            v = va - vb
            if v.dot(self.normal) < 0:
                m = 1 / (1/a.mass + 1/b.mass + sap.dot(self.normal)**2/a.momi + sbp.dot(self.normal)**2/b.momi)
                J = -(1 + restitution) * m * v.dot(self.normal)
                impulse = J * self.normal

                #if(self.flipNormals):
                   # a.impulse(impulse, point)
                 #   b.impulse(impulse, point)
                #else:
                a.impulse(impulse, point)
                b.impulse(-impulse, point)
                if(a.mass < 0 and self.flipNormals):
                    a.mass *= -1
# Contact class for two circles
class Circle_Circle(Contact):
    def __init__(self, a, b, **kwargs):
        super().__init__(a, b, **kwargs)

    def update(self):  # compute the appropriate values
        r = Vector2(self.a.pos - self.b.pos)
        self.overlap = self.a.radius + self.b.radius - r.magnitude()
        if r != Vector2(0,0):
            self.normal = r.normalize()

    def point(self):
        return self.a.pos - self.a.radius*self.normal

class Circle_Circle(Contact):
    def __init__(self, a, b, **kwargs):
        super().__init__(a, b, **kwargs)

    def update(self):  # compute the appropriate values
        r = Vector2(self.a.pos - self.b.pos)
        self.overlap = self.a.radius + self.b.radius - r.magnitude()
        if r != Vector2(0,0):
            self.normal = r.normalize()

    def point(self):
        return self.a.pos - self.a.radius*self.normal

class Cable_Circle(Contact):
    def __init__(self, a, b, len = 0, modifiedCircle = False, **kwargs):
        self.a = a
        self.b = b
        self.len = len
        self.modifiedCircle = modifiedCircle
        self.update()
        super().__init__(a, b, **kwargs)

    def update(self):  # compute the appropriate values
        r = Vector2(self.a.pos - self.b.pos)
        if(self.len != 0):
            if r != Vector2(0,0) and r.magnitude() > self.len:
                self.overlap = r.magnitude() - self.len
            else:
                self.overlap = 0
            self.normal = -r.normalize()
        else:
            self.overlap = 0
            if r != Vector2(0,0):
                self.normal = r.normalize()
        
           

    def point(self):
        return self.a.pos - self.a.radius*self.normal

class Cable_Polygon(Contact):
    def __init__(self, a, b, **kwargs):
        self.circle = a
        self.polygon = b
        super().__init__(a, b, **kwargs)

    def point(self):
        return self.circle.pos - self.circle.radius*self.normal

    def update(self):  # compute the appropriate values
        min_overlap = math.inf # Current min overlap
        # Loop over all sides, find index of minimum overlap
        for i, (wall_point, wall_normal) in enumerate(zip(self.polygon.points, self.polygon.normals)):
            overlap = self.circle.radius + (wall_point - self.circle.pos).dot(wall_normal)
            #if overlap is less than min_overlap
            if overlap < min_overlap:
            ## update min_overlap
                min_overlap = overlap
            ## save index
                index = i

        self.overlap = min_overlap
        # self.normal = the normal of the wall of the least overlap
        self.normal = self.polygon.normals[index]

        if 0 < self.overlap < self.circle.radius:
            # Check if the point is beyond one of the endpoints
            endpoint1 = self.polygon.points[index]
            endpoint2 = self.polygon.points[index - 1]
            # if beyond index
            if (self.circle.pos - endpoint1).dot(endpoint1 - endpoint2) > 0:
                ## set new overlap and normal
                r = self.circle.pos - endpoint1
                self.overlap = self.circle.radius - r.magnitude()
                self.normal = r.normalize()
            # elif beyond index - 1
            elif (self.circle.pos - endpoint2).dot(endpoint2 - endpoint1) > 0:
                ## set new overlap and normal
                r = self.circle.pos - endpoint2
                self.overlap = self.circle.radius - r.magnitude()
                self.normal = r.normalize()

class Cable_Wall(Contact):
    def __init__(self, a, b, **kwargs):
        self.circle = a
        self.wall = b
        super().__init__(a, b, **kwargs)

    def update(self):  # compute the appropriate values
        self.overlap = self.circle.radius + (self.wall.pos - self.circle.pos).dot(self.wall.normal)
        self.normal = self.wall.normal

    def point(self):
        return self.circle.pos - self.circle.radius*self.normal

# Contact class for Circle and a Wall
# Circle is before Wall because it comes before it in the alphabet
class Circle_Wall(Contact):
    def __init__(self, a, b, **kwargs):
        self.circle = a
        self.wall = b
        super().__init__(a, b, **kwargs)

    def update(self):  # compute the appropriate values
        self.overlap = self.circle.radius + (self.wall.pos - self.circle.pos).dot(self.wall.normal)
        self.normal = self.wall.normal

    def point(self):
        return self.circle.pos - self.circle.radius*self.normal

class Circle_Polygon(Contact):
    def __init__(self, a, b, **kwargs):
        self.circle = a
        self.polygon = b
        super().__init__(a, b, **kwargs)

    def point(self):
        return self.circle.pos - self.circle.radius*self.normal

    def update(self):  # compute the appropriate values
        min_overlap = math.inf # Current min overlap
        # Loop over all sides, find index of minimum overlap
        for i, (wall_point, wall_normal) in enumerate(zip(self.polygon.points, self.polygon.normals)):
            overlap = self.circle.radius + (wall_point - self.circle.pos).dot(wall_normal)
            #if overlap is less than min_overlap
            if overlap < min_overlap:
            ## update min_overlap
                min_overlap = overlap
            ## save index
                index = i

        self.overlap = min_overlap
        # self.normal = the normal of the wall of the least overlap
        self.normal = self.polygon.normals[index]

        if 0 < self.overlap < self.circle.radius:
            # Check if the point is beyond one of the endpoints
            endpoint1 = self.polygon.points[index]
            endpoint2 = self.polygon.points[index - 1]
            # if beyond index
            if (self.circle.pos - endpoint1).dot(endpoint1 - endpoint2) > 0:
                ## set new overlap and normal
                r = self.circle.pos - endpoint1
                self.overlap = self.circle.radius - r.magnitude()
                self.normal = r.normalize()
            # elif beyond index - 1
            elif (self.circle.pos - endpoint2).dot(endpoint2 - endpoint1) > 0:
                ## set new overlap and normal
                r = self.circle.pos - endpoint2
                self.overlap = self.circle.radius - r.magnitude()
                self.normal = r.normalize()

class Wall_Wall(Contact):
    def __init__(self, a, b, **kwargs):
        super().__init__(a, b, **kwargs)

class Polygon_Wall(Contact):
    def __init__(self, a, b, **kwargs):
        self.polygon = a
        self.wall = b
        super().__init__(a, b, **kwargs)

    def update(self):
        max_overlap = -math.inf # Current min overlap
        # Loop over all sides, find index of minimum overlap
        for i, point in enumerate(self.polygon.points):
            overlap = (self.wall.pos - point).dot(self.wall.normal)
            #if overlap is less than min_overlap
            if overlap > max_overlap:
            ## update min_overlap
                max_overlap = overlap
            ## save index
                index = i

        self.overlap = max_overlap
        # self.normal = the normal of the wall of the least overlap
        self.normal = self.wall.normal
        self.pt = self.polygon.points[index]

    def point(self):
        return self.pt

class Polygon_Polygon(Contact):
    def __init__(self, a, b, **kwargs):
        super().__init__(a, b, **kwargs)

    def update(self):
        self.overlap = math.inf
        
        for wall_pos, wall_normal in zip(self.a.points, self.a.normals):
            #overlap between polygon and wall
            max_overlap = -math.inf
            for i, point in enumerate(self.b.points):
                overlap = (wall_pos - point).dot(wall_normal)
                if overlap > max_overlap:
                    max_overlap = overlap
                    point_index = i

            if max_overlap < self.overlap:
                self.overlap = max_overlap
                self.normal = -wall_normal
                self.point_index = point_index
                self.point_polygon = self.b
                if self.overlap <= 0:
                    return

        for wall_pos, wall_normal in zip(self.b.points, self.b.normals):
            max_overlap = -math.inf
            for i, point in enumerate(self.a.points):
                overlap = (wall_pos - point).dot(wall_normal)
                if overlap > max_overlap:
                    max_overlap = overlap
                    point_index = i

            if max_overlap < self.overlap:
                self.overlap = max_overlap
                self.normal = wall_normal
                self.point_index = point_index
                self.point_polygon = self.a
                if self.overlap <= 0:
                    return

    def point(self):
        return self.point_polygon.points[self.point_index]