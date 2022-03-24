import math


class Point(object):
    """
    class Point:

        A point identified by (x,y) coordinates.

    @operations: +, -, *, /, str, repr
    @method: _length        -- calculate length of vector to point from origin
    @method: distanceTo     -- calculate distance between two points
    @method: asTuple        -- construct tuple (x,y)
    @method: clone          -- construct a duplicate
    @method: castInt        -- convert x & y to integers
    @method: castFloat      -- convert x & y to floats
    @method: jumpTo         -- reset x & y
    @method: gotoPoint      -- move (in place) +dx, +dy, as spec'd by point
    @method: moveTo         -- move (in place) +dx, +dy
    @method: rotate         -- rotate around the origin
    @method: rotate_about   -- rotate around another point

    source: https://wiki.python.org/moin/PointsAndRectangles
    """

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        """Overload + operater
        Params:
            other : Point(x2,y2)
        Returns:
            Point(x1+x2, y1+y2)
        """
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Overload - operater
        Params:
            other : Point(x2,y2)
        Returns:
            Point(x1-x2, y1-y2)
        """
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Overload * operater
        Params:
            scalar : int value
        Returns:
            Point(x*scalar, y*scalar)
        """
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """Overload / operater
        Params:
            scalar : int value
        Returns:
            Point(x/scalar, y/scalar)
        """
        return Point(self.x / scalar, self.y / scalar)

    def __str__(self):
        if self.data:
            return f"({self.x}, {self.y}, {self.data})"
        else:
            return f"({self.x}, {self.y})"

    def __repr__(self):
        if self.data:
            return f"{self.__class__.__name__}, ({self.x}, {self.y}, {self.data})"
        else:
            return f"{self.__class__.__name__}, ({self.x}, {self.y})"

    def _length(self):
        """Displacement vector. Used in conjunction with distanceTo"""
        return math.sqrt(self.x**2 + self.y**2)

    def distanceTo(self, p):
        """Distance to another point
        Params:
            other : Point(x2,y2)
        Returns:
            float : distance
        """
        return (self - p)._length()

    def asTuple(self):
        """Point to tuple
        Params:
            None
        Returns:
            tuple : (x,y)
        """
        return (self.x, self.y)

    def clone(self):
        """Return a full copy of this point.
        Params:
            None
        Returns:
            Point : Point(x,y)
        """
        return Point(self.x, self.y)

    def castInt(self):
        """Cast co-ordinate values to integers.
        Params:
            None
        Returns:
            None
        """
        self.x = int(self.x)
        self.y = int(self.y)

    def castFloat(self):
        """Cast co-ordinate values to floats.
        Params:
            None
        Returns:
            None
        """
        self.x = float(self.x)
        self.y = float(self.y)

    def jumpTo(self, x, y):
        """Transport this point to new x,y
        Params:
            x (int) : x coord
            y (int) : y coord
        Returns:
            None
        """
        self.x = x
        self.y = y

    def moveTo(self, dx, dy):
        """Move this point by adding a change to x,y
        Params:
            dx (int) : x shift
            dy (int) : y shift
        Returns:
            None
        """
        self.x = self.x + dx
        self.y = self.y + dy

    def gotoPoint(self, target):
        """Same as jumpTo, but uses a point as a param
        Params:
            target (Point) : point to go to
        Returns:
            None
        """
        self.x = self.x + target.x
        self.y = self.y + target.y

    def rotate(self, rad):
        """
        Rotate counter-clockwise by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        """
        Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide(-p.x, -p.y)
        result.rotate(theta)
        result.slide(p.x, p.y)
        return result


if __name__ == "__main__":
    p = Point()
    print(p)
