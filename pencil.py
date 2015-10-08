__author__ = 'wybe'


import math
import copy

from vector import Vector


class Pencil:
    """
    Moves after a target in semi random patterns, drawing colored lines.
    """
    def __init__(self, x, y, r, g, b, a):

        # ---- Parameters. ----

        self._max_vel = 500
        self._max_acc = 100

        # ---- Variables ----

        self._pos = Vector(x, y)

        self._last_pos = Vector(x, y)

        self._vel = Vector(0, 0)

        self._col = (r, g, b, a)

    def update(self, dt, t_x, t_y):
        """
        Lets the pencil move, returns the line drawn this frame.
        :param dt: Deltatime.
        :param t_x: Target x.
        :param t_y: Target y.
        :return: Line.
        """

        self._last_pos = copy.copy(self._pos)

        # Calculate the distance from the target.
        dist = Vector(t_x - self._pos.x, t_y - self._pos.y)

        # ---- Calculate acceleration. ----

        acc = Vector(1, 0)

        # Set the heading.
        acc.set_head(dist.get_head())

        # Set the force according to the distance, but not higher than _max_acc.
        acc.set_mag(0.5 * dist.get_mag())

        # ---- Update velocity. ----

        dt_acc = copy.copy(acc)
        dt_acc.mult(dt)

        self._vel += dt_acc

        # Enforce the maximum speed.
        if self._vel.get_mag() > self._max_vel:
            self._vel.set_mag(self._max_vel)

        # ---- Update position. ----

        dt_vel = copy.copy(self._vel)
        dt_vel.mult(dt)

        self._pos += dt_vel

        # Create a line between the last point and the new point.
        line = Line(self._last_pos.x, self._last_pos.y, self._pos.x, self._pos.y,
                    self._col[0], self._col[1], self._col[2], self._col[3])

        return line

class Line:
    """
    Class to represent a line with a color.
    """
    def __init__(self, start_x, start_y, end_x, end_y, r, g, b, a):
        self.start_x = start_x
        self.start_y = start_y

        self.end_x = end_x
        self.end_y = end_y

        self.r = r
        self.g = g
        self.b = b
        self.a = a

        self.col = (r, g, b, a)
