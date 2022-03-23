import math


class Point(object):
    """
    class Point:

        A point identified by (x,y) coordinates.

    @operations: +, -, *, /, str, repr
    @method: length         -- calculate length of vector to point from origin
    @method: distance_to    -- calculate distance between two points
    @method: as_tuple       -- construct tuple (x,y)
    @method: clone          -- construct a duplicate
    @method: integerize     -- convert x & y to integers
    @method: floatize       -- convert x & y to floats
    @method: move_to        -- reset x & y
    @method: goto_point     -- move (in place) +dx, +dy, as spec'd by point
    @method: move_to_xy     -- move (in place) +dx, +dy
    @method: rotate         -- rotate around the origin
    @method: rotate_about   -- rotate around another point

    source: https://wiki.python.org/moin/PointsAndRectangles
    """

    def __init__(self, x=0.0, y=0.0, data=None):
        self.x = float(x)
        self.y = float(y)

        self.data = data

    def __add__(self, p):
        """
        @returns Point(x1+x2, y1+y2)
        """
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        """
        @returns Point(x1-x2, y1-y2)
        """
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, scalar):
        """
        Point(x1*x2, y1*y2)
        """
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        """
        Point(x1/x2, y1/y2)
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

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def distance_to(self, p):
        """
        Calculate the distance between two points.
        @returns distance
        """
        return (self - p).length()

    def as_tuple(self):
        """
        @returns a tuple (x, y)
        """
        return (self.x, self.y)

    def clone(self):
        """
        Return a full copy of this point.
        """
        return Point(self.x, self.y)

    def integerize(self):
        """
        Convert co-ordinate values to integers.
        @returns Point(int(x),int(y))
        """
        self.x = int(self.x)
        self.y = int(self.y)

    def floatize(self):
        """
        Convert co-ordinate values to floats.
        @returns Point(float(x),float(y))
        """
        self.x = float(self.x)
        self.y = float(self.y)

    def move_to(self, x, y):
        """
        Moves / sets point to x,y .
        """
        self.x = x
        self.y = y

    def goto_point(self, p):
        """
        Move to new (x+dx,y+dy).
        """
        self.x = self.x + p.x
        self.y = self.y + p.y

    def move_to_xy(self, dx, dy):
        """
        Move to new (x+dx,y+dy).
        """
        self.x = self.x + dx
        self.y = self.y + dy

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

    def set_direction(self, direction):
        assert direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        self.direction = direction

    def update_position(self):
        if self.direction == "N":
            self.y -= 1
        if self.direction == "NE":
            self.y -= 1
            self.x += 1
        if self.direction == "E":
            self.x += 1
        if self.direction == "SE":
            self.x += 1
            self.y += 1
        if self.direction == "S":
            self.y += 1
        if self.direction == "SW":
            self.x -= 1
            self.y += 1
        if self.direction == "W":
            self.x -= 1
        if self.direction == "NW":
            self.y -= 1
            self.x -= 1


if __name__ == "__main__":
    p = Point()
    print(p)
