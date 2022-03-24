# from xml.sax import handler
# from matplotlib.cbook import index_of
from rich import print
from point import Point
from rectangle import *
import random
from random import choice

width = 1024
height = 768


class qtPoint(Point):
    def __init__(self, x, y, data=None, color=(255, 255, 255), radius=2):
        Point.__init__(self, x, y)
        self.data = data
        self.color = color
        self.dx = 3
        self.dy = 3
        self.radius = radius

    def setRadius(self, r):
        self.radius = r

    def set_dx_dy(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def setColor(self, color):
        self.color = color

    def set_direction(self, direction):
        assert direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        self.direction = direction

    def update_position(self):
        if self.direction == "N":
            self.y -= self.dy
        if self.direction == "NE":
            self.y -= self.dy
            self.x += self.dx
        if self.direction == "E":
            self.x += self.dx
        if self.direction == "SE":
            self.x += self.dx
            self.y += self.dy
        if self.direction == "S":
            self.y += self.dy
        if self.direction == "SW":
            self.x -= self.dx
            self.y += self.dy
        if self.direction == "W":
            self.x -= self.dx
        if self.direction == "NW":
            self.y -= self.dy
            self.x -= self.dx


class PointQuadTree(object):
    def __init__(self, bbox, maxPoints, parent=0):
        self.maxPoints = maxPoints
        self.parent = parent
        self.bboxOriginal = bbox
        self.bbox = bbox

        self.init()

    def init(self):

        self.parent = 0
        self.northEast = None
        self.southEast = None
        self.southWest = None
        self.northWest = None
        self.bbox = self.bboxOriginal
        self.points = []

    def __str__(self):
        return "\nnorthwest: %s,\nnorthEast: %s,\nsouthWest: %s,\nsouthEast: %s,\npoints: %s,\nbbox: %s,\nmaxPoints: %s,\nparent: %s" % (
            self.northWest,
            self.northEast,
            self.southWest,
            self.southEast,
            self.points,
            self.bbox,
            self.maxPoints,
            self.parent,
        )

    def reset(self, points):
        self.init()
        for point in points:
            self.insert(point)

    def insert(self, point):
        """
        Insert a new point into this QuadTree node
        """
        if not self.bbox.contains(point):
            # print "Point %s is not inside bounding box %s" % (point,self.bbox)
            return False

        if len(self.points) < self.maxPoints:
            # If we still have spaces in the bucket array for this QuadTree node,
            #    then the point simply goes here and we're finished
            self.points.append(point)
            return True
        elif self.northEast == None:
            # Otherwise we split this node into NW/NE/SE/SW quadrants
            self.subdivide()

        # Insert the point into the appropriate quadrant, and finish
        if (
            (self.northEast.insert(point))
            or (self.southEast.insert(point))
            or (self.southWest.insert(point))
            or (self.northWest.insert(point))
        ):
            return True

        # If we couldn't insert the new point, then we have an exception situation
        raise ValueError("Point %s is outside bounding box %s" % (point, self.bbox))

    def subdivide(self):
        """
        Split this QuadTree node into four quadrants for NW/NE/SE/SW
        """
        l = self.bbox.left
        r = self.bbox.right
        t = self.bbox.top
        b = self.bbox.bottom
        mX = (l + r) / 2
        mY = (t + b) / 2
        self.northEast = PointQuadTree(
            Rectangle(p1=Point(mX, t), p2=Point(r, mY)), self.maxPoints, self.parent + 1
        )
        self.southEast = PointQuadTree(
            Rectangle(p1=Point(mX, mY), p2=Point(r, b)), self.maxPoints, self.parent + 1
        )
        self.southWest = PointQuadTree(
            Rectangle(p1=Point(l, mY), p2=Point(mX, b)), self.maxPoints, self.parent + 1
        )
        self.northWest = PointQuadTree(
            Rectangle(p1=Point(l, t), p2=Point(mX, mY)), self.maxPoints, self.parent + 1
        )

    def searchBox(self, bbox):
        """Return an array of all points within this QuadTree and its child nodes that fall
        within the specified bounding box
        """
        results = []

        if self.bbox.overlaps(bbox) or self.bbox.encompasses(bbox):
            # Test each point that falls within the current QuadTree node
            for p in self.points:
                # Test each point stored in this QuadTree node in turn, adding to the results array
                #    if it falls within the bounding box
                if self.bbox.contains(p):
                    results.append((bbox, self.parent))

            # If we have child QuadTree nodes....
            if not self.northWest == None:
                # ... search each child node in turn, merging with any existing results
                results = results + self.northWest.searchBox(self.bbox)
                results = results + self.northEast.searchBox(self.bbox)
                results = results + self.southWest.searchBox(self.bbox)
                results = results + self.southEast.searchBox(self.bbox)

        return results

    def searchNeighbors(self, point):
        """Returns the containers points that are in the same container as another point."""
        # If its not a point (its a bounding rectangle)
        if not hasattr(point, "x"):
            return []

        results = []

        if self.bbox.containsPoint(point):
            # Test each point that falls within the current QuadTree node
            for p in self.points:
                # Test each point stored in this QuadTree node in turn, adding to the results array
                #    if it falls within the bounding box
                if self.bbox.containsPoint(p):
                    results.append(p)

            # If we have child QuadTree nodes....
            if not self.northWest == None:
                # ... search each child node in turn, merging with any existing results
                results = results + self.northWest.searchNeighbors(point)
                results = results + self.northEast.searchNeighbors(point)
                results = results + self.southWest.searchNeighbors(point)
                results = results + self.southEast.searchNeighbors(point)

        return results

    def getBBoxes(self):
        """Print helper to draw tree"""
        bboxes = []

        bboxes.append(self.bbox)

        if not self.northWest == None:
            # ... search each child node in turn, merging with any existing results
            bboxes = bboxes + self.northWest.getBBoxes()
            bboxes = bboxes + self.northEast.getBBoxes()
            bboxes = bboxes + self.southWest.getBBoxes()
            bboxes = bboxes + self.southEast.getBBoxes()

        return bboxes


def drawPoints(screen, points):
    for p in points:
        pygame.draw.circle(screen, p.color, [p.x, p.y], p.radius)


def updatePoints(points, width, height):

    old = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    new = ["S", "SW", "W", "NW", "N", "NE", "E", "SE"]

    dx = 3
    dy = 3
    for p in points:
        # p.update_position()
        d = list(p.direction)
        # print("+" * 20)
        # print(d)
        if p.x > width or p.x < 0:
            i = p.direction.find("E")
            if i >= 0:
                d[i] = "W"

            i = p.direction.find("W")
            if i >= 0:
                d[i] = "E"
        if p.y > height or p.y < 0:
            i = p.direction.find("N")
            if i >= 0:
                d[i] = "S"

            i = p.direction.find("S")
            if i >= 0:
                d[i] = "N"

        p.direction = "".join(d)
        # print(p.direction)
        # print("-" * 20)

        p.update_position()
        # pygame.draw.circle(screen, (255, 255, 255), [p.x, p.y], 2)

    return points


def drawRects(screen, rects):
    """left, top, width, height"""
    for r in rects:
        l = r.left
        t = r.top
        w = r.w
        h = r.h
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(l, t, w, h), 1)


if __name__ == "__main__":
    import pygame

    dPoints = []
    dRects = []

    pygame.init()
    width, height = (1024, 768)
    screen = pygame.display.set_mode((width, height))
    done = False
    clock = pygame.time.Clock()

    width = 1024
    height = 768
    maxPoints = 50

    bbox = Rectangle(p1=Point(0, 0), p2=Point(width, height))
    qt = PointQuadTree(bbox, 1, 0)

    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    id = 0
    while id < maxPoints:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = (r, g, b)
        x = int(width * random.random())
        y = int(height * random.random())
        p = qtPoint(x, y, id, color, 3)
        p.set_dx_dy(3, 3)
        p.set_direction(choice(dirs))
        qt.insert(p)
        dPoints.append(p)
        id += 1

    while not done:
        pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

        if pos:
            print(pos)
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = (0, 255, 0)
            p = qtPoint(pos[0], pos[1], id, (r, g, b), 10)
            p.set_dx_dy(10, 10)
            p.set_direction(choice(dirs))
            qt.insert(p)
            dPoints.append(p)
            id += 1

        screen.fill((0, 0, 0))

        bboxes = qt.getBBoxes()
        dPoints = updatePoints(dPoints, width, height)

        drawPoints(screen, dPoints)
        drawRects(screen, bboxes)

        qt.reset(dPoints)
        # print(bboxes)

        pygame.display.flip()
        clock.tick(60)

    # print(qt)
    # res = qt.searchNeighbors(Point(70.0, 311.0))
    # print(res)
    # print(len(res))
