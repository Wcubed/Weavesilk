__author__ = 'wybe'
# Python 3.4.3


import math


class Vector:
    """
    Vector class.
    """

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def __add__(self, other):
        """
        Adds two vectors together.
        """
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        Subtracts two vectors from each other.
        """
        return Vector(self.x - other.x, self.y - other.y)

    def __str__(self):
        """
        Converts the vector into a human readable string.
        """
        return "<" + str(self.x) + ", " + str(self.y) + ">"

    def get_head(self):
        """
        Returns the heading of the vector.
        """
        return math.atan2(self.y, self.x)

    def get_mag(self):
        """
        Returns the magnitude of the vector.
        """
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    def set_head(self, heading):
        """
        Sets the heading of the vector and keeps the magnitude the same.
        """
        mag = self.get_mag()

        self.x = math.cos(heading) * mag
        self.y = math.sin(heading) * mag

    def set_mag(self, magnitude):
        """
        Sets the magnitude of the vector and keeps the heading the same.
        """
        head = self.get_head()

        self.x = math.cos(head) * magnitude
        self.y = math.sin(head) * magnitude

    def mult(self, factor):
        """
        Multiplies the vector with the factor.
        """
        mag = self.get_mag()
        self.set_mag(mag * factor)

    def rotate(self, angle):
        """
        Rotates the vector by the angle.
        """
        head = self.get_head()
        self.set_head(head + angle)
