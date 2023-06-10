import pygame
from pygame.math import Vector2
import math

class PhysicsObject:
    #constructor
    def __init__(self, pos, vel = (0,0), mass = 1, angle = 0, avel = 0, momi = math.inf):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.point = None
        self.clear_force()

    def clear_force(self):
        self.force = Vector2(0,0)
        self.torque = 0

    def add_force(self, force):
        self.force += force

    def add_torque(self, torque):
        self.torque += torque

    def update(self, dt):
        # update velocity using the current force
        self.vel += (self.force / self.mass) * dt
        # update position using the newly updated velocity
        self.pos += self.vel * dt
        #update angular vel using the current torque
        self.avel += self.torque / self.momi * dt
        #update angle using the newly updated angular velocity
        self.angle += self.avel * dt

    def delta_pos(self, delta):
        self.pos += delta
    
    def set_pos(self, pos):
        self.pos = pos

    def impulse(self, impulse, point):
        self.vel += impulse / self.mass
        if point is not None:
            s = Vector2(point) - self.pos
            self.avel += s.cross(impulse)/self.momi


class Circle(PhysicsObject):
    def __init__(self, window, radius=100, color=(255,0,0), width=0, **kwargs):
        self.window = window
        self.radius = radius
        self.color = color
        self.width = width
        self.contact_type = "Circle"
        super().__init__(**kwargs)

    def draw(self):
        pygame.draw.circle(self.window, self.color, self.pos, self.radius, self.width)
        pygame.draw.line(self.window, (255, 255, 255), self.pos, 
                        self.pos + self.radius*Vector2(0, -1).rotate_rad(self.angle))

class Wall(PhysicsObject):
    def __init__(self, window, start_point, end_point, reverse = False, color=(255,255,255), width=1):
        self.window = window
        self.start_point = Vector2(start_point)
        self.end_point = Vector2(end_point)
        self.color = color
        self.width = width
        self.reverse = reverse
        self.contact_type = "Wall"
        super().__init__(pos=(self.start_point+self.end_point)/2, mass=math.inf)
        self.update_wall()

    def update_wall(self):
        self.pos = (self.start_point+self.end_point)/2
        self.normal = (self.end_point - self.start_point).rotate(90).normalize()
        if self.reverse:
            self.normal *= -1

    def draw(self):
        pygame.draw.line(self.window, self.color, self.start_point, self.end_point, self.width)

class Polygon(PhysicsObject):
    def __init__(self, window, local_points = [], color=(255,0,0), reverse = False, width=0, **kwargs):
        self.window = window
        self.color = color
        self.width = width
        self.reverse = reverse
        self.contact_type = "Polygon"
        super().__init__(**kwargs)

        self.local_points = []
        for p in local_points:
            self.local_points.append(Vector2(p))
        self.points = self.local_points.copy()

        self.local_normals = []
        for i in range(len(self.local_points)):
            normal = (self.local_points[i] - self.local_points[i-1]).normalize().rotate(90)
            self.local_normals.append(normal)
        self.normals = self.local_normals.copy()

        self.update_polygon()

    def update_polygon(self):
        for i, p in enumerate(self.local_points):
            self.points[i] = self.pos + p.rotate_rad(self.angle)
            self.normals[i] = self.local_normals[i].rotate_rad(self.angle)

    def set_pos(self, pos):
        self.pos = pos
        self.update_polygon()

    def update(self, dt):
        super().update(dt)
        self.update_polygon()

    def delta_pos(self, delta):
        super().delta_pos(delta)
        self.update_polygon()

    def draw(self):
        pygame.draw.polygon(self.window, self.color, self.points, self.width)
        #for p, n in zip(self.points, self.normals):
            #pygame.draw.line(self.window, self.color, p, p + 50*n)

class UniformCircle(Circle):
    def __init__(self, window, density=1, radius = 100, **kwargs):
        # calculate mass and moment of inertia
        mass = density * math.pi * radius**2
        momi = 0.5 * mass * radius**2
        super().__init__(window, mass=mass, momi=momi, radius = radius, **kwargs)

class UniformPolygon(Polygon):
    def __init__(self, window, density=1, local_points=[], pos=[0,0], angle=0, shift=True, **kwargs):
        # Calculate mass, moment of inertia, and center of mass
        # by looping over all "triangles" of the polygon
        mass = 0
        momi = 0
        com_numerator = Vector2(0,0)
        for i in range(len(local_points)):
            r1 = Vector2(local_points[i - 1])
            r2 = Vector2(local_points[i])
            # triangle mass
            tri_mass = density * 0.5 * r1.cross(r2)
            # triangle moment of inertia
            tri_momi = tri_mass/6 * (r1*r1 + r2*r2 + r1*r2)
            # triangle center of mass
            tri_com = 1/3 * (r2 + r1)
            tri_com_numerator = tri_mass * tri_com

            # add to total mass
            mass += tri_mass
            # add to total moment of inertia
            momi += tri_momi
            # add to center of mass numerator
            com_numerator += tri_com_numerator
        
        # calculate total center of mass by dividing numerator by denominator (total mass)
        com = com_numerator / mass

        if shift:
            # Shift loca_points by com
            for i in range(len(local_points)):
                local_points[i] -= com
            # shift pos
            pos - com + pos
            # Use parallel axis theorem to correct the moment of inertia
            momi -= mass * com.magnitude_squared()

        # Then call super().__init__() with those correct values
        super().__init__(window, mass=mass, momi=momi, local_points=local_points, pos=pos, angle=angle, **kwargs)