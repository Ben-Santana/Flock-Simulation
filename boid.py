from cmath import cos, sin
import math
import numpy
import pygame
import random
from vector import Vector, random_vector
import vector

pygame.init()


class Agent:
    def __init__(
        self,
        position: Vector,
        newPos: Vector,
        angle: float,
        sight: float,
        minDist: float,
        predator: bool,
        dx: float,
        dy: float,
        size: float,
        color: float
    ):
        self.position = position
        self.angle = angle
        self.sight = sight
        self.minDist = minDist
        self.newPos = newPos
        self.predator = predator
        self.dx = dx
        self.dy = dy
        self.size = size
        self.randomColor = color


delta_time = 0.0
clock = pygame.time.Clock()

# changeable variables ( for customization )
numOfAgents = 50
numOfPredators = 1
screenSizeX = 700
screenSizeY = 600
maxSpeed = 4
predatorMaxSpeed = 3
predatorFollowMouse = False


ArrayAgents = numpy.empty(numOfAgents, dtype=Agent)


agentStartingAngle = random.random() * 180  # redundant

direction = Vector(0, 0)

pygame.mouse.set_visible(False)


# make agents

for n in range(numOfAgents):

    ArrayAgents[n] = Agent(
        Vector(
            random.random() * screenSizeX, random.random() * screenSizeY),
        Vector(0, 0),
        agentStartingAngle,
        100,
        20.0,  # TEMP
        False,
        random.random(),
        random.random(),
        10,
        random.random() * 100
    )


def setPredators():
    totalPredators = 0
    for n in ArrayAgents:
        if (numOfPredators > 0):
            n.predator = True
            n.sight = n.sight*3
            totalPredators += 1
            if (totalPredators == numOfPredators):
                break


setPredators()

screen = pygame.display.set_mode((screenSizeX, screenSizeY))

trailFollow = Vector(0, 0)

simRunning = True
agentStart = True

# else:
#    agentX.position = Vector(
#        random.random() * screenSizeX, random.random() * screenSizeY)


# ---------------------------------------------------------------------------------------------------
# Boid Functions ------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def distance(boid1: Agent, boid2: Agent):
    return math.sqrt((boid1.position.x - boid2.position.x) ** 2 + (boid1.position.y - boid2.position.y)**2)


def flyTowardsCenter(boid):
    centeringFactor = 0.005

    centerX = 0
    centerY = 0
    numNeighbors = 0

    for otherBoid in ArrayAgents:
        if (distance(boid, otherBoid) < boid.sight):
            centerX += otherBoid.position.x
            centerY += otherBoid.position.y
            numNeighbors += 1

    if (numNeighbors):
        centerX = centerX / numNeighbors
        centerY = centerY / numNeighbors

        boid.dx += (centerX - boid.x) * centeringFactor
        boid.dy += (centerY - boid.y) * centeringFactor


def matchVelocity(boid):
    matchingFactor = 0.05  # Adjust by this % of average velocity

    avgDX = 0
    avgDY = 0
    numNeighbors = 0

    for otherBoid in ArrayAgents:
        if distance(boid, otherBoid) < boid.sight:
            avgDX += otherBoid.dx
            avgDY += otherBoid.dy
            numNeighbors += 1

    if (numNeighbors):
        avgDX = avgDX / numNeighbors
        avgDY = avgDY / numNeighbors

        boid.dx += (avgDX - boid.dx) * matchingFactor
        boid.dy += (avgDY - boid.dy) * matchingFactor


def limitSpeed(boid):
    if not boid.predator:
        speedLimit = maxSpeed
    else:
        speedLimit = predatorMaxSpeed

    speed = math.sqrt(boid.dx * boid.dx + boid.dy * boid.dy)

    if (speed > speedLimit):
        boid.dx = (boid.dx / speed) * speedLimit
        boid.dy = (boid.dy / speed) * speedLimit


def flyTowardsCenter(boid):
    centeringFactor = 0.001

    centerX = 0
    centerY = 0
    numNeighbors = 0

    for otherBoid in ArrayAgents:
        if (distance(boid, otherBoid) < boid.sight and not otherBoid.predator):
            centerX += otherBoid.position.x
            centerY += otherBoid.position.y
            numNeighbors += 1

    if (numNeighbors):
        centerX = centerX / numNeighbors
        centerY = centerY / numNeighbors

        boid.dx += (centerX - boid.position.x) * centeringFactor
        boid.dy += (centerY - boid.position.y) * centeringFactor


def avoidPredator(boid):
    avoidFactor = 0.003
    moveX = 0
    moveY = 0
    for k in ArrayAgents:
        distance = math.sqrt((boid.position.x - k.position.x)
                             ** 2 + (boid.position.y - k.position.y)**2)
        if k.predator and k != boid:
            if distance < boid.sight:
                moveX += boid.position.x - k.position.x
                moveY += boid.position.y - k.position.y

    boid.dx += moveX * avoidFactor
    boid.dy += moveY * avoidFactor


def avoidEdge(boid):
    avoidFactor = 0.0027
    moveX = 0
    moveY = 0
    marginSight = boid.sight

    if boid.position.x < marginSight:
        moveX += boid.position.x
    if boid.position.x > screenSizeX - marginSight:
        moveX += boid.position.x - screenSizeX
    if boid.position.y < marginSight:
        moveY += boid.position.y
    if boid.position.y > screenSizeY - marginSight:
        moveY += boid.position.y - screenSizeY

    boid.dx += moveX * avoidFactor
    boid.dy += moveY * avoidFactor


def chaseAgents(boid):
    # chaseFactor = 0.001
    # moveX = 0
    # moveY = 0
    # numberOfPrey = 0
    # for k in ArrayAgents:
    #     distance = math.sqrt((boid.position.x - k.position.x)
    #                          ** 2 + (boid.position.y - k.position.y)**2)
    #     if not k.predator:
    #         if distance < boid.sight:
    #             moveX -= boid.position.x - k.position.x
    #             moveY -= boid.position.y - k.position.y
    #             numberOfPrey += 1
    # if (numberOfPrey):
    #     boid.dx += (moveX * chaseFactor) / numberOfPrey
    #     boid.dy += (moveY * chaseFactor) / numberOfPrey

    chaseFactor = 0.004

    centerX = 0
    centerY = 0
    numPrey = 0

    for otherBoid in ArrayAgents:
        if (distance(boid, otherBoid) < boid.sight and not otherBoid.predator):
            centerX += otherBoid.position.x
            centerY += otherBoid.position.y
            numPrey += 1

    if (numPrey):
        centerX = centerX / numPrey
        centerY = centerY / numPrey

        boid.dx += (centerX - boid.position.x) * chaseFactor
        boid.dy += (centerY - boid.position.y) * chaseFactor


def moveAgent(n: Agent):
    if agentStart:

        direction = Vector(n.dx, n.dy)


# checks for out of bounds

        if (n.position + direction).x >= screenSizeX or (
            n.position + direction
        ).x <= 0:
            n.newPos = Vector(
                screenSizeX - n.position.x, n.position.y)

        elif (n.position + direction).y >= screenSizeY or (
            n.position + direction
        ).y <= 0:
            n.newPos = Vector(
                n.position.x, screenSizeY - n.position.y)

# if not out og bounds, set newPosition
        else:
            n.newPos = n.position + direction

        n.position = n.newPos

        if n.predator and predatorFollowMouse:
            mousePos = pygame.mouse.get_pos()
            n.position.x = mousePos[0]
            n.position.y = mousePos[1]


def AvoidBoids(n: Agent):
    # nested for loop to compare each boid to one another and check if they are too close
    avoidFactor = 0.01
    moveX = 0
    moveY = 0
    for k in ArrayAgents:
        distance = math.sqrt((n.position.x - k.position.x)
                             ** 2 + (n.position.y - k.position.y)**2)
        if n != k:
            if distance < n.minDist:
                moveX += n.position.x - k.position.x
                moveY += n.position.y - k.position.y

    n.dx += moveX * avoidFactor
    n.dy += moveY * avoidFactor


def update():
    for n in ArrayAgents:
        if not n.predator:
            flyTowardsCenter(n)
            AvoidBoids(n)
            matchVelocity(n)
            avoidPredator(n)
            limitSpeed(n)
            avoidEdge(n)
            moveAgent(n)
        if n.predator:
            flyTowardsCenter(n)
            AvoidBoids(n)
            matchVelocity(n)
            limitSpeed(n)
            moveAgent(n)
            chaseAgents(n)

    pass


def draw():
    screen.fill((0, 0, 0))
    for n in ArrayAgents:
        if not n.predator:
            pygame.draw.rect(
                screen,
                (75 + n.randomColor, 75 + n.randomColor, 155 + n.randomColor),
                pygame.Rect(n.position.x, n.position.y, n.size, n.size),)
        if n.predator:
            pygame.draw.rect(
                screen,
                (155 + n.randomColor, n.randomColor, n.randomColor),
                pygame.Rect(n.position.x, n.position.y, n.size, n.size),)


while simRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                simRunning = False

    update()
    draw()

    pygame.display.flip()

    delta_time = 0.001 * clock.tick(144)


pygame.quit()
# quit()
