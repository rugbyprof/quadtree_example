import pygame
from rich import print
from point import Point
from ball import Ball
import random
from rectangle import Rectangle
from rectangle import Bounds
from pointQuadTree import PointQuadTree
import sys

# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

BUFFER = 20

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

TREE_WIDTH = SCREEN_WIDTH - BUFFER
TREE_HEIGHT = SCREEN_HEIGHT - BUFFER


class TreeDriver(object):
    """This would normally be a game class. But, we need a tree handler so
    I'm repurposing a game class I found here:
    http://programarcadegames.com/python_examples/f.php?file=game_class_example.py
    """

    def __init__(self, **kwargs):
        """Init driver class"""

        self.screen = kwargs.get("screen", None)  # screen
        if not self.screen:
            print("Need a pygame screen!")
            sys.exit()
        self.width = kwargs.get("width", TREE_WIDTH)  # tree bbox width
        self.height = kwargs.get("height", TREE_HEIGHT)  # tree bbox height
        self.primePoints = kwargs.get("primePoints", 0)  # prime tree with N points
        self.loadPoints = kwargs.get("loadPoints", [])  # load a list of points
        self.ballColor = kwargs.get("ballColor", (0, 255, 0))  # generic ball color

        self.bbox = Rectangle(p1=Point(0, 0), p2=Point(self.width, self.height))
        self.tree = PointQuadTree(self.bbox, 1, 0)
        self.pid = 0
        self.balls = []
        self.rects = []
        self.c = 0

        # if list or number of points passed in, call init function
        if len(self.loadPoints) > 0:
            self.initPoints(self.loadPoints)
        elif self.primePoints > 0:
            self.initPoints(self.primePoints)

    def initPoints(self, points):
        """Load quadtree with any pre-existing points"""

        # if points == int then we load "points" number of balls into the tree
        if isinstance(points, int):
            while self.pid < points:
                x = int(self.width * random.random())
                y = int(self.height * random.random())
                p = Ball(
                    x, y, data={"id": self.pid}, color=self.color, radius=3, dx=3, dy=3
                )
                self.tree.insert(p)
                self.balls.append(p)
                self.pid += 1
        # else if points is a "list" of points or balls, we handle that as well
        elif isinstance(points, list):
            for p in points:
                if isinstance(p, Ball):
                    p.data["id"] = self.pid
                    self.tree.insert(p)
                    self.balls.append(p)
                elif isinstance(p, Point):
                    p.data["id"] = self.pid
                    p = Ball(p.x, p.y, data=p.data)
                self.tree.insert(p)
                self.balls.append(p)
                self.pid += 1
        self.rects = self.tree.getBBoxes()

    def captureEvents(self):
        """Handles events like mouse clicks and closing game window.
        Returns:
            dictionary :  a dictionary with keys indicating events that happened
        Examples:
            returns a mouse click event
            {
                "mouseUp" : (345,23)
            }
            returns a keyboard or kill window event
            {
                "quit" : True
            }
        """
        eventHandler = {}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                eventHandler["quit"] = True

            if event.type == pygame.MOUSEBUTTONUP:
                eventHandler["mouseUp"] = True
                eventHandler["data"] = pygame.mouse.get_pos()

            if event.type == pygame.KEYDOWN:
                eventHandler["keydown"] = event.key

        return eventHandler

    def updateLogic(self, events):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        Params:
            events (dict) : event dictionary created in handleEvents
        """
        if "mouseUp" in events:
            x, y = events["data"]
            self.balls.append(Ball(x, y, radius=5, color=(128, 0, 128)))
        # print(events)
        # Move all the balls or sprites

        # check for collision

        # handle collisions or stuff

    def displayFrame(self):
        """Display everything to the screen for the game.
        Params:
            screen (pygame window) : draw stuff to this object
        """
        self.screen.fill(WHITE)
        # points = self.tree.points

        self.tree.reset(self.balls)

        self.drawBalls()
        self.drawRects()

        pygame.display.flip()

    def gameOver(self):
        """Do stuff like below if your game is over
        Params:
            screen (pygame window) : draw stuff to this object
        """
        # font = pygame.font.Font("Serif", 25)
        font = pygame.font.SysFont("serif", 25)
        text = font.render("Game Over, click to restart", True, BLACK)
        center_x = (TREE_WIDTH // 2) - (text.get_width() // 2)
        center_y = (TREE_HEIGHT // 2) - (text.get_height() // 2)
        self.screen.blit(text, [center_x, center_y])

    def drawBalls(self):
        for ball in self.balls:
            print(self.screen, ball.color, [ball.x, ball.y], ball.radius)
            pygame.draw.circle(self.screen, ball.color, [ball.x, ball.y], ball.radius)

    def drawRects(self):
        """left, top, width, height"""
        for rect in self.rects:
            c = rect["color"]
            r = rect["bbox"]
            p = rect["parent"]
            l = r.left + BUFFER // 2
            t = r.top + BUFFER // 2
            w = r.w
            h = r.h

            print(self.c)
            self.c += 1
            pygame.draw.rect(self.screen, c, pygame.Rect(l, t, w, h), 1)


def initSomeBalls(bounds=Bounds(0, 0, TREE_WIDTH, TREE_HEIGHT), n=10):
    """Randomly generate some balls to load into the quadtree"""
    balls = []
    for i in range(n):
        x = random.randint(bounds.minX, bounds.maxX)
        y = random.randint(bounds.minY, bounds.maxY)
        balls.append(Ball(x, y, radius=5, color=(128, 0, 128)))

    return balls


def main():
    """Main program function that does most things pygame"""

    # Initialize Pygame and set up the window
    pygame.init()

    # basic window setup with size and a bounds class
    # for the bouncy balls
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    bounds = Bounds(0, 0, TREE_WIDTH, TREE_HEIGHT)
    screen = pygame.display.set_mode(size)

    # title the game window, and make the mouse show up
    pygame.display.set_caption("Quadtree Demo")
    pygame.mouse.set_visible(True)

    # Game loop boolean and instance of the pygame clock
    keepLooping = True
    clock = pygame.time.Clock()

    #####################################################################
    # Create an instance of the Game class that drives
    # this whole mess.
    driver = TreeDriver(screen=screen, loadPoints=initSomeBalls(bounds, 1))

    #####################################################################
    # Main game loop
    while keepLooping:

        # Process events (keystrokes, mouse clicks, etc)
        events = driver.captureEvents()

        # some quit event happened so break out
        if "quit" in events:
            break

        # Update object positions, check for collisions
        driver.updateLogic(events)

        # Draw the current frame
        driver.displayFrame()

        # Pause for the next frame
        clock.tick(60)

    # Close window and exit
    pygame.quit()


# Call the main function, start up the game
if __name__ == "__main__":
    main()
