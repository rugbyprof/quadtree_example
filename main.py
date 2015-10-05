import math
import random
import numpy as np
import time
from pointQuadTree import *
from Rectangle import *
import pantograph


"""
A vector can be determined from a single point when basing
it from the origin (0,0), but I'm going to assume 2 points.
Example:
    AB = Vector(Point(3,4),Point(6,7))

or if you want to use the origin

    AB = Vector(Point(0,0),Point(8,4))

"""
class Vector(object):
    def __init__(self,p1,p2):
        assert not p1 == None
        assert not p2 == None
        self.p1 = p1
        self.p2 = p2
        self.v = [self.p1.x - self.p2.x, self.p1.y - self.p2.y]
        self.a,self.b = self.v

    def _str__(self):
        return "[\n p1: %s,\n p2: %s,\n vector: %s,\n a: %s,\nb: %s\n]" % (self.p1, self.p2, self.v,self.a,self.b)

    def __repr__(self):
        return "[\n p1: %s,\n p2: %s,\n vector: %s,\n a: %s,\nb: %s\n]" % (self.p1, self.p2, self.v,self.a,self.b)

"""
VectorOps give the ability to apply some simple movement to an object.

@method: _bearing       -- private method to give the bearing going from p1 -> p2
@method: _magnitude     -- length in this context
@method: _step          -- a "motion vector" (not correct term) to apply to point p1
                           that will "step" it towards p2. The size of the "step" is
                           based on the velocity.

"""
class VectorOps(object):
    def __init__(self,p1=None,p2=None,velocity=1):
        self.p1 = p1
        self.p2 = p2
        self.dx = 0
        self.dy = 0
        if not self.p1 == None and not self.p2 == None:
            self.v = Vector(p1,p2)
            self.velocity = velocity
            self.magnitude = self._magnitude()
            self.bearing = self._bearing()
            self.step = self._step()
        else:
            self.v = None
            self.velocity = None
            self.bearing = None
            self.magnitude = None

    """
    Calculate the bearing (in radians) between p1 and p2
    """
    def _bearing(self):
        dx = self.p2.x - self.p1.x
        dy = self.p2.y - self.p1.y
        rads = math.atan2(-dy,dx)
        return rads % 2*math.pi         # In radians
        #degs = degrees(rads)
    """
    A vector by itself can have a magnitude when basing it on the origin (0,0),
    but in this context we want to calculate magnitude (length) based on another
    point (converted to a vector).
    """
    def _magnitude(self):
        assert not self.v == None
        return math.sqrt( (self.v.a**2) + (self.v.b**2) )

    """
    Create the step factor between p1 and p2 to allow a point to
    move toward p2 at some interval based on velocity. Greater velocity
    means bigger steps (less granular).
    """
    def _step(self):
        cosa = math.sin(self.bearing)
        cosb = math.cos(self.bearing)
        self.dx = cosa * self.velocity
        self.dy = cosb * self.velocity
        return [cosa * self.velocity, cosb * self.velocity]

    def _str__(self):
        return "[\n vector: %s,\n velocity: %s,\n bearing: %s,\n magnitude: %s\n, step: %s\n]" % (self.v, self.velocity, self.bearing,self.magnitude,self.step)

    def __repr__(self):
        return "[\n vector: %s,\n velocity: %s,\n bearing: %s,\n magnitude: %s\n, step: %s\n]" % (self.v, self.velocity, self.bearing,self.magnitude,self.step)

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
class Ball():
    def __init__(self, center, radius,velocity=1,color="#000"):
        self.center = center
        self.radius = radius
        self.velocity = velocity
        self.x = center.x
        self.y = center.y
        self.center = center
        self.dest = self.destination(100,math.radians(random.randint(0,360)))
        self.vectorOps = VectorOps(self.center,self.dest,self.velocity)
        self.color = color

    """
    Given a distance and a bearing find the point: P2 (where we would end up).
    """
    def destination(self,distance,bearing):
        cosa = math.sin(bearing)
        cosb = math.cos(bearing)
        return Point(self.x + (distance * cosa), self.y + (distance * cosb))

    """
    Applies the "step" to current location and checks for out of bounds
    """
    def move(self,bounds):
        x = self.x
        y = self.y

        #Move temporarily
        x += self.vectorOps.dx
        y += self.vectorOps.dy

        #Check if in bounds
        #If it's not, then change direction
        if not self._xInBounds(bounds,x):
            self.vectorOps.dx *= -1
        if not self._yInBounds(bounds,y):
            self.vectorOps.dy *= -1

        # Move any way because If we hit boundaries then we'll
        # go in the other direction.
        self.x += self.vectorOps.dx
        self.y += self.vectorOps.dy

        # Update center value of ball
        self.center.x = self.x
        self.center.y = self.y


    def _xInBounds(self,bounds,x):
        if x >= bounds.maxX or x <= bounds.minX :
            return False

        return True

    def yInBounds(self,bounds,y):
        if y >= bounds.maxY or y <= bounds.minY:
            return False

        return True

    """
    @returns a tuple (x, y)
    """
    def as_tuple(self):
        return (self.x, self.y)


    def _str__(self):
        return "[\n center: %s,\n radius: %s,\n vector: %s,\n speed: %s\n ]" % (self.center,self.radius, self.vectorOps,self.velocity)

    def __repr__(self):
        return "[\n center: %s,\n radius: %s,\n vector: %s,\n speed: %s\n ]" % (self.center, self.radius, self.vectorOps,self.velocity)

"""
A class more or so to put all the boundary values together. Friendlier than
using a map type.
"""
class Bounds(object):
    def __init__(self,minx,miny,maxx,maxy):
        self.minX = minx
        self.minY = miny
        self.maxX = maxx
        self.maxY = maxy
    def __repr__(self):
        return "[%s %s %s %s]" % (self.minX, self.minY, self.maxX,self.maxY)


"""
The driver class that extends the Pantograph class that creates the html 5
canvas animations.

If you run this file from the command line "python visualizeQuadtree.py"
Pantograph will start a local server running at address: http://127.0.0.1:8080
Simply place "http://127.0.0.1:8080" in the address bar of a browser and hit enter.

Dependencies:

    Pantograph:
        pip install pantograph
    Numpy
    Point
    Rectangle
"""
class Driver(pantograph.PantographHandler):

    """
    Sets up canvas, generates balls, etc.
    """
    def setup(self):
        self.bounds = Bounds(0,0,self.width,self.height)
        self.BallSpeeds = np.arange(1,15,1)
        self.numBalls = 50
        self.qt = PointQuadTree(Rectangle(Point(0,0),Point(self.width,self.height)),1)
        self.BallSize = 5
        self.halfSize = self.BallSize / 2
        self.Balls = []
        self.boxes = []

        for i in range(self.numBalls):

            speed = random.choice(self.BallSpeeds)

            r = Ball(self.getRandomPosition(),self.BallSize,speed,"#F00")
            self.Balls.append(r)
            self.qt.insert(r)

    """
    Runs the animation. Update happens every ? milliseconds. Its not to bad.
    """
    def update(self):
        self.moveBalls()
        self.clear_rect(0, 0, self.width, self.height)
        self.drawBalls()
        self.drawBoxes();
        #time.sleep(.5)

    """
    Not Implemented fully. The goal is to use the quadtree to check to see which
    balls collide, then change direction.
    """
    def checkCollisions(self,r):
        box = Rectangle(Point(r.center.x-self.halfSize,r.center.y-self.halfSize),Point(r.center.x+self.halfSize,r.center.y+self.halfSize))
        boxes  = self.qt.searchBox(box)
        boxes.sort(key=lambda tup: tup[1],reverse=True)
        #print boxes
        #print

    """
    Generate some random point somewhere within the bounds of the canvas.
    """
    def getRandomPosition(self):
        x = random.randint(0+self.BallSize,int(self.width)-self.BallSize)
        y = random.randint(0+self.BallSize,int(self.height)-self.BallSize)
        return Point(x,y)


    """
    Draw the bounding boxes fetched from the quadtree
    """
    def drawBoxes(self):
        boxes = self.qt.getBBoxes()
        for box in boxes:
            self.draw_rect(box.left,box.top,box.w,box.h)

    """
    Draw the balls :)
    """
    def drawBalls(self):
        for r in self.Balls:
            self.fill_circle(r.x,r.y,r.radius,r.color)

    """
    Moves the balls by applying my super advanced euclidian based geometric
    vector functions to my balls. By super advanced I mean ... not.
    """
    def moveBalls(self):
        self.qt = PointQuadTree(Rectangle(Point(0,0),Point(self.width,self.height)),1)
        for r in self.Balls:
            self.checkCollisions(r)
            r.move(self.bounds)
            self.qt.insert(r)


if __name__ == '__main__':
    app = pantograph.SimplePantographApplication(Driver)
    app.run()
