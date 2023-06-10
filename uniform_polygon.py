''' Copy this into your physics_objects.py file! '''

class UniformCircle(Circle):
    def __init__(self, window, density=1, **kwargs):
        # calculate mass and moment of inertia
        super().__init__(mass=mass, momi=momi, **kwargs)


class UniformPolygon(Polygon):
    def __init__(self, window, density=1, local_points=[], pos=[0,0], angle=0, shift=True, **kwargs):
        # Calculate mass, moment of inertia, and center of mass
        # by looping over all "triangles" of the polygon
        for i in range(len(local_points)):
            # triangle mass
            # triangle moment of inertia
            # triangle center of mass

            # add to total mass
            # add to total moment of inertia
            # add to center of mass numerator
            pass
        
        # calculate total center of mass by dividing numerator by denominator (total mass)

        if shift:
            # Shift loca_points by com
            for i in range(len(local_points)):
                local_points[i] -= com
            # shift pos
            # Use parallel axis theorem to correct the moment of inertia
            pass

        # Then call super().__init__() with those correct values
        super().__init__(window, mass=total_mass, momi=total_momi, local_points=local_points, pos=pos, angle=angle, **kwargs) 
