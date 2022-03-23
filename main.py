import math
import random
import numpy as np
import time
from pointQuadTree import *
from rectangle import *
import pygame


class Vector(object):
    """A vector can be determined from a single point when basing
    it from the origin (0,0), but I'm going to assume 2 points.
    Example:
        AB = Vector(Point(3,4),Point(6,7))

    or if you want to use the origin

        AB = Vector(Point(0,0),Point(8,4))
    """

    def __init__(self, p1, p2):
        assert not p1 == None
        assert not p2 == None
        self.p1 = p1
        self.p2 = p2
        self.v = [self.p1.x - self.p2.x, self.p1.y - self.p2.y]
        self.a, self.b = self.v

    def _str__(self):
        return "[\n p1: %s,\n p2: %s,\n vector: %s,\n a: %s,\nb: %s\n]" % (
            self.p1,
            self.p2,
            self.v,
            self.a,
            self.b,
        )

    def __repr__(self):
        return "[\n p1: %s,\n p2: %s,\n vector: %s,\n a: %s,\nb: %s\n]" % (
            self.p1,
            self.p2,
            self.v,
            self.a,
            self.b,
        )


class VectorOps(object):
    """VectorOps give the ability to apply some simple movement to an object.

    @method: _bearing       -- private method to give the bearing going from p1 -> p2
    @method: _magnitude     -- length in this context
    @method: _step          -- a "location change vector" (not correct term) to apply to point p1
                               that will "step" it towards p2. The size of the "step" is
                               based on the velocity.
    """

    def __init__(self, p1=None, p2=None, velocity=1):
        self.p1 = p1
        self.p2 = p2
        self.dx = 0
        self.dy = 0
        if not self.p1 == None and not self.p2 == None:
            self.v = Vector(p1, p2)
            self.velocity = velocity
            self.magnitude = self._magnitude()
            self.bearing = self._bearing()
            self.step = self._step()
        else:
            self.v = None
            self.velocity = None
            self.bearing = None
            self.magnitude = None

    def _bearing(self):
        """
        Calculate the bearing (in radians) between p1 and p2
        """
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        rads = math.atan2(-dy, dx)
        return rads % 2 * math.pi  # In radians
        # degs = degrees(rads)

    def _magnitude(self):
        """
        A vector by itself can have a magnitude when basing it on the origin (0,0),
        but in this context we want to calculate magnitude (length) based on another
        point (converted to a vector).
        """
        assert not self.v == None
        return math.sqrt((self.v.a**2) + (self.v.b**2))

    def _step(self):
        """
        Create the step factor between p1 and p2 to allow a point to
        move toward p2 at some interval based on velocity. Greater velocity
        means bigger steps (less granular).
        """
        cosa = math.sin(self.bearing)
        cosb = math.cos(self.bearing)
        self.dx = cosa * self.velocity
        self.dy = cosb * self.velocity
        return [cosa * self.velocity, cosb * self.velocity]

    def _str__(self):
        return (
            "[\n vector: %s,\n velocity: %s,\n bearing: %s,\n magnitude: %s\n, step: %s\n]"
            % (self.v, self.velocity, self.bearing, self.magnitude, self.step)
        )

    def __repr__(self):
        return (
            "[\n vector: %s,\n velocity: %s,\n bearing: %s,\n magnitude: %s\n, step: %s\n]"
            % (self.v, self.velocity, self.bearing, self.magnitude, self.step)
        )


class Ball:
    """
    Ball is an extension of a point. It doesn't truly "extend" the point class but it
    probably should have! Having said that, I probably should extend the VectorOps class
    as well.

    @method: destination       -- private method to give the bearing going from p1 -> p2
    @method: move              -- length in this context
    @method: xInBounds         -- Helper class to check ... I'll let you guess
    @method: yInBounds         -- Same as previous just vertically :)

    This class is used as follows:

    Given a point, p1, I want to move it somewhere, anywhere. So I do the following:

    1) Create a random point somewhere else on the screen / world / board:
            distance = 100
            degrees = math.radians(random.randint(0,360))
            p2 = destination(distance,degrees)

    2) Now I can calculate a vector between P1 and P2 at a given velocity (scalar value
        to adjust speed)

            velocity = random.randint(1,MaxSpeed) # 1-15 or 20
            vectorOps = VectorOps(p1,p2,velocity)

    3) Finally I have a "step" (or incorrectly coined as a motion vector) that as applied to
        p1 will move it toward p2 at the given step.

            p1.x += vectorOps.dx
            p1.y += vectorOps.dy
    """

    def __init__(self, center, radius, velocity=1, color="#000"):
        self.center = center
        self.radius = radius
        self.velocity = velocity
        self.x = center.x
        self.y = center.y
        self.center = center
        self.bearing = math.radians(random.randint(0, 360))
        self.dest = self.destination(100, self.bearing)
        self.vectorOps = VectorOps(self.center, self.dest, self.velocity)
        self.color = color

    """
    Given a distance and a bearing find the point: P2 (where we would end up).
    """

    def destination(self, distance, bearing):
        cosa = math.sin(bearing)
        cosb = math.cos(bearing)
        return Point(self.x + (distance * cosa), self.y + (distance * cosb))

    """
    Applies the "step" to current location and checks for out of bounds
    """

    def move(self, bounds):
        x = self.x
        y = self.y

        # Move temporarily
        x += self.vectorOps.dx
        y += self.vectorOps.dy

        # Check if in bounds
        # If it's not, then change direction
        if not self._xInBounds(bounds, x):
            self.vectorOps.dx *= -1
            self._change_bearing(math.pi)
        if not self._yInBounds(bounds, y):
            self.vectorOps.dy *= -1

        # Move any way because If we hit boundaries then we'll
        # go in the other direction.
        self.x += self.vectorOps.dx
        self.y += self.vectorOps.dy

        # Update center value of ball
        self.center.x = self.x
        self.center.y = self.y

    def _xInBounds(self, bounds, x):
        if x >= bounds.maxX or x <= bounds.minX:
            return False

        return True

    def _yInBounds(self, bounds, y):
        if y >= bounds.maxY or y <= bounds.minY:
            return False

        return True

    def _change_bearing(self, change):
        """
        Change Bearing
        """
        self.bearing = (self.bearing + change) % (2 * math.pi)

    def changeSpeed(self, new_velocity):
        self.dest = self.destination(100, self.bearing)
        self.velocity = new_velocity
        self.vectorOps = VectorOps(self.center, self.dest, self.velocity)

    def as_tuple(self):
        """
        @returns a tuple (x, y)
        """
        return (self.x, self.y)

    def _str__(self):
        return "[\n center: %s,\n radius: %s,\n vector: %s,\n speed: %s\n ]" % (
            self.center,
            self.radius,
            self.vectorOps,
            self.velocity,
        )

    def __repr__(self):
        return "[\n center: %s,\n radius: %s,\n vector: %s,\n speed: %s\n ]" % (
            self.center,
            self.radius,
            self.vectorOps,
            self.velocity,
        )


class Bounds(object):
    """
    A class more or so to put all the boundary values together. Friendlier than
    using a map type.
    """

    def __init__(self, minx, miny, maxx, maxy):
        self.minX = minx
        self.minY = miny
        self.maxX = maxx
        self.maxY = maxy

    def __repr__(self):
        return "[%s %s %s %s]" % (self.minX, self.minY, self.maxX, self.maxY)


class Driver:
    """
    The driver class that uses pygame

    Dependencies:
        pygame
        Numpy
        Point
        Rectangle
    """

    def __init__(self):
        self.bounds = Bounds(0, 0, self.width, self.height)
        self.BallSpeeds = np.arange(1, 4, 1)
        self.numBalls = 50
        self.qt = PointQuadTree(
            Rectangle(Point(0, 0), Point(self.width, self.height)), 1
        )
        self.BallSize = 5
        self.halfSize = self.BallSize / 2
        self.Balls = []
        self.boxes = []
        self.freeze = False

        for i in range(self.numBalls):

            speed = random.choice(self.BallSpeeds)
            if i == 0:
                color = "#00F"
            else:
                color = "#F00"
            r = Ball(self.getRandomPosition(), self.BallSize, speed, color)
            self.Balls.append(r)
            self.qt.insert(r)

    def update(self):
        """
        Update happens every ? milliseconds. Its not to bad.
        """
        if not self.freeze:
            self.moveBalls()
        self.clear_rect(0, 0, self.width, self.height)
        self.drawBalls()
        self.drawBoxes()
        # time.sleep(.5)

    def checkCollisions(self, r):
        """
        Not Implemented fully. The goal is to use the quadtree to check to see which
        balls collide, then change direction.
        """
        # box = Rectangle(Point(r.center.x-self.halfSize,r.center.y-self.halfSize),Point(r.center.x+self.halfSize,r.center.y+self.halfSize))
        # boxes  = self.qt.searchBox(box)
        # boxes.sort(key=lambda tup: tup[1],reverse=True)
        # #print boxes
        # #print
        pass

    def getRandomPosition(self):
        """
        Generate some random point somewhere within the bounds of the canvas.
        """
        x = random.randint(0 + self.BallSize, int(self.width) - self.BallSize)
        y = random.randint(0 + self.BallSize, int(self.height) - self.BallSize)
        return Point(x, y)

    def drawBoxes(self):
        """
        Draw the bounding boxes fetched from the quadtree
        """
        boxes = self.qt.getBBoxes()
        for box in boxes:
            self.draw_rect(box.left, box.top, box.w, box.h)

    def drawBalls(self):
        """
        Draw the balls :)
        """
        for r in self.Balls:
            self.fill_circle(r.x, r.y, r.radius, r.color)

    def moveBalls(self):
        """
        Moves the balls by applying my super advanced euclidian based geometric
        vector functions to my balls. By super advanced I mean ... not.
        """
        self.qt = PointQuadTree(
            Rectangle(Point(0, 0), Point(self.width, self.height)), 1
        )
        for r in self.Balls:
            self.checkCollisions(r)
            r.move(self.bounds)
            self.qt.insert(r)

    def on_click(self, InputEvent):
        """
        Toggles movement on and off
        """
        if self.freeze == False:
            self.freeze = True
        else:
            self.freeze = False

    def on_key_down(self, InputEvent):
        """
        Dbl Click will speed balls up by some factor
        Shift Dbl Click will slow balls down by same factor
        """
        # User hits the UP arrow
        if InputEvent.key_code == 38:
            print(self.Balls[0].bearing)
            for r in self.Balls:
                r.changeSpeed(r.velocity * 1.25)
        # User hits the DOWN arrow
        if InputEvent.key_code == 40:
            pass


if __name__ == "__main__":
    pass
