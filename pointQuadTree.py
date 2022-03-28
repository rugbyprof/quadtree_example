# from xml.sax import handler
# from matplotlib.cbook import index_of
# from jinja2 import pass_eval_context
from rich import print
from point import Point
from rectangle import *
import random
from random import choice

# width = 1024
# height = 768


# class qtPoint(Point):
#     def __init__(self, x, y, data=None, color=(255, 255, 255), radius=2):
#         Point.__init__(self, x, y)
#         self.data = data
#         self.color = color
#         self.dx = 3
#         self.dy = 3
#         self.radius = radius

#     def setRadius(self, r):
#         self.radius = r

#     def set_dx_dy(self, dx, dy):
#         self.dx = dx
#         self.dy = dy

#     def setColor(self, color):
#         self.color = color

#     def set_direction(self, direction):
#         assert direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

#         self.direction = direction

#     def update_position(self):
#         if self.direction == "N":
#             self.y -= self.dy
#         if self.direction == "NE":
#             self.y -= self.dy
#             self.x += self.dx
#         if self.direction == "E":
#             self.x += self.dx
#         if self.direction == "SE":
#             self.x += self.dx
#             self.y += self.dy
#         if self.direction == "S":
#             self.y += self.dy
#         if self.direction == "SW":
#             self.x -= self.dx
#             self.y += self.dy
#         if self.direction == "W":
#             self.x -= self.dx
#         if self.direction == "NW":
#             self.y -= self.dy
#             self.x -= self.dx

colorDict = {
    "Black": (0, 0, 0),
    "Red": (255, 0, 0),
    "Lime": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Silver": (192, 192, 192),
    "Gray": (128, 128, 128),
    "Maroon": (128, 0, 0),
    "Olive": (128, 128, 0),
    "Green": (0, 128, 0),
    "Purple": (128, 0, 128),
    "Teal": (0, 128, 128),
    "Navy": (0, 0, 128),
    "White": (255, 255, 255),
    "Yellow": (255, 255, 0),
}

colorList = list(colorDict.values())


class PointQuadTree(object):
    def __init__(self, bbox, maxPoints, parent=0):
        self.maxPoints = maxPoints
        self.parent = parent
        self.bboxOriginal = bbox
        self.bbox = bbox
        self.color = colorList[self.parent]
        self.points = []

        self.init()

    def init(self):

        self.northEast = None
        self.southEast = None
        self.southWest = None
        self.northWest = None
        self.bbox = self.bboxOriginal
        self.points = []

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

    def reset(self, points):
        self.init()
        for point in points:
            if isinstance(point, Point):
                self.insert(point)
            else:
                self.insert(Point(point.x, point.y, data=point.data))

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

        bboxes.append({"bbox": self.bbox, "color": self.color, "parent": self.parent})

        if not self.northWest == None:
            # ... search each child node in turn, merging with any existing results
            bboxes = bboxes + self.northWest.getBBoxes()
            bboxes = bboxes + self.northEast.getBBoxes()
            bboxes = bboxes + self.southWest.getBBoxes()
            bboxes = bboxes + self.southEast.getBBoxes()

        return bboxes


if __name__ == "__main__":
    pass
