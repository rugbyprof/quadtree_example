from rich import print
from point import Point
from rectangle import *
from random import random


class PointQuadTree(object):
    def __init__(self, bbox, maxPoints, parent=0):
        self.northEast = None
        self.southEast = None
        self.southWest = None
        self.northWest = None

        self.points = []
        self.bbox = bbox
        self.maxPoints = maxPoints
        self.parent = parent

    def __str__(self):
        return (
            "\nnorthwest: %s,\nnorthEast: %s,\nsouthWest: %s,\nsouthEast: %s,\npoints: %s,\nbbox: %s,\nmaxPoints: %s,\nparent: %s"
            % (
                self.northWest,
                self.northEast,
                self.southWest,
                self.southEast,
                self.points,
                self.bbox,
                self.maxPoints,
                self.parent,
            )
        )

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
            Rectangle(Point(mX, t), Point(r, mY)), self.maxPoints, self.parent + 1
        )
        self.southEast = PointQuadTree(
            Rectangle(Point(mX, mY), Point(r, b)), self.maxPoints, self.parent + 1
        )
        self.southWest = PointQuadTree(
            Rectangle(Point(l, mY), Point(mX, b)), self.maxPoints, self.parent + 1
        )
        self.northWest = PointQuadTree(
            Rectangle(Point(l, t), Point(mX, mY)), self.maxPoints, self.parent + 1
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


if __name__ == "__main__":
    width = 500
    height = 500
    maxPoints = 1000
    bbox = Rectangle(Point(0, 0), Point(width, height))
    qt = PointQuadTree(bbox, 50, parent=0)
    for i in range(maxPoints):
        x = int(width * random())
        y = int(height * random())
        p = Point(x, y, i)
        qt.insert(p)
        print(p)
    print(qt)
    res = qt.searchNeighbors(Point(70.0, 311.0))
    print(res)
    print(len(res))
